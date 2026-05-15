from RECIPES.database.db_init import get_db_connection

def get_root_categories():
    with get_db_connection() as conn:
        rows = conn.execute("""
            SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
            FROM categories c LEFT JOIN users u ON c.created_by = u.id
            WHERE c.parent_id IS NULL ORDER BY c.name
        """).fetchall()
        return [dict(row) for row in rows]

def get_children_and_objects(category_id, user_id=None):
    with get_db_connection() as conn:
        children = conn.execute("""
            SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
            FROM categories c LEFT JOIN users u ON c.created_by = u.id
            WHERE c.parent_id = ? ORDER BY c.name
        """, (category_id,)).fetchall()

        if user_id:
            objects = conn.execute("""
                SELECT o.id, o.name, o.visible_to_guests
                FROM objects o WHERE o.category_id = ? ORDER BY o.name
            """, (category_id,)).fetchall()
        else:
            objects = conn.execute("""
                SELECT o.id, o.name, o.visible_to_guests
                FROM objects o WHERE o.category_id = ? AND o.visible_to_guests = 1 ORDER BY o.name
            """, (category_id,)).fetchall()

        return [dict(row) for row in children], [dict(row) for row in objects]
