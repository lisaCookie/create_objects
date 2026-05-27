# RECIPES/categories/repositories/object_repository.py
from RECIPES.database.db_init import get_db_connection

class ObjectRepository:
    @staticmethod
    def get_by_category(category_id, user_id=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                query = """
                    SELECT
                        o.id,
                        o.name,
                        o.description,
                        o.technology,
                        o.created_by,
                        u.username AS created_by_username,
                        TO_CHAR(o.created_at, 'YYYY-MM-DD') AS created_at, 
                        o.visible_to_guests
                    FROM objects o
                    JOIN users u ON o.created_by = u.id
                    WHERE o.category_id = %s
                """
                params = [category_id]

                if user_id is None:
                    query += " AND o.visible_to_guests = 1"

                query += " ORDER BY o.created_at DESC"

                cursor.execute(query, tuple(params))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(object_id, user_id=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT o.id, o.name, o.description, o.technology, 
                        TO_CHAR(o.created_at, 'YYYY-MM-DD') AS created_at, 
                        c.name AS category_name, o.visible_to_guests, o.category_id, o.created_by
                    FROM objects o
                    JOIN categories c ON o.category_id = c.id
                    LEFT JOIN users u ON o.created_by = u.id
                    WHERE o.id = %s
                """, (object_id,))
                obj = cursor.fetchone()

                if not obj:
                    return None

                obj = dict(obj)
                if obj['visible_to_guests'] == 0 and not user_id:
                    return None

                return obj
        finally:
            conn.close()

    @staticmethod
    def create(name, description, category_id, created_by, technology=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO objects (name, description, category_id, created_by, technology)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, description, category_id, created_by, technology))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_by_name(name, exclude_id=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                query = """
                    SELECT id FROM objects
                    WHERE name = %s
                """
                params = (name,)

                if exclude_id is not None:
                    query += " AND id != %s"
                    params = (name, exclude_id)

                cursor.execute(query, params)
                return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def insert(name, description, category_id, user_id, technology=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO objects (name, description, technology, category_id, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (name, description, technology, category_id, user_id))
                result = cursor.fetchone()
                return result[0] if result else None
        finally:
            conn.close()

    @staticmethod
    def get_dependencies(object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT created_by, category_id, u.is_admin
                    FROM objects o
                    JOIN users u ON o.created_by = u.id
                    WHERE o.id = %s
                """, (object_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def delete(object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ingredients WHERE object_id = %s", (object_id,))
                cursor.execute("DELETE FROM comments WHERE object_id = %s", (object_id,))
                cursor.execute("DELETE FROM objects WHERE id = %s", (object_id,))
        finally:
            conn.close()

    @staticmethod
    def update(name, description, technology, object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE objects SET name = %s, description = %s, technology = %s
                    WHERE id = %s
                """, (name, description, technology, object_id))
        finally:
            conn.close()

    @staticmethod
    def add_ingredients(object_id, ingredients):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                for name, amount, unit in ingredients:
                    cursor.execute("""
                        INSERT INTO ingredients (object_id, name, amount, unit)
                        VALUES (%s, %s, %s, %s)
                    """, (object_id, name.strip(), amount.strip(), unit.strip()))
        finally:
            conn.close()

    @staticmethod
    def clear_ingredients(object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ingredients WHERE object_id = %s", (object_id,))
        finally:
            conn.close()

    @staticmethod
    def get_ingredients(object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, amount, unit FROM ingredients WHERE object_id = %s
                """, (object_id,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
