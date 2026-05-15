# RECIPES/users/db_settings.py
import sqlite3
from RECIPES.database.db_init import get_db_connection

def get_auth_code():
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT auth_code FROM settings WHERE id = 1")
        row = cursor.fetchone()
        return row[0] if row else None

def update_settings_auth_code(new_code):
    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE settings SET auth_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (new_code,)
        )
        return cursor.rowcount > 0
