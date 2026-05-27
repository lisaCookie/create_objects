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
    try:
        with conn:
            cursor = conn.cursor()
            # Получаем данные для фильтров
            cursor.execute("SELECT id, username FROM users ORDER BY username")
            all_users_for_filter = cursor.fetchall()

            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            all_categories_for_filter = cursor.fetchall()

            cursor.execute("""
                SELECT
                    o.id, o.name, c.name AS category_name,
                    TO_CHAR(o.created_at, 'YYYY-MM-DD') AS created_at
                    FROM objects o
                    JOIN categories c ON o.category_id = c.id
                    ORDER BY c.name, o.name
            """)
            all_objects_for_filter = cursor.fetchall()

            # Применяем фильтры
            users_sql, users_params = build_users_filter_sql(creator_id_filter)
            cursor.execute(users_sql, users_params)
            users = cursor.fetchall()

            categories_sql, categories_params = build_categories_filter_sql(creator_id_filter, object_id_filter)
            cursor.execute(categories_sql, categories_params)
            categories = cursor.fetchall()

            objects_sql, objects_params = build_objects_filter_sql(creator_id_filter, category_id_filter)
            cursor.execute(objects_sql, objects_params)
            objects = cursor.fetchall()

            comments_sql, comments_params = build_comments_filter_sql(object_id_filter, creator_id_filter, category_id_filter)
            cursor.execute(comments_sql, comments_params)
            comments = cursor.fetchall()

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
    finally:
        conn.close()
