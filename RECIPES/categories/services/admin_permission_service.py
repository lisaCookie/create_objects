# RECIPES/categories/services/admin_permission_service.py

from RECIPES.database.db_init import get_db_connection

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором"""
    conn = get_db_connection()
    admin_status = conn.execute(
        "SELECT is_admin FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if admin_status and admin_status['is_admin']:
        return True
    return False

def has_admin_access(user_id):
    """Проверяет права администратора для редактирования/удаления чужих объектов"""
    return is_admin(user_id)
