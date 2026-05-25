# RECIPES/utils/admin_filters.py

from typing import Optional

from typing import Optional
from .db_filters import build_users_filter_sql, build_categories_filter_sql, build_objects_filter_sql, build_comments_filter_sql


def build_users_filter_sql_wrapper(creator_id: Optional[str] = None) -> tuple[str, list]:
    """ Обёртка для совместимости — просто делегирует вызов в db_filters """
    return build_users_filter_sql(creator_id)


def build_categories_filter_sql_wrapper(creator_id: Optional[str] = None, object_id: Optional[str] = None) -> tuple[str, list]:
    """ Обёртка для совместимости — просто делегирует вызов в db_filters """
    return build_categories_filter_sql(creator_id, object_id)


def build_objects_filter_sql_wrapper(creator_id: Optional[str] = None, category_id: Optional[str] = None) -> tuple[str, list]:
    """ Обёртка для совместимости — просто делегирует вызов в db_filters """
    return build_objects_filter_sql(creator_id, category_id)


def build_comments_filter_sql_wrapper(object_id: Optional[str] = None, creator_id: Optional[str] = None, category_id: Optional[str] = None) -> tuple[str, list]:
    """ Обёртка для совместимости — просто делегирует вызов в db_filters """
    return build_comments_filter_sql(object_id, creator_id, category_id)