# RECIPES/utils/admin_filters.py
from typing import Optional


def build_users_filter_sql(creator_id: Optional[str] = None) -> tuple[str, list]:
    """
    Строит SQL-запрос для получения пользователей с фильтрацией по создателю.
    :param creator_id: ID пользователя для фильтрации (опционально)
    :return: (sql_query, params_list)
    """
    sql = """
    SELECT u.id, u.username, u.is_admin, 
           COUNT(DISTINCT o.id) as objects_count, 
           COUNT(DISTINCT c.id) as comments_count 
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


def build_categories_filter_sql(creator_id: Optional[str] = None, object_id: Optional[str] = None) -> tuple[str, list]:
    """
    Строит SQL-запрос для получения категорий с фильтрацией по создателю и/или объекту.
    :param creator_id: ID создателя категории
    :param object_id: ID объекта — если задан, показываем только категории, к которым он относится
    :return: (sql_query, params_list)
    """
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


def build_objects_filter_sql(creator_id: Optional[str] = None, category_id: Optional[str] = None) -> tuple[str, list]:
    """
    Строит SQL-запрос для получения объектов с фильтрацией по создателю и/или категории.
    :param creator_id: ID создателя объекта
    :param category_id: ID категории
    :return: (sql_query, params_list)
    """
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


def build_comments_filter_sql(object_id: Optional[str] = None, creator_id: Optional[str] = None, category_id: Optional[str] = None) -> tuple[str, list]:
    """
    Строит SQL-запрос для получения комментариев с фильтрацией по объекту, создателю и/или категории.
    :param object_id: ID объекта
    :param creator_id: ID создателя комментария
    :param category_id: ID категории (для фильтрации по категориям объектов)
    :return: (sql_query, params_list)
    """
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
