# RECIPES/categories/services/obj_ingredient_service.py

from RECIPES.categories.repositories.ingredient_repository import (
    get_ingredients_by_object_id_rep,
    insert_ingredients_for_object_rep
)

def get_ingredients_by_object_id(object_id):
    """Возвращает список ингредиентов для объекта (биндинг с репозиторием)."""
    return get_ingredients_by_object_id_rep(object_id)


def insert_ingredients_for_object(object_id, ingredient_names, ingredient_amounts, ingredient_units):
    """
    Вставляет ингредиенты для объекта.
    Преобразует входные данные в формат для репозитория и делегирует выполнение.
    """
    ingredient_data = []
    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        amount = ingredient_amounts[i].strip()
        unit = ingredient_units[i] if i < len(ingredient_units) else 'ml'

        if name and amount and amount.isdigit() and int(amount) >= 0:
            ingredient_data.append({
                'name': name,
                'amount': int(amount),
                'unit': unit
            })

    if ingredient_data:
        insert_ingredients_for_object_rep(object_id, ingredient_data)


def parse_ingredients_for_object(ingredient_names, ingredient_amounts, ingredient_units):

    ingredients = []
    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        amount = ingredient_amounts[i].strip()
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else 'ml'

        if name:  # Проверяем только имя (количество может быть пустым)
            ingredients.append((name, amount, unit))
    return ingredients
