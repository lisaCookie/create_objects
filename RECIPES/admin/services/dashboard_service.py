# RECIPES/admin/services/dashboard_service.py
from RECIPES.database.db_init import get_db_connection
from RECIPES.utils.admin_filters import (
    build_users_filter_sql,
    build_categories_filter_sql,
    build_objects_filter_sql,
    build_comments_filter_sql,
)

def get_dashboard_data(creator_id_filter=None, category_id_filter=None, object_id_filter=None):
    conn = get_db_connection()
    with conn:
        # Получаем данные для фильтров (все пользователи/категории/объекты)
        all_users_for_filter = conn.execute(
            "SELECT id, username FROM users ORDER BY username"
        ).fetchall()

        all_categories_for_filter = conn.execute(
            "SELECT id, name FROM categories ORDER BY name"
        ).fetchall()

        all_objects_for_filter = conn.execute("""
            SELECT o.id, o.name, c.name AS category_name
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            ORDER BY c.name, o.name
        """).fetchall()

        # Применяем фильтры
        users_sql, users_params = build_users_filter_sql(creator_id_filter)
        users = conn.execute(users_sql, users_params).fetchall()

        categories_sql, categories_params = build_categories_filter_sql(creator_id_filter, object_id_filter)
        categories = conn.execute(categories_sql, categories_params).fetchall()

        objects_sql, objects_params = build_objects_filter_sql(creator_id_filter, category_id_filter)
        objects = conn.execute(objects_sql, objects_params).fetchall()

        comments_sql, comments_params = build_comments_filter_sql(object_id_filter, creator_id_filter, category_id_filter)
        comments = conn.execute(comments_sql, comments_params).fetchall()

        return {
            'users': users,
            'categories': categories,
            'objects': objects,
            'comments': comments,
            'all_users_for_filter': all_users_for_filter,
            'all_categories_for_filter': all_categories_for_filter,
            'all_objects_for_filter': all_objects_for_filter,
            'current_creator_id': creator_id_filter,
            'current_category_id': category_id_filter,
            'current_object_id': object_id_filter,
        }
