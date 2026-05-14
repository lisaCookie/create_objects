# RECIPES/users/work_db_users.py

import os
import sqlite3
from sqlite3 import Row

# Путь к базе данных SQLite (исправлено: не 'urls.db', а 'recipes.db' — логично для рецептов!)
DB_PATH = os.path.join(os.path.dirname(__file__), 'recipes.db')


def get_db_connection():
    """Создаёт и возвращает подключение к базе данных с поддержкой именованных столбцов."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = Row  # Позволяет обращаться к столбцам по именам, например: row['username']
    return conn


def init_users_table():
    """
    Создаёт все необходимые таблицы для приложения рецептов:
    users, categories, objects, ingredients, comments.
    
    Также создаёт администратора 'superadmin', если он ещё не существует.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with conn:
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            """)

            # Таблица категорий
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER,  
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users (id),
                    UNIQUE(name, parent_id)
                )
            """)

            # Таблица объектов (рецептов)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visible_to_guests INTEGER DEFAULT 1,
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """)

            # Таблица ингредиентов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    FOREIGN KEY (object_id) REFERENCES objects (id)
                )
            """)

            # Таблица комментариев
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (object_id) REFERENCES objects (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            # Проверка и создание администратора 'superadmin'
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("superadmin",))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                    ("superadmin", "ujkjuhfabz", 1)
                )
                print("✅ Админ-пользователь 'superadmin' создан с паролем 'ujkjuhfabz'")

    except sqlite3.Error as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
    finally:
        conn.close()
# --- Функции для работы с категориями ---

def insert_category(name, user_id, parent_id=None):
    """Создаёт категорию (корневую или подкатегорию)."""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, parent_id, created_by) VALUES (?, ?, ?)",
            (name, parent_id, user_id)
        )
        return cursor.lastrowid

def get_all_categories_with_hierarchy():
    """Возвращает все категории с иерархией: родитель → подкатегории."""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
            FROM categories c
            JOIN users u ON c.created_by = u.id
            ORDER BY c.parent_id, c.name
        """)
        rows = cursor.fetchall()
        categories = [dict(row) for row in rows]
        
        # Группируем по parent_id
        hierarchy = {}
        for cat in categories:
            parent_id = cat['parent_id']
            if parent_id not in hierarchy:
                hierarchy[parent_id] = []
            hierarchy[parent_id].append(cat)
        
        # Формируем дерево
        def build_tree(parent_id=None, level=0):
            children = hierarchy.get(parent_id, [])
            result = []
            for child in children:
                child['level'] = level
                child['children'] = build_tree(child['id'], level + 1)
                result.append(child)
            return result
        
        return build_tree()

def get_categories_by_parent(parent_id=None):
    """Возвращает все категории с заданным parent_id (для отображения в одной ветке)."""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
            FROM categories c
            JOIN users u ON c.created_by = u.id
            WHERE c.parent_id = ?
            ORDER BY c.name
        """, (parent_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_category_by_id(category_id):
    """Получает категорию по ID."""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
            FROM categories c
            JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

# --- Функции для работы с объектами (рецептами) ---

def get_objects_by_category_id(category_id, user_id=None):
    """
    Возвращает объекты для указанной категории.
    Если user_id не предоставлен (т.е. гость), возвращает только объекты, видимые гостям.
    """
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        query = """
            SELECT o.id, o.name, o.description, o.created_by, u.username AS created_by_username, o.created_at, o.visible_to_guests
            FROM objects o
            JOIN users u ON o.created_by = u.id
            WHERE o.category_id = ?
        """
        params = [category_id]

        # Если пользователь не авторизован (user_id is None),
        # добавляем условие, что объект должен быть видим для гостей.
        if user_id is None:
            query += " AND o.visible_to_guests = 1"
        
        query += " ORDER BY o.created_at DESC"
        
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

def insert_object(name, description, category_id, user_id):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO objects (name, description, category_id, created_by)
            VALUES (?, ?, ?, ?)
        """, (name, description, category_id, user_id))
        return cursor.lastrowid

# --- Функции для работы с ингредиентами ---

def get_ingredients_by_object_id(object_id):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, amount, unit
            FROM ingredients
            WHERE object_id = ?
            ORDER BY name
        """, (object_id,))
        return cursor.fetchall()

def insert_ingredient(object_id, name, amount, unit):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ingredients (object_id, name, amount, unit) 
            VALUES (?, ?, ?, ?)
        """, (object_id, name, amount, unit))

# --- Функции для работы с комментариями ---

def get_comments_by_object_id(object_id):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.text, c.user_id, u.username, c.created_at
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.object_id = ?
            ORDER BY c.created_at DESC
        """, (object_id,))
        return cursor.fetchall()

def insert_comment(object_id, user_id, text):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (object_id, user_id, text)
            VALUES (?, ?, ?)
        """, (object_id, user_id, text))