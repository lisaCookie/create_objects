# RECIPES/admin/services/object_service.py
from RECIPES.database.db_init import get_db_connection

def delete_object(object_id):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ingredients WHERE object_id = %s", (object_id,))
        cursor.execute("DELETE FROM comments WHERE object_id = %s", (object_id,))
        cursor.execute("DELETE FROM objects WHERE id = %s", (object_id,))
    return True
