# RECIPES/admin/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from RECIPES.users.work_db_users import get_db_connection

admin_bp = Blueprint('admin', __name__, template_folder='../templates', static_folder='../static')

@admin_bp.route('/admin')
def dashboard():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        user_session = conn.execute("SELECT is_admin, username FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not user_session or not user_session['is_admin']:
            flash('У вас нет прав администратора.')
            return redirect(url_for('index'))

        # --- Получаем данные для фильтров ---
        # Все пользователи для фильтра по создателю
        all_users_for_filter = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
        # Все категории для фильтра по категориям
        all_categories_for_filter = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        # Все объекты для фильтра по объектам (для комментариев)
        all_objects_for_filter = conn.execute("""
            SELECT o.id, o.name, c.name AS category_name
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            ORDER BY c.name, o.name
        """).fetchall()

        # --- Получаем параметры фильтрации из запроса ---
        # Для всех сущностей (пользователи, категории, объекты, комментарии)
        creator_id_filter = request.args.get('creator_id') # Фильтр по создателю
        category_id_filter = request.args.get('category_id') # Фильтр по категории
        object_id_filter = request.args.get('object_id') # Фильтр по объекту (в основном для комментариев)

        # --- Формируем SQL-запросы с учетом фильтров ---

        # --- Получаем всех пользователей (для отображения в таблице) ---
        users_sql = """
            SELECT u.id, u.username, u.is_admin, COUNT(DISTINCT o.id) as objects_count, COUNT(DISTINCT c.id) as comments_count
            FROM users u
            LEFT JOIN objects o ON u.id = o.created_by
            LEFT JOIN comments c ON u.id = c.user_id
            WHERE 1=1
        """
        users_params = []
        # Если применен фильтр по создателю, то и пользователей можно отфильтровать
        if creator_id_filter:
            users_sql += " AND u.id = ?"
            users_params.append(creator_id_filter)

        users_sql += " GROUP BY u.id ORDER BY u.username"
        users = conn.execute(users_sql, users_params).fetchall()

        # --- Получаем все категории (для отображения в таблице) ---
        categories_sql = """
            SELECT c.id, c.name, u.username AS created_by, COUNT(DISTINCT o.id) as objects_count
            FROM categories c
            JOIN users u ON c.created_by = u.id
            LEFT JOIN objects o ON c.id = o.category_id
            WHERE 1=1
        """
        categories_params = []
        # Фильтр по создателю категории
        if creator_id_filter:
            categories_sql += " AND c.created_by = ?"
            categories_params.append(creator_id_filter)

        if object_id_filter: # Если выбран конкретный объект, показываем категории, к которым он относится
            categories_sql += " AND c.id IN (SELECT category_id FROM objects WHERE id = ?)"
            categories_params.append(object_id_filter)

        categories_sql += " GROUP BY c.id ORDER BY c.name"
        categories = conn.execute(categories_sql, categories_params).fetchall()

        # --- Получаем все объекты (для отображения в таблице) ---
        objects_sql = """
            SELECT o.id, o.name, c.name AS category_name, u.username AS created_by, o.created_at
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            JOIN users u ON o.created_by = u.id
            WHERE 1=1
        """
        objects_params = []
        # Применяем фильтры к объектам
        if creator_id_filter:
            objects_sql += " AND o.created_by = ?"
            objects_params.append(creator_id_filter)
        if category_id_filter:
            objects_sql += " AND o.category_id = ?"
            objects_params.append(category_id_filter)

        objects_sql += " ORDER BY o.created_at DESC"
        objects = conn.execute(objects_sql, objects_params).fetchall()


        # --- Получаем все комментарии (для отображения в таблице) ---
        comments_sql = """
            SELECT c.id, c.text, o.name AS object_name, u.username AS user_name, c.created_at, c.object_id, c.user_id
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        comments_params = []

        # Применяем фильтры к комментариям
        if object_id_filter: # Фильтруем по конкретному объекту
            comments_sql += " AND c.object_id = ?"
            comments_params.append(object_id_filter)
        if creator_id_filter: # Фильтруем комментарии, созданные определенным пользователем
            comments_sql += " AND c.user_id = ?"
            comments_params.append(creator_id_filter)
        if category_id_filter: # Фильтруем комментарии к объектам определенной категории
            comments_sql += " AND c.object_id IN (SELECT id FROM objects WHERE category_id = ?)"
            comments_params.append(category_id_filter)

        comments_sql += " ORDER BY c.created_at DESC"
        comments = conn.execute(comments_sql, comments_params).fetchall()

        return render_template('admin/dashboard.html',
                               users=users,
                               categories=categories,
                               objects=objects,
                               comments=comments,
                               all_users_for_filter=all_users_for_filter,
                               all_categories_for_filter=all_categories_for_filter,
                               all_objects_for_filter=all_objects_for_filter,
                               # Передаем текущие значения фильтров для их сохранения в выпадающих списках
                               current_creator_id=creator_id_filter,
                               current_category_id=category_id_filter,
                               current_object_id=object_id_filter)

# --- Маршруты удаления с исправленными редиректами ---

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        user_session = conn.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not user_session or not user_session['is_admin']:
            flash('У вас нет прав администратора.')
            return redirect(url_for('index'))

        # Проверка: нельзя удалить самого себя
        if user_id == session['user_id']:
            flash('Нельзя удалить самого себя.')
            # Остаемся на странице админки
            return redirect(url_for('admin.dashboard'))

        # Удаляем все объекты пользователя
        conn.execute("DELETE FROM objects WHERE created_by = ?", (user_id,))
        # Удаляем все комментарии пользователя
        conn.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        # Удаляем его категории
        conn.execute("DELETE FROM categories WHERE created_by = ?", (user_id,))
        # Удаляем самого пользователя
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

        flash(f'Пользователь с ID {user_id} удалён (все его данные удалены).')
        # Исправленный редирект: остаемся в админке
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category_admin(category_id):
    if 'user_id' not in session: # Проверяем авторизацию
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        user_session = conn.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not user_session or not user_session['is_admin']:
            flash('У вас нет прав администратора.')
            return redirect(url_for('index'))

        # Удаляем все объекты в категории
        objects = conn.execute("SELECT id FROM objects WHERE category_id = ?", (category_id,)).fetchall()
        for obj in objects:
            # Удаляем связанные данные (ингредиенты, комментарии)
            conn.execute("DELETE FROM ingredients WHERE object_id = ?", (obj['id'],))
            conn.execute("DELETE FROM comments WHERE object_id = ?", (obj['id'],))
        # Удаляем сами объекты
        conn.execute("DELETE FROM objects WHERE category_id = ?", (category_id,))
        # Удаляем категорию
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        flash('Категория и все её объекты удалены админом.')
        # Исправленный редирект: остаемся в админке
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/object/<int:object_id>/delete', methods=['POST'])
def delete_object_admin(object_id):
    if 'user_id' not in session: # Проверяем авторизацию
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        user_session = conn.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not user_session or not user_session['is_admin']:
            flash('У вас нет прав администратора.')
            return redirect(url_for('index'))

        # Удаляем связанные данные
        conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))
        conn.execute("DELETE FROM comments WHERE object_id = ?", (object_id,))
        # Удаляем сам объект
        conn.execute("DELETE FROM objects WHERE id = ?", (object_id,))
        flash('Объект удалён админом.')
        # Исправленный редирект: остаемся в админке
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment_admin(comment_id):
    if 'user_id' not in session: # Проверяем авторизацию
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        user_session = conn.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not user_session or not user_session['is_admin']:
            flash('У вас нет прав администратора.')
            return redirect(url_for('index'))

        # Удаляем комментарий
        conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        flash('Комментарий удалён админом.')
        # Исправленный редирект: остаемся в админке
        return redirect(url_for('admin.dashboard'))