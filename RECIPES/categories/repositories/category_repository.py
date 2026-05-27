# RECIPES/categories/repositories/category_repository.py

from RECIPES.database.db_init import get_db_connection

class CategoryRepository:
    @staticmethod
    def get_by_id(category_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username
                    FROM categories c
                    LEFT JOIN users u ON c.created_by = u.id
                    WHERE c.id = %s
                """, (category_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(name, created_by, parent_id=None):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO categories (name, created_by, parent_id)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (name.strip(), created_by, parent_id))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            raise e
        finally:
            conn.close()

    @staticmethod
    def check_parent_exists(parent_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM categories
                    WHERE id = %s
                """, (parent_id,))
                return cursor.fetchone() is not None
        finally:
            conn.close()



    @staticmethod
    def check_subcategory_exists(name, parent_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM categories
                    WHERE name = %s AND parent_id = %s
                """, (name.strip(), parent_id))
                return cursor.fetchone() is not None
        finally:
            conn.close()


    @staticmethod
    def get_all_with_hierarchy():
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
                    FROM categories c JOIN users u ON c.created_by = u.id
                    ORDER BY c.parent_id, c.name
                """)
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_parent(parent_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
                    FROM categories c JOIN users u ON c.created_by = u.id
                    WHERE c.parent_id = %s
                    ORDER BY c.name
                """, (parent_id,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_owner_check(category_id, user_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.id, c.name, c.created_by, u.username AS created_by_username
                    FROM categories c LEFT JOIN users u ON c.created_by = u.id
                    WHERE c.id = %s
                """, (category_id,))
                category = cursor.fetchone()

                if not category:
                    return None

                category = dict(category)
                cursor.execute(
                    "SELECT is_admin FROM users WHERE id = %s", (user_id,)
                )
                is_admin_row = cursor.fetchone()
                is_admin = is_admin_row and is_admin_row['is_admin']
                is_owner = (category['created_by'] == user_id)
                can_edit = is_owner or (is_admin and is_admin)

                return {
                    'category': category,
                    'can_edit': can_edit
                }
        finally:
            conn.close()

    @staticmethod
    def update(name, category_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE categories
                    SET name = %s
                    WHERE id = %s
                """, (name.strip(), category_id))
        finally:
            conn.close()

    @staticmethod
    def delete(category_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM categories WHERE id = %s
                """, (category_id,))
        except Exception as e:
            raise ValueError(f"Ошибка при удалении: {e}")
        finally:
            conn.close()
