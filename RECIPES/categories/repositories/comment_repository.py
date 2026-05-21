from RECIPES.database.db_init import get_db_connection


class CommentRepository:
    @staticmethod
    def get_by_object_id(object_id):
        conn = get_db_connection()
        with conn:
            comments = conn.execute("""
                SELECT co.id, co.text, co.created_at, co.user_id, u.username
                FROM comments co
                JOIN users u ON co.user_id = u.id
                WHERE co.object_id = ?
                ORDER BY co.created_at DESC
            """, (object_id,)).fetchall()
            return [dict(row) for row in comments]

    @staticmethod
    def get_by_id(comment_id):
        conn = get_db_connection()
        with conn:
            row = conn.execute("""
                SELECT co.id, co.text, co.created_at, co.user_id, co.object_id
                FROM comments co
                WHERE co.id = ?
            """, (comment_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_dependencies(comment_id):
        """Получает информацию для проверки прав доступа (владелец, админ)."""
        conn = get_db_connection()
        with conn:
            return conn.execute("""
                SELECT co.user_id, u.is_admin
                FROM comments co
                JOIN users u ON co.user_id = u.id
                WHERE co.id = ?
            """, (comment_id,)).fetchone()

    @staticmethod
    def create(object_id, user_id, text):
        conn = get_db_connection()
        with conn:
            conn.execute("""
                INSERT INTO comments (object_id, user_id, text)
                VALUES (?, ?, ?)
            """, (object_id, user_id, text))

    @staticmethod
    def update(comment_id, text):
        conn = get_db_connection()
        with conn:
            conn.execute("""
                UPDATE comments SET text = ? WHERE id = ?
            """, (text, comment_id))

    @staticmethod
    def delete(comment_id):
        conn = get_db_connection()
        with conn:
            conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
