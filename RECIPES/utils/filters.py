# RECIPES/utils/filters.py

from typing import List, Dict, Any, Optional
from .db_filters import search_objects_sql


def filter_categories_by_search(categories: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """ Рекурсивно фильтрует дерево категорий по поисковому запросу. """
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
    """ Выполняет поиск объектов по имени в базе данных. """
    if not search_term:
        return []
    sql, params = search_objects_sql(search_term)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return [
        {
            'id': row[0],
            'name': row[1],
            'created_at': row[2],
            'category_name': row[3]
        }
        for row in cursor.fetchall()
    ]