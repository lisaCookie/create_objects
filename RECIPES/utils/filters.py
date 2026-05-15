# RECIPES/utils/filters.py

from typing import List, Dict, Any, Optional


def filter_categories_by_search(categories: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """
    Рекурсивно фильтрует дерево категорий по поисковому запросу.
    Возвращает копию дерева с отфильтрованными категориями.
    
    :param categories: Список категорий с иерархией (с ключом 'children')
    :param search_term: Поисковая строка (регистронезависимая)
    :return: Отфильтрованное дерево категорий
    """
    if not search_term:
        return categories

    search_term = search_term.strip().lower()

    def _filter_node(cat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        matches = search_term in cat['name'].lower()
        children = cat.get('children', [])
        filtered_children = [_filter_node(child) for child in children]
        filtered_children = [child for child in filtered_children if child is not None]

        if matches or filtered_children:
            cat_copy = cat.copy()
            cat_copy['children'] = filtered_children
            return cat_copy
        return None

    return [cat for cat in (_filter_node(c) for c in categories) if cat is not None]


def search_objects_in_db(conn, search_term: str) -> List[Dict[str, Any]]:
    """
    Выполняет поиск объектов по имени в базе данных.
    
    :param conn: SQLite соединение
    :param search_term: Поисковая строка
    :return: Список объектов с полями id, name, created_at, category_name
    """
    if not search_term:
        return []

    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.id, o.name, o.created_at, c.name AS category_name
        FROM objects o
        JOIN categories c ON o.category_id = c.id
        WHERE o.name LIKE ?
        ORDER BY o.created_at DESC
    """, ('%' + search_term + '%',))

    return [
        {
            'id': row[0],
            'name': row[1],
            'created_at': row[2],
            'category_name': row[3]
        }
        for row in cursor.fetchall()
    ]
