# RECIPES/utils/filters.py

from typing import List, Dict, Any, Optional
from .db_filters import search_objects_sql


def filter_categories_by_search(categories: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """
    Рекурсивно фильтрует дерево категорий.
    Поиск расширяется по мере ввода: 'а' -> 'аб' -> 'абр'.
    Ищет совпадение с НАЧАЛО слова.
    """
    if not search_term:
        return categories
   
    # УБИРАЕМ [:1]. Теперь берем весь введенный текст,
    # но приводим к нижнему регистру для корректного сравнения.
    search_term = search_term.strip().lower()

    def _filter_node(cat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Используем startswith(search_term) без ограничения длины.
        # Теперь если ввели "Аб", найдет "Абрикос", но не найдет "Саб".
        matches = cat['name'].lower().startswith(search_term)
       
        children = cat.get('children', [])
        filtered_children = []
        for child in children:
            res = _filter_node(child)
            if res:
                filtered_children.append(res)
       
        if matches or filtered_children:
            cat_copy = cat.copy()
            cat_copy['children'] = filtered_children
            return cat_copy
        return None

    return [cat for c in categories if (cat := _filter_node(c)) is not None]


def search_objects_in_db(conn, search_term: str) -> List[Dict[str, Any]]:
    """
    Выполняет поиск объектов в БД.
    По мере ввода символов запрос уточняется (LIKE 'a%', LIKE 'ab%').
    """
    if not search_term:
        return []
   
    # УБИРАЕМ [:1]. Теперь передаем в SQL всю строку, которую ввел пользователь.
    search_term = search_term.strip().lower()
   
    # SQL должен использовать оператор LIKE 'term%'
    # Если пользователь ввел "Аб", SQL будет: WHERE name LIKE 'аб%'
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