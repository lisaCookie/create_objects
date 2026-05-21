from RECIPES.database.db_init import get_db_connection
import sqlite3


class CategoryRepository:
    @staticmethod
    def get_by_id(category_id):
        conn = get_db_connection()
        with conn:
            row = conn.execute("""
                SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username
                FROM categories c
                LEFT JOIN users u ON c.created_by = u.id
                WHERE c.id = ?
            """, (category_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(name, created_by, parent_id=None):
        conn = get_db_connection()
        try:
            with conn:
                result = conn.execute("""
                    INSERT INTO categories (name, created_by, parent_id)
                    VALUES (?, ?, ?)
                """, (name.strip(), created_by, parent_id))
                return result.lastrowid
        except Exception as e:
            raise e

    @staticmethod
    def check_parent_exists(parent_id):
        conn = get_db_connection()
        with conn:
            return conn.execute(
                "SELECT id FROM categories WHERE id = ?", (parent_id,)
            ).fetchone() is not None

    @staticmethod
    def check_subcategory_exists(name, parent_id):
        conn = get_db_connection()
        with conn:
            return conn.execute(
                "SELECT id FROM categories WHERE name = ? AND parent_id = ?",
                (name.strip(), parent_id)
            ).fetchone() is not None

    @staticmethod
    def get_all_with_hierarchy():
        conn = get_db_connection()
        with conn:
            rows = conn.execute("""
                SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
                FROM categories c JOIN users u ON c.created_by = u.id
                ORDER BY c.parent_id, c.name
            """).fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_by_parent(parent_id):
        conn = get_db_connection()
        with conn:
            return [dict(row) for row in conn.execute("""
                SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
                FROM categories c JOIN users u ON c.created_by = u.id
                WHERE c.parent_id = ?
                ORDER BY c.name
            """, (parent_id,)).fetchall()]

    @staticmethod
    def get_owner_check(category_id, user_id):
        conn = get_db_connection()
        with conn:
            category = conn.execute("""
                SELECT c.id, c.name, c.created_by, u.username AS created_by_username
                FROM categories c LEFT JOIN users u ON c.created_by = u.id
                WHERE c.id = ?
            """, (category_id,)).fetchone()

            if not category:
                return None

            category = dict(category)
            is_owner = (category['created_by'] == user_id)
            is_admin_row = conn.execute(
                "SELECT is_admin FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            is_admin = is_admin_row and is_admin_row['is_admin']
            can_edit = is_owner or (is_admin and is_admin)

            return {
                'category': category,
                'can_edit': can_edit
            }

    @staticmethod
    def update(name, category_id):
        conn = get_db_connection()
        with conn:
            conn.execute("""
                UPDATE categories
                SET name = ?
                WHERE id = ?
            """, (name.strip(), category_id))
            
    @staticmethod
    def delete(category_id):
        conn = get_db_connection()
        try:
            # Убедимся, что внешние ключи работают внутри транзакции
            with conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка при удалении: {e}. Возможно, нарушены внешние ключи.")
        except Exception as e:
            raise ValueError(f"Ошибка при удалении категории: {e}")
