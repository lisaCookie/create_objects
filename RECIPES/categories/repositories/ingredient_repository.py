# RECIPES/categories/repositories/ingredient_repository.py

from RECIPES.database.db_init import get_db_connection

def get_ingredients_by_object_id_rep(object_id):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, amount, unit
                FROM ingredients
                WHERE object_id = %s
                ORDER BY name
            """, (object_id,))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def insert_ingredients_for_object_rep(object_id, ingredient_data):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO ingredients (object_id, name, amount, unit)
                VALUES (%s, %s, %s, %s)
            """, [(object_id, item['name'], item['amount'], item['unit']) for item in ingredient_data])
    finally:
        conn.close()
