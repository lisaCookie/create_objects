# RECIPES/users/work_db_users.py

import os
import sqlite3
from sqlite3 import Row

# Путь к базе данных SQLite (исправлено: не 'urls.db', а 'recipes.db' — логично для рецептов!)
DB_PATH = os.path.join(os.path.dirname(__file__), 'recipes.db')


def get_db_connection():
    """Создаёт и возвращает подключение к базе данных с поддержкой именованных столбцов."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = Row
    conn.execute("PRAGMA foreign_keys = ON")
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

            # Таблица категорий (с глобальной уникальностью имён)
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
                    technology TEXT,
                    category_id INTEGER NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    visible_to_guests INTEGER DEFAULT 1,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(name)
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
                    FOREIGN KEY (object_id) REFERENCES objects (id) ON DELETE CASCADE
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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1), -- только одна строка
                auth_code TEXT,  -- кодовое слово для пользователей (не админов)
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO settings (id, auth_code) VALUES (1, NULL)")

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
    """Создаёт категорию (корневую или подкатегорию). Возвращает ID или None при ошибке."""
    if not name or not name.strip():
        raise ValueError("Имя категории не может быть пустым")

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, parent_id, created_by) VALUES (?, ?, ?)",
                (name.strip(), parent_id, user_id)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Категория с именем '{name}' уже существует")
    except sqlite3.Error as e:
        raise RuntimeError(f"Ошибка базы данных при создании категории: {e}")


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
            SELECT o.id, o.name, o.description, o.technology, o.created_by, u.username AS created_by_username, o.created_at, o.visible_to_guests
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

def insert_object(name, description, category_id, user_id, technology=None):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO objects (name, description, technology, category_id, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, technology, category_id, user_id))
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

# --- Функции для работы с кодовым словом ---
def get_auth_code():
    """Возвращает текущее кодовое слово из settings (или None, если не задано)"""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT auth_code FROM settings WHERE id = 1")
        row = cursor.fetchone()
        return row[0] if row else None

def update_settings_auth_code(new_code):
    """Обновляет кодовое слово в settings. Может быть пустым (None)."""
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET auth_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (new_code,))
        return cursor.rowcount > 0
