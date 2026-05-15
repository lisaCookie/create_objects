# RECIPES/admin/services/comment_service.py
from RECIPES.database.db_init import get_db_connection

def delete_comment(comment_id):
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    return True
