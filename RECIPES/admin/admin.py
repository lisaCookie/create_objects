# RECIPES/admin/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from RECIPES.admin.services import (
    dashboard_service,
    user_service,
    category_service,
    object_service,
    comment_service,
    auth_service,
)

admin_bp = Blueprint('admin', __name__, template_folder='../templates', static_folder='../static')

@admin_bp.route('/admin')
def dashboard():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    conn = dashboard_service.get_db_connection()  # или импортируйте get_db_connection напрямую
    try:
        with conn:
            cursor = conn.cursor()  # Создаём курсор
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
            user_session = cursor.fetchone()  # Получаем результат через курсор

            if not user_session or not user_session['is_admin']:
                flash('У вас нет прав администратора.')
                return redirect(url_for('index'))
    except Exception as e:
        flash('Ошибка при проверке прав администратора.', 'danger')
        return redirect(url_for('index'))

    # --- Получаем данные через сервис ---
    filters = {
        'creator_id_filter': request.args.get('creator_id'),
        'category_id_filter': request.args.get('category_id'),
        'object_id_filter': request.args.get('object_id'),
    }

    data = dashboard_service.get_dashboard_data(**filters)

    return render_template('admin/dashboard.html',
        current_auth_code=auth_service.get_current_auth_code(),
        **data
    )

# --- Удаление пользователей ---
@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы.')
        return redirect(url_for('login.login'))

    if not _is_admin():
        flash('У вас нет прав администратора.')
        return redirect(url_for('index'))

    try:
        user_service.delete_user(user_id, session['user_id'])
        flash(f'Пользователь с ID {user_id} удалён (все его данные удалены).')
    except ValueError as e:
        flash(str(e))

    return redirect(url_for('admin.dashboard'))

# --- Удаление категорий ---
@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category_admin(category_id):
    if not _is_admin():
        flash('У вас нет прав администратора.')
        return redirect(url_for('index'))

    category_service.delete_category(category_id)
    flash('Категория и все её объекты удалены админом.')
    return redirect(url_for('admin.dashboard'))

# --- Удаление объектов ---
@admin_bp.route('/object/<int:object_id>/delete', methods=['POST'])
def delete_object_admin(object_id):
    if not _is_admin():
        flash('У вас нет прав администратора.')
        return redirect(url_for('index'))

    object_service.delete_object(object_id)
    flash('Объект удалён админом.')
    return redirect(url_for('admin.dashboard'))

# --- Удаление комментариев ---
@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment_admin(comment_id):
    if not _is_admin():
        flash('У вас нет прав администратора.')
        return redirect(url_for('index'))

    comment_service.delete_comment(comment_id)
    flash('Комментарий удалён админом.')
    return redirect(url_for('admin.dashboard'))

# --- Обновление auth_code ---
@admin_bp.route('/update_auth_code', methods=['POST'])
def update_auth_code():
    if not _is_admin():
        flash('У вас нет прав администратора.')
        return redirect(url_for('index'))

    new_code = request.form.get('auth_code', '').strip() or None
    if auth_service.update_auth_code(new_code):
        flash('Код авторизации обновлён!')
    else:
        flash('Ошибка при обновлении кода.')

    return redirect(url_for('admin.dashboard'))

# --- Вспомогательная функция для проверки админа ---
def _is_admin():
    if 'user_id' not in session:
        return False
    from RECIPES.database.db_init import get_db_connection
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()  # Создаём курсор
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            return user and user['is_admin']
    except Exception as e:
        print(f"Ошибка при проверке прав: {e}")
        return False
