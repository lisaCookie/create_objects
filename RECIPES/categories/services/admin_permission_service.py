# RECIPES/categories/services/admin_permission_service.py

from RECIPES.database.db_init import get_db_connection
import psycopg2

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
            admin_status = cursor.fetchone()
            if admin_status and admin_status[0]:
                return True
    except psycopg2.Error as e:
        print(f"Ошибка при проверке прав администратора: {e}")
    return False

def has_admin_access(user_id):
    """Проверяет права администратора для редактирования/удаления чужих объектов"""
    return is_admin(user_id)
