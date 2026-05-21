from RECIPES.database.db_init import get_db_connection


def get_ingredients_by_object_id_rep(object_id):
    """Возвращает ингредиенты для объекта из БД."""
    conn = get_db_connection()
    with conn:
        result = conn.execute("""
            SELECT name, amount, unit
            FROM ingredients
            WHERE object_id = ?
            ORDER BY name
        """, (object_id,))
        return [dict(row) for row in result.fetchall()]

def insert_ingredients_for_object_rep(object_id, ingredient_data):
    """
    Вставляет ингредиенты для объекта в БД.
    `ingredient_data` — список словарей вида [{'name': ..., 'amount': ..., 'unit': ...}].
    """
    conn = get_db_connection()
    with conn:
        conn.executemany("""
            INSERT INTO ingredients (object_id, name, amount, unit)
            VALUES (?, ?, ?, ?)
        """, [(object_id, item['name'], item['amount'], item['unit']) for item in ingredient_data])
