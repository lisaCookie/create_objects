# RECIPES/admin/services/category_service.py
from RECIPES.database.db_init import get_db_connection

def delete_category(category_id):
    conn = get_db_connection()
    with conn:
        # Получаем все объекты в категории
        objects = conn.execute("SELECT id FROM objects WHERE category_id = ?", (category_id,)).fetchall()
        for obj in objects:
            conn.execute("DELETE FROM ingredients WHERE object_id = ?", (obj['id'],))
            conn.execute("DELETE FROM comments WHERE object_id = ?", (obj['id'],))
        conn.execute("DELETE FROM objects WHERE category_id = ?", (category_id,))
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    return True
