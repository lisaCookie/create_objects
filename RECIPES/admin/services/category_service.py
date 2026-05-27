# RECIPES/admin/services/category_service.py
from RECIPES.database.db_init import get_db_connection


def delete_category(category_id):
    conn = get_db_connection()
    with conn:
        # Получаем все объекты в категории
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM objects WHERE category_id = %s", (category_id,))
        objects = cursor.fetchall()
        for obj in objects:
            cursor.execute("DELETE FROM ingredients WHERE object_id = %s", (obj['id'],))
            cursor.execute("DELETE FROM comments WHERE object_id = %s", (obj['id'],))
        cursor.execute("DELETE FROM objects WHERE category_id = %s", (category_id,))
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    return True
