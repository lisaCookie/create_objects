# RECIPES/categories/repositories/sitemap_repository.py

from RECIPES.database.db_init import get_db_connection

class SitemapRepository:
    @staticmethod
    def get_root_categories():
        with get_db_connection() as conn:
            rows = conn.execute("""
                SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
                FROM categories c LEFT JOIN users u ON c.created_by = u.id
                WHERE c.parent_id IS NULL ORDER BY c.name
            """).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_children_and_objects(category_id, user_id=None):
        with get_db_connection() as conn:
            children = conn.execute("""
                SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
                FROM categories c LEFT JOIN users u ON c.created_by = u.id
                WHERE c.parent_id = ? ORDER BY c.name
            """, (category_id,)).fetchall()

            query_objects = """
                SELECT o.id, o.name, o.visible_to_guests
                FROM objects o WHERE o.category_id = ?
            """
            params = [category_id]

            if user_id is None:
                query_objects += " AND o.visible_to_guests = 1"

            objects = conn.execute(query_objects, params).fetchall()

            return [dict(row) for row in children], [dict(row) for row in objects]
