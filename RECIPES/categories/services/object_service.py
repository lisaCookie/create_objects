# RECIPES/categories/services/object_service.py

from RECIPES.database.db_init import get_db_connection
from RECIPES.categories.repositories.object_repository import ObjectRepository
from RECIPES.categories.services.admin_permission_service import has_admin_access

# ===== Основные функции CRUD =====

def get_objects_by_category_id(category_id, user_id=None):
    """Возвращает объекты по ID категории (с учетом прав доступа)."""
    return ObjectRepository.get_by_category(category_id, user_id)

def create_obj(name, description, category_id, created_by, technology=None):
    """Создает новый объект (проверяет обязательные поля)."""
    if not name or not name.strip():
        raise ValueError("Имя объекта не может быть пустым")
    return ObjectRepository.create(name, description, category_id, created_by, technology)

def insert_object(name, description, category_id, user_id, technology=None):
    """Аналог create_obj, но с явно указанным user_id."""
    return ObjectRepository.insert(name, description, category_id, user_id, technology)

def get_object_by_id(object_id, user_id=None):
    """Возвращает объект по ID (с учетом доступа)."""
    return ObjectRepository.get_by_id(object_id, user_id)

# ===== Удаление и редактирование =====

def delete_obj(object_id, user_id):
    obj = ObjectRepository.get_dependencies(object_id)
    if not obj:
        raise ValueError("Объект не найден")

    # Админ может удалять любые объекты
    # Обычный пользователь только свои
    if obj['created_by'] != user_id and not has_admin_access(user_id):
        raise ValueError("Вы можете удалять только свои объекты")

    ObjectRepository.delete(object_id)

def edit_obj(object_id, name, description, technology, ingredients, user_id):
    """Редактирует объект и обновляет ингредиенты."""
    if not name or not name.strip():
        raise ValueError("Название объекта не может быть пустым")

    obj = ObjectRepository.get_by_id(object_id)
    if not obj:
        raise ValueError("Объект не найден")

    # Админ может редактировать любые объекты
    # Обычный пользователь только свои
    if obj['created_by'] != user_id and not has_admin_access(user_id):
        raise ValueError("Вы не можете редактировать чужой объект")

    ObjectRepository.update(name, description, technology, object_id)
    ObjectRepository.clear_ingredients(object_id)
    ObjectRepository.add_ingredients(object_id, ingredients)

# ===== Проверка прав доступа =====

def can_edit(user_id, owner_id, conn=None):
    """Проверяет, может ли пользователь редактировать объект (в том числе администраторы)."""
    if user_id == owner_id:
        return True

    conn = conn or get_db_connection()
    admin_status = conn.execute(
        "SELECT is_admin FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    return admin_status and admin_status['is_admin']
