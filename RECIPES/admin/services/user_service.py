# RECIPES/admin/services/user_service.py
from RECIPES.database.db_init import get_db_connection

def delete_user(user_id, current_user_id):
    if user_id == current_user_id:
        raise ValueError("Нельзя удалить самого себя")

    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        # Удаляем все связанные данные
        cursor.execute("DELETE FROM objects WHERE created_by = %s", (user_id,))
        cursor.execute("DELETE FROM comments WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM categories WHERE created_by = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

    return True
