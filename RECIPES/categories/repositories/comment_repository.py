# RECIPES/categories/repositories/comment_repository.py

from RECIPES.database.db_init import get_db_connection


class CommentRepository:
    @staticmethod
    def get_by_object_id(object_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        co.id, co.text,
                        TO_CHAR(co.created_at, 'YYYY-MM-DD') AS created_at,
                        co.user_id, u.username
                    FROM comments co
                    JOIN users u ON co.user_id = u.id
                    WHERE co.object_id = %s
                    ORDER BY co.created_at DESC
                """, (object_id,))
                return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(comment_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        co.id, co.text, 
                        TO_CHAR(co.created_at, 'YYYY-MM-DD') AS created_at,
                        co.user_id, co.object_id
                    FROM comments co
                    WHERE co.id = %s
                """, (comment_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_dependencies(comment_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT co.user_id, u.is_admin
                    FROM comments co
                    JOIN users u ON co.user_id = u.id
                    WHERE co.id = %s
                """, (comment_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def create(object_id, user_id, text):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO comments (object_id, user_id, text)
                    VALUES (%s, %s, %s)
                """, (object_id, user_id, text))
        finally:
            conn.close()

    @staticmethod
    def update(comment_id, text):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE comments SET text = %s WHERE id = %s
                """, (text, comment_id))
        finally:
            conn.close()

    @staticmethod
    def delete(comment_id):
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        finally:
            conn.close()
