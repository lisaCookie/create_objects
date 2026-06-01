# RECIPES/categories/services/obj_category_service.py
from RECIPES.database.db_init import get_db_connection
from RECIPES.categories.repositories.category_repository import CategoryRepository
from RECIPES.categories.validation import validate_not_empty, check_category_ownership, validate_object_exists


def get_category_by_id(category_id):
    return CategoryRepository.get_by_id(category_id)


def create_category(name, created_by, parent_id=None):
    validate_not_empty(name, "Имя категории")
    if parent_id is not None and not CategoryRepository.check_parent_exists(parent_id):
        raise ValueError("Родительская категория не найдена")
    return CategoryRepository.create(name, created_by, parent_id)


def create_subcat(name, created_by, parent_id):
    validate_not_empty(name, "Название подкатегории")
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
    validate_not_empty(name, "Название категории")
    owner_check = CategoryRepository.get_owner_check(category_id, user_id)

    if not check_category_ownership(owner_check):
        raise ValueError("У вас нет прав на редактирование этой категории")

    CategoryRepository.update(name.strip(), category_id)



def delete_category_service(category_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Замените `?` на `%s` для стиля параметров psycopg2 по умолчанию
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    is_admin_row = cursor.fetchone()

    conn.close()

    if not is_admin_row or not is_admin_row[0]:
        raise ValueError("Только администратор может удалять категории")

    category = CategoryRepository.get_by_id(category_id)
    validate_object_exists(category, "Категория не найдена")
    CategoryRepository.delete(category_id)