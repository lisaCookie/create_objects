# RECIPES/users/db_init.py
import os
import sqlite3
from sqlite3 import Row

DB_PATH = os.path.join(os.path.dirname(__file__), 'recipes.db')

def get_db_connection():
    """Создаёт и возвращает подключение к базе данных с поддержкой именованных столбцов."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_users_table():
    """Создаёт все таблицы и админа 'superadmin', если не существует."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        with conn:
            # Таблицы: users, categories, objects, ingredients, comments, settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0
                )
            """)

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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (object_id) REFERENCES objects (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    auth_code TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO settings (id, auth_code) VALUES (1, NULL)")

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
