# RECIPES/admin/services/user_service.py
from RECIPES.database.db_init import get_db_connection

def delete_user(user_id, current_user_id):
    if user_id == current_user_id:
        raise ValueError("Нельзя удалить самого себя")

    conn = get_db_connection()
    with conn:
        # Удаляем все связанные данные
        conn.execute("DELETE FROM objects WHERE created_by = ?", (user_id,))
        conn.execute("DELETE FROM comments WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM categories WHERE created_by = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    return True
