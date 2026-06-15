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
    Поддерживает дробные числа и проверяет валидность данных.
    """
    ingredient_data = []
    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        amount_str = ingredient_amounts[i].strip()
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else 'ml'

        # Пропускаем пустые имена
        if not name:
            continue

        # Пробуем преобразовать количество в число (дробное или целое)
        try:
            amount = float(amount_str) if amount_str else 0.0
            if amount < 0:
                raise ValueError("Количество не может быть отрицательным")
        except ValueError:
            # Если преобразование не удалось, пропускаем этот ингредиент
            continue

        ingredient_data.append({
            'name': name,
            'amount': amount,  # Сохраняем как float для дробных значений
            'unit': unit
        })

    if ingredient_data:
        insert_ingredients_for_object_rep(object_id, ingredient_data)

def parse_ingredients_for_object(ingredient_names, ingredient_amounts, ingredient_units):
    """
    Парсит ингредиенты из массивов, поддерживая дробные числа.
    Возвращает список кортежей (name, amount, unit).
    """
    ingredients = []
    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        amount_str = ingredient_amounts[i].strip()
        unit = ingredient_units[i].strip() if i < len(ingredient_units) else 'ml'

        # Проверяем, что имя не пустое
        if not name:
            continue

        # Добавляем ингредиент только если имя валидно
        ingredients.append((name, amount_str, unit))
    return ingredients
