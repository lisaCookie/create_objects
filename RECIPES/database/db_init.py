# RECIPES/users/db_init.py
import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from time import sleep

load_dotenv()

SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME")
SUPERADMIN_PASSWORD = os.getenv("SUPERADMIN_PASSWORD")
if not SUPERADMIN_USERNAME or not SUPERADMIN_PASSWORD:
    raise ValueError("SUPERADMIN_USERNAME и SUPERADMIN_PASSWORD должны быть заданы в переменных окружения!")

DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Создаёт и возвращает подключение с повторными попытками."""
    max_retries = 5
    retry_delay = 1

    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(
                DB_URL,
                cursor_factory=DictCursor,
                connect_timeout=5
            )
            conn.autocommit = False
            return conn
        except psycopg2.OperationalError as e:
            print(f"Попытка {_ + 1} подключения к базе данных не удалась: {e}")
            if _ < max_retries - 1:
                sleep(retry_delay)
    raise RuntimeError("Не удалось подключиться к базе данных после нескольких попыток.")

def init_users_table():
    """Создаёт все таблицы и админа 'superadmin', если не существует."""
    conn = psycopg2.connect(DB_URL, cursor_factory=DictCursor)
    # ВАЖНО: Отключаем autocommit, чтобы управлять транзакцией вручную
    conn.autocommit = False 
    cursor = conn.cursor()

    try:
        # 1. Создаем таблицы
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                object_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                unit TEXT NOT NULL,
                FOREIGN KEY (object_id) REFERENCES objects (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
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

        # 2. Проверка и вставка данных
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO settings (id, auth_code) VALUES (1, NULL)")

        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (SUPERADMIN_USERNAME,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                (SUPERADMIN_USERNAME, generate_password_hash(SUPERADMIN_PASSWORD), 1)
            )
            print(f"✅ Суперпользователь '{SUPERADMIN_USERNAME}' создан.")

        # КРИТИЧЕСКИ ВАЖНО: Фиксируем изменения!
        conn.commit()
        print("✅ Все таблицы и данные успешно инициализированы.")

    except psycopg2.Error as e:
        conn.rollback()  # Откатываем всё при ошибке
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        raise e # Пробрасываем ошибку дальше, чтобы docker-compose понял, что инициализация провалена
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Этот блок выполнится только когда вы запускаете: python -m RECIPES.database.db_init
    try:
        print("🚀 Starting database initialization...")
        init_users_table()
    except Exception as e:
        print(f"❌ Critical error during initialization: {e}")
        exit(1)