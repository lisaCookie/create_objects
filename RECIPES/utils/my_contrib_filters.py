# utils/my_contrib_filters.py

def generate_my_contribution_filters_sql(user_id, category_id=None):
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
