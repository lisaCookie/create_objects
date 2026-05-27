# utils/my_contrib_filters.py

from typing import Dict, Any, Optional
from .db_filters import build_my_contribution_sql


def generate_my_contribution_filters_sql(user_id: str, category_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """ Генерирует SQL-запросы и параметры для объектов и комментариев пользователя. """
    return build_my_contribution_sql(user_id, category_id)