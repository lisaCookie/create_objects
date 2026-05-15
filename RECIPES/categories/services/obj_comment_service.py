# RECIPES/categories/services/obj_comment_service.py
from RECIPES.database.db_init import get_db_connection

def get_comments_by_object_id(object_id):
    conn = get_db_connection()
    with conn:
        comments = conn.execute("""
            SELECT co.text, co.created_at, u.username
            FROM comments co
            JOIN users u ON co.user_id = u.id
            WHERE co.object_id = ?
            ORDER BY co.created_at DESC
        """, (object_id,)).fetchall()
        return [dict(row) for row in comments]

def create_comment(object_id, user_id, text):
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT INTO comments (object_id, user_id, text)
            VALUES (?, ?, ?)
        """, (object_id, user_id, text))