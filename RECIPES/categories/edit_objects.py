# RECIPES/categories/edit_objects.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from RECIPES.users.work_db_users import get_db_connection

edit_objects_bp = Blueprint('edit_objects', __name__)


def can_edit(user_id, owner_id, conn):
    """
    Проверяет, может ли пользователь редактировать объект, принадлежащий owner_id.
    Возвращает True, если:
    - пользователь — автор объекта, ИЛИ
    - пользователь — администратор.
    """
    if user_id == owner_id:
        return True
    admin_status = conn.execute(
        "SELECT is_admin FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    return admin_status and admin_status['is_admin']


@edit_objects_bp.route('/object/<int:object_id>/edit', methods=['GET', 'POST'])
def edit_object(object_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        obj = conn.execute("""
            SELECT o.id, o.name, o.description, o.category_id, o.created_by
            FROM objects o
            WHERE o.id = ?
        """, (object_id,)).fetchone()

        if not obj:
            flash("Объект не найден.")
            return redirect(url_for('index'))

        # ✅ Используем универсальную функцию проверки
        if not can_edit(session['user_id'], obj['created_by'], conn):
            flash("Вы не можете редактировать чужой объект.")
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))

        ingredients = conn.execute("""
            SELECT name, amount, unit FROM ingredients WHERE object_id = ?
        """, (object_id,)).fetchall()

        if request.method == 'POST':
            name = request.form.get('object_name', '').strip()
            description = request.form.get('object_description', '').strip()

            if not name:
                flash('Название объекта не может быть пустым.')
                return redirect(url_for('edit_objects.edit_object', object_id=object_id))

            # ✅ Обновляем основные поля объекта
            conn.execute("""
                UPDATE objects SET name = ?, description = ? WHERE id = ?
            """, (name, description, object_id))

            # ✅ Удаляем старые ингредиенты
            conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))

            # ✅ Добавляем новые ингредиенты
            ingredient_names = request.form.getlist('ingredient_name[]')
            ingredient_amounts = request.form.getlist('ingredient_amount[]')
            ingredient_units = request.form.getlist('ingredient_unit[]')

            for i in range(len(ingredient_names)):
                name = ingredient_names[i].strip()
                amount = ingredient_amounts[i].strip()
                unit = ingredient_units[i].strip()
                if name:  # Не добавляем пустые
                    conn.execute("""
                        INSERT INTO ingredients (object_id, name, amount, unit)
                        VALUES (?, ?, ?, ?)
                    """, (object_id, name, amount, unit))

            flash('Объект успешно обновлён!')
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))

        # ✅ Передаём ингредиенты в шаблон
        return render_template('categorypage.html', 
                              category=obj, 
                              object_to_edit=obj, 
                              ingredients=ingredients,
                              editing=True)  # ✅ Флаг редактирования


@edit_objects_bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования комментария.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        comment = conn.execute("""
            SELECT c.id, c.text, c.object_id, c.user_id, o.category_id
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            WHERE c.id = ?
        """, (comment_id,)).fetchone()

        if not comment:
            flash("Комментарий не найден.")
            return redirect(url_for('index'))

        # ✅ Используем универсальную функцию проверки
        if not can_edit(session['user_id'], comment['user_id'], conn):
            flash("Вы не можете редактировать чужой комментарий.")
            return redirect(url_for('objects.category_page', category_id=comment['category_id']))

        if request.method == 'POST':
            text = request.form.get('comment_text', '').strip()

            if not text:
                flash('Комментарий не может быть пустым.')
                return redirect(url_for('objects.edit_comment', comment_id=comment_id))

            conn.execute("""
                UPDATE comments
                SET text = ?
                WHERE id = ?
            """, (text, comment_id))

            flash('Комментарий успешно обновлён!')
            return redirect(url_for('objects.category_page', category_id=comment['category_id']))

        return render_template('edit_comment.html', comment=comment)


@edit_objects_bp.route('/category/<int:category_id>/edit', methods=['POST'])
def edit_category(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        category = conn.execute("""
            SELECT id, created_by
            FROM categories
            WHERE id = ?
        """, (category_id,)).fetchone()

        if not category:
            flash("Категория не найдена.")
            return redirect(url_for('index'))

        # ✅ Используем универсальную функцию проверки
        if not can_edit(session['user_id'], category['created_by'], conn):
            flash("Вы не можете редактировать эту категорию.")
            return redirect(url_for('objects.category_page', category_id=category_id))

        name = request.form.get('category_name', '').strip()
        if not name:
            flash('Название категории не может быть пустым.')
            return redirect(url_for('objects.category_page', category_id=category_id))

        conn.execute("""
            UPDATE categories
            SET name = ?
            WHERE id = ?
        """, (name, category_id))

        flash('Название категории успешно изменено!')
        return redirect(url_for('objects.category_page', category_id=category_id))
