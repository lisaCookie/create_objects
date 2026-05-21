# RECIPES/categories/services/obj_category_service.py
from RECIPES.database.db_init import get_db_connection
from RECIPES.categories.repositories.category_repository import CategoryRepository
from RECIPES.categories.services.admin_permission_service import has_admin_access


def get_category_by_id(category_id):
    return CategoryRepository.get_by_id(category_id)


def create_category(name, created_by, parent_id=None):
    if not name or not name.strip():
        raise ValueError("Имя категории не может быть пустым")

    if parent_id is not None and not CategoryRepository.check_parent_exists(parent_id):
        raise ValueError("Родительская категория не найдена")

    return CategoryRepository.create(name, created_by, parent_id)


def create_subcat(name, created_by, parent_id):
    if not name or not name.strip():
        raise ValueError("Название подкатегории не может быть пустым")

    if not parent_id:
        raise ValueError("Не указан родительский идентификатор категории")

    if not CategoryRepository.check_parent_exists(parent_id):
        raise ValueError("Родительская категория не найдена")

    if CategoryRepository.check_subcategory_exists(name, parent_id):
        raise ValueError("Подкатегория с таким именем уже существует в этой категории")

    return CategoryRepository.create(name, created_by, parent_id)


def get_all_categories_with_hierarchy():
    categories = CategoryRepository.get_all_with_hierarchy()
    hierarchy = {}

    for cat in categories:
        parent_id = cat['parent_id']
        if parent_id not in hierarchy:
            hierarchy[parent_id] = []
        hierarchy[parent_id].append(cat)

    def build_tree(parent_id=None, level=0):
        children = hierarchy.get(parent_id, [])
        result = []
        for child in children:
            child['level'] = level
            child['children'] = build_tree(child['id'], level + 1)
            result.append(child)
        return result

    return build_tree()


def get_categories_by_parent(parent_id):
    return CategoryRepository.get_by_parent(parent_id)


def get_category_detail_owner_check(category_id, user_id):
    return CategoryRepository.get_owner_check(category_id, user_id)


def edit_category_service(category_id, name, user_id):
    if not name or not name.strip():
        raise ValueError("Название категории не может быть пустым")

    is_admin = has_admin_access(user_id)
    owner_check = CategoryRepository.get_owner_check(category_id, user_id)

    # Админ может редактировать любые категории
    # Обычный пользователь только свои
    if not is_admin and (not owner_check or not owner_check['can_edit']):
        raise ValueError("У вас нет прав на редактирование этой категории")

    CategoryRepository.update(name.strip(), category_id)


def delete_category_service(category_id, user_id):
    # Проверка прав админа
    is_admin_row = get_db_connection().execute(
        "SELECT is_admin FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    is_admin = is_admin_row and is_admin_row['is_admin']

    if not is_admin:
        raise ValueError("Только администратор может удалять категории")

    # Проверяем, что категория существует
    category = CategoryRepository.get_by_id(category_id)
    if not category:
        raise ValueError("Категория не найдена")

    # ВСЁ ДАЛЬНЕЙШЕЕ УДАЛИЛ! Каскадное удаление происходит автоматически на уровне БД
    CategoryRepository.delete(category_id)  # <-- Теперь это достаточно
