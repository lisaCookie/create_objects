# RECIPES/categories/services/obj_ingredient_service.py
from RECIPES.database.db_init import get_db_connection

def get_ingredients_by_object_id(object_id):
    conn = get_db_connection()
    with conn:
        ingredients = conn.execute("""
            SELECT name, amount, unit
            FROM ingredients
            WHERE object_id = ?
            ORDER BY name
        """, (object_id,)).fetchall()
        return [dict(row) for row in ingredients]

def insert_ingredients_for_object(object_id, ingredient_names, ingredient_amounts, ingredient_units):
    conn = get_db_connection()
    with conn:
        for i in range(len(ingredient_names)):
            name = ingredient_names[i].strip()
            amount = ingredient_amounts[i].strip()
            unit = ingredient_units[i] if i < len(ingredient_units) else 'ml'

            if name and amount and amount.isdigit() and int(amount) >= 0:
                conn.execute("""
                    INSERT INTO ingredients (object_id, name, amount, unit)
                    VALUES (?, ?, ?, ?)
                """, (object_id, name, int(amount), unit))
