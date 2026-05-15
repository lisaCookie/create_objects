# RECIPES/admin/services/auth_service.py
from RECIPES.database.db_settings import get_auth_code, update_settings_auth_code

def get_current_auth_code():
    return get_auth_code()

def update_auth_code(new_code):
    return update_settings_auth_code(new_code)
