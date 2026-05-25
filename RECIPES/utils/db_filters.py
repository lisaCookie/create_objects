# RECIPES/utils/db_filters.py

from typing import Optional, Tuple, List, Dict, Any

# =====================
# ADMIN FILTERS (SQL)
# =====================

def build_users_filter_sql(creator_id: Optional[str] = None) -> Tuple[str, List]:
    """ Строит SQL-запрос для получения пользователей с фильтрацией по создателю. """
    sql = """
        SELECT u.id, u.username, u.is_admin, COUNT(DISTINCT o.id) as objects_count, COUNT(DISTINCT c.id) as comments_count
        FROM users u
        LEFT JOIN objects o ON u.id = o.created_by
        LEFT JOIN comments c ON u.id = c.user_id
        WHERE 1=1
    """
    params = []
    if creator_id:
        sql += " AND u.id = ?"
        params.append(creator_id)
    sql += " GROUP BY u.id ORDER BY u.username"
    return sql, params


def build_categories_filter_sql(creator_id: Optional[str] = None, object_id: Optional[str] = None) -> Tuple[str, List]:
    """ Строит SQL-запрос для получения категорий с фильтрацией по создателю и/или объекту. """
    sql = """
        SELECT c.id, c.name, u.username AS created_by, COUNT(DISTINCT o.id) as objects_count
        FROM categories c
        JOIN users u ON c.created_by = u.id
        LEFT JOIN objects o ON c.id = o.category_id
        WHERE 1=1
    """
    params = []
    if creator_id:
        sql += " AND c.created_by = ?"
        params.append(creator_id)
    if object_id:
        sql += " AND c.id IN (SELECT category_id FROM objects WHERE id = ?)"
        params.append(object_id)
    sql += " GROUP BY c.id ORDER BY c.name"
    return sql, params


def build_objects_filter_sql(creator_id: Optional[str] = None, category_id: Optional[str] = None) -> Tuple[str, List]:
    """ Строит SQL-запрос для получения объектов с фильтрацией по создателю и/или категории. """
    sql = """
        SELECT o.id, o.name, o.description, o.category_id, c.name AS category_name, u.username AS created_by, o.created_at
        FROM objects o
        JOIN categories c ON o.category_id = c.id
        JOIN users u ON o.created_by = u.id
        WHERE 1=1
    """
    params = []
    if creator_id:
        sql += " AND o.created_by = ?"
        params.append(creator_id)
    if category_id:
        sql += " AND o.category_id = ?"
        params.append(category_id)
    sql += " ORDER BY o.created_at DESC"
    return sql, params


def build_comments_filter_sql(object_id: Optional[str] = None, creator_id: Optional[str] = None, category_id: Optional[str] = None) -> Tuple[str, List]:
    """ Строит SQL-запрос для получения комментариев с фильтрацией по объекту, создателю и/или категории. """
    sql = """
        SELECT c.id, c.text, o.name AS object_name, u.username AS user_name, c.created_at, c.object_id, c.user_id
        FROM comments c
        JOIN objects o ON c.object_id = o.id
        JOIN users u ON c.user_id = u.id
        WHERE 1=1
    """
    params = []
    if object_id:
        sql += " AND c.object_id = ?"
        params.append(object_id)
    if creator_id:
        sql += " AND c.user_id = ?"
        params.append(creator_id)
    if category_id:
        sql += " AND c.object_id IN (SELECT id FROM objects WHERE category_id = ?)"
        params.append(category_id)
    sql += " ORDER BY c.created_at DESC"
    return sql, params


# =====================
# SEARCH FILTERS (SQL)
# =====================

def search_objects_sql(search_term: str) -> Tuple[str, List]:
    """ Выполняет поиск объектов по имени в базе данных. """
    if not search_term:
        return "", []
    sql = """
        SELECT o.id, o.name, o.created_at, c.name AS category_name
        FROM objects o
        JOIN categories c ON o.category_id = c.id
        WHERE o.name LIKE ?
        ORDER BY o.created_at DESC
    """
    return sql, ['%' + search_term + '%']


# =====================
# MY CONTRIBUTION FILTERS (SQL)
# =====================

def build_my_contribution_sql(user_id: str, category_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """ Возвращает SQL-запросы и параметры для объектов и комментариев пользователя. """
    if category_id:
        # Объекты пользователя в выбранной категории
        sql_objects = """
            SELECT o.id, o.name, o.description, o.created_at, cat.id as category_id, cat.name as category_name
            FROM objects o
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.created_by = ? AND o.category_id = ?
            ORDER BY o.created_at DESC
        """
        params_objects = [user_id, category_id]

        # Комментарии пользователя ко всем объектам в выбранной категории
        sql_comments = """
            SELECT c.id, c.text, c.created_at, o.name as object_name, c.object_id, o.category_id, cat.name as category_name
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.category_id = ? AND c.user_id = ?
            ORDER BY c.created_at DESC
        """
        params_comments = [category_id, user_id]

    else:
        # Все объекты пользователя (без фильтра по категории)
        sql_objects = """
            SELECT o.id, o.name, o.description, o.created_at, cat.id as category_id, cat.name as category_name
            FROM objects o
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.created_by = ?
            ORDER BY o.created_at DESC
        """
        params_objects = [user_id]

        # Все комментарии пользователя (к любым объектам)
        sql_comments = """
            SELECT c.id, c.text, c.created_at, o.name as object_name, c.object_id, o.category_id, cat.name as category_name
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN categories cat ON o.category_id = cat.id
            WHERE c.user_id = ?
            ORDER BY c.created_at DESC
        """
        params_comments = [user_id]

    return {
        'objects': {'sql': sql_objects, 'params': params_objects},
        'comments': {'sql': sql_comments, 'params': params_comments}
    }