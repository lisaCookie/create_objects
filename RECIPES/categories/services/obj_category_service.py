# RECIPES/categories/services/obj_category_service.py
from RECIPES.database.db_init import get_db_connection
import sqlite3


def get_category_by_id(category_id):
    conn = get_db_connection()
    with conn:
        row = conn.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,)).fetchone()
        return dict(row) if row else None

def create_category(name, created_by, parent_id=None):
    if not name or not name.strip():
        raise ValueError("Имя категории не может быть пустым")
    conn = get_db_connection()
    try:
        with conn:
            result = conn.execute("""
                INSERT INTO categories (name, created_by, parent_id)
                VALUES (?, ?, ?)
            """, (name.strip(), created_by, parent_id))
            return result.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Категория с таким именем уже существует")
    
def create_subcat(name, created_by, parent_id):
    if not name or not name.strip():
        raise ValueError("Название подкатегории не может быть пустым")
    if parent_id is None:
        raise ValueError("Не указан родительский идентификатор категории")
    conn = get_db_connection()
    try:
        with conn:
            # Проверяем, существует ли категория с данным parent_id
            parent_category = conn.execute(
                "SELECT id FROM categories WHERE id = ?", (parent_id,)
            ).fetchone()
            if not parent_category:
                raise ValueError("Родительская категория не найдена")
            # Проверяем, что название уникально в рамках этой родительской категории
            existing = conn.execute(
                "SELECT id FROM categories WHERE name = ? AND parent_id = ?",
                (name.strip(), parent_id)
            ).fetchone()
            if existing:
                raise ValueError("Подкатегория с таким именем уже существует в этой категории")
            # Вставляем новую подкатегорию
            result = conn.execute(
                """
                INSERT INTO categories (name, created_by, parent_id)
                VALUES (?, ?, ?)
                """,
                (name.strip(), created_by, parent_id)
            )
            return result.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Ошибка при создании подкатегории")
    

def get_all_categories_with_hierarchy():
    conn = get_db_connection()
    with conn:
        rows = conn.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
            FROM categories c JOIN users u ON c.created_by = u.id
            ORDER BY c.parent_id, c.name
        """).fetchall()
        categories = [dict(row) for row in rows]
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
    conn = get_db_connection()
    with conn:
        return [dict(row) for row in conn.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username, c.created_at
            FROM categories c JOIN users u ON c.created_by = u.id
            WHERE c.parent_id = ?
            ORDER BY c.name
        """, (parent_id,)).fetchall()]

def get_category_detail_owner_check(category_id, user_id):
    conn = get_db_connection()
    with conn:
        category = conn.execute("""
            SELECT c.id, c.name, c.created_by, u.username AS created_by_username
            FROM categories c LEFT JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,)).fetchone()

        if not category:
            return None

        category = dict(category)
        is_owner = (category['created_by'] == user_id)
        is_admin_row = conn.execute(
            "SELECT is_admin FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        is_admin = is_admin_row and is_admin_row['is_admin']
        can_edit = is_owner or (is_admin and is_admin)

        return {
            'category': category,
            'can_edit': can_edit
        }