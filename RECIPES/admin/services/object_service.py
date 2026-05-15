# RECIPES/admin/services/object_service.py
from RECIPES.database.db_init import get_db_connection

def delete_object(object_id):
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))
        conn.execute("DELETE FROM comments WHERE object_id = ?", (object_id,))
        conn.execute("DELETE FROM objects WHERE id = ?", (object_id,))
    return True
