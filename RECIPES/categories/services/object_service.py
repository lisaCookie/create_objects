# RECIPES/categories/services/object_service.py
from RECIPES.database.db_init import get_db_connection
import sqlite3


def get_objects_by_category_id(category_id, user_id=None):
    """ Возвращает объекты для указанной категории.
        Если user_id не предоставлен (т.е. гость), возвращает только объекты, видимые гостям.
    """
    conn = get_db_connection()
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
                o.created_at, 
                o.visible_to_guests
            FROM objects o 
            JOIN users u ON o.created_by = u.id 
            WHERE o.category_id = ?
        """
        params = [category_id]

        # Если пользователь не авторизован — фильтруем по visible_to_guests
        if user_id is None:
            query += " AND o.visible_to_guests = 1"

        query += " ORDER BY o.created_at DESC"
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    
def create_obj(name, description, category_id, created_by, technology):
    conn = get_db_connection()
    with conn:
        try:
            result = conn.execute("""
                INSERT INTO objects (name, description, category_id, created_by, technology)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, category_id, created_by, technology))
            return result.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("Имя уже занято.")
        
def insert_object(name, description, category_id, user_id, technology=None):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO objects (name, description, technology, category_id, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, technology, category_id, user_id))
        return cursor.lastrowid

def get_object_by_id(object_id, user_id=None):
    conn = get_db_connection()
    with conn:
        obj = conn.execute("""
            SELECT o.id, o.name, o.description, o.technology, o.created_at,
            c.name AS category_name, o.visible_to_guests, o.category_id
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            WHERE o.id = ?
        """, (object_id,)).fetchone()

        if not obj:
            return None

        obj = dict(obj)

    # Проверка видимости для гостей
        if obj['visible_to_guests'] == 0 and not user_id:
            return None

        return obj