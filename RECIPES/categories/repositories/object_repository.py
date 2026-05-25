# RECIPES/categories/repositories/object_repository.py
from RECIPES.database.db_init import get_db_connection

class ObjectRepository:
    @staticmethod
    def get_by_category(category_id, user_id=None):
        conn = get_db_connection()
        with conn:
            query = """
                SELECT
                    o.id,
                    o.name,
                    o.description,
                    o.technology,
                    o.created_by,
                    u.username AS created_by_username,
                    o.created_at,
                    o.visible_to_guests
                FROM objects o
                JOIN users u ON o.created_by = u.id
                WHERE o.category_id = ?
            """
            params = [category_id]

            if user_id is None:
                query += " AND o.visible_to_guests = 1"

            query += " ORDER BY o.created_at DESC"

            return conn.execute(query, tuple(params)).fetchall()

    @staticmethod
    def get_by_id(object_id, user_id=None):
        conn = get_db_connection()
        with conn:
            obj = conn.execute("""
                SELECT o.id, o.name, o.description, o.technology, o.created_at,
                c.name AS category_name, o.visible_to_guests, o.category_id, o.created_by
                FROM objects o
                JOIN categories c ON o.category_id = c.id
                LEFT JOIN users u ON o.created_by = u.id
                WHERE o.id = ?
            """, (object_id,)).fetchone()

            if not obj:
                return None

            obj = dict(obj)
            if obj['visible_to_guests'] == 0 and not user_id:
                return None

            return obj

    @staticmethod
    def create(name, description, category_id, created_by, technology=None):
        conn = get_db_connection()
        with conn:
            try:
                result = conn.execute("""
                    INSERT INTO objects (name, description, category_id, created_by, technology)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, description, category_id, created_by, technology))
                return result.lastrowid
            except Exception as e:
                raise e
            
    @staticmethod
    def get_by_name(name, exclude_id=None):
        """Проверяет существование объекта с данным именем (кроме указанного ID)."""
        conn = get_db_connection()
        with conn:
            query = """
                SELECT id FROM objects
                WHERE name = ?
            """
            params = (name,)

            if exclude_id is not None:
                query += " AND id != ?"
                params = (name, exclude_id)

            return conn.execute(query, params).fetchone() is not None


    @staticmethod
    def insert(name, description, category_id, user_id, technology=None):
        conn = get_db_connection()
        with conn:
            result = conn.execute("""
                INSERT INTO objects (name, description, technology, category_id, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, technology, category_id, user_id))
            return result.lastrowid

    @staticmethod
    def get_dependencies(object_id):
        conn = get_db_connection()
        with conn:
            obj = conn.execute("""
                SELECT created_by, category_id, u.is_admin
                FROM objects o
                JOIN users u ON o.created_by = u.id
                WHERE o.id = ?
            """, (object_id,)).fetchone()
            return obj

    @staticmethod
    def delete(object_id):
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))
            conn.execute("DELETE FROM comments WHERE object_id = ?", (object_id,))
            conn.execute("DELETE FROM objects WHERE id = ?", (object_id,))

    @staticmethod
    def update(name, description, technology, object_id):
        conn = get_db_connection()
        with conn:
            conn.execute("""
                UPDATE objects SET name = ?, description = ?, technology = ?
                WHERE id = ?
            """, (name, description, technology, object_id))

    @staticmethod
    def add_ingredients(object_id, ingredients):
        conn = get_db_connection()
        with conn:
            for name, amount, unit in ingredients:
                conn.execute("""
                    INSERT INTO ingredients (object_id, name, amount, unit)
                    VALUES (?, ?, ?, ?)
                """, (object_id, name.strip(), amount.strip(), unit.strip()))

    @staticmethod
    def clear_ingredients(object_id):
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))

    @staticmethod
    def get_ingredients(object_id):
        conn = get_db_connection()
        with conn:
            return conn.execute("""
                SELECT name, amount, unit FROM ingredients WHERE object_id = ?
            """, (object_id,)).fetchall()
