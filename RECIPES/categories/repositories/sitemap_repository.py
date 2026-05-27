# RECIPES/categories/repositories/sitemap_repository.py

from RECIPES.database.db_init import get_db_connection

class SitemapRepository:
    @staticmethod
    def get_root_categories():
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
                    FROM categories c LEFT JOIN users u ON c.created_by = u.id
                    WHERE c.parent_id IS NULL ORDER BY c.name
                """)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_children_and_objects(category_id, user_id=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                # Получаем дочерние категории
                cursor.execute("""
                    SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
                    FROM categories c LEFT JOIN users u ON c.created_by = u.id
                    WHERE c.parent_id = %s ORDER BY c.name
                """, (category_id,))
                children = [dict(row) for row in cursor.fetchall()]

                # Получаем объекты
                query_objects = """
                    SELECT o.id, o.name, o.visible_to_guests
                    FROM objects o WHERE o.category_id = %s
                """
                params = [category_id]

                if user_id is None:
                    query_objects += " AND o.visible_to_guests = 1"

                cursor.execute(query_objects, params)
                objects = [dict(row) for row in cursor.fetchall()]

                return children, objects
        finally:
            conn.close()