# RECIPES/categories/validation.py

from flask import session, flash, redirect, url_for

def check_authentication():
    """Проверяет авторизацию пользователя."""
    return 'user_id' in session

def validate_object_exists(obj, error_message="Объект не найден."):
    """Проверяет существование объекта и выбрасывает ValueError при ошибке."""
    if not obj:
        raise ValueError(error_message)

def check_comment_ownership(current_user_id, comment_user_id):
    """Проверяет право редактирования комментария."""
    return current_user_id == comment_user_id

def check_category_ownership(category_owner_check):
    """Проверяет право редактирования категории."""
    return category_owner_check and category_owner_check.get('can_edit', False)

def validate_not_empty(value, field_name="Поле"):
    """Проверяет, что значение не пустое."""
    if not value:
        raise ValueError(f"{field_name} не может быть пустым.")
