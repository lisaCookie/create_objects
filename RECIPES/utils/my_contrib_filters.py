# utils/my_contrib_filters.py

def generate_my_contribution_filters_sql(user_id, category_id=None):
    """
    Генерирует SQL-параметры для получения данных пользователя (объектов и комментариев)
    с фильтрацией только по категории. object_id игнорируется.

    Args:
        user_id (int): ID текущего пользователя.
        category_id (int, optional): ID категории для фильтрации.

    Returns:
        dict: Словарь с ключами 'objects' и 'comments', каждый содержит 'sql' и 'params'.
              Если category_id не указан — возвращает данные по всему пользователю.
    """
    if category_id:
        # Фильтруем объекты и комментарии по категории
        sql_objects = """
            SELECT o.id, o.name, o.description, o.created_at, cat.id as category_id, cat.name as category_name
            FROM objects o
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.category_id = ? AND o.created_by = ?
            ORDER BY o.created_at DESC
        """
        params_objects = [category_id, user_id]

        sql_comments = """
            SELECT c.id, c.text, c.created_at, o.name as object_name, c.object_id, o.category_id, cat.name as category_name
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.category_id = ? AND o.created_by = ?
            ORDER BY c.created_at DESC
        """
        params_comments = [category_id, user_id]

        return {
            'objects': {'sql': sql_objects, 'params': params_objects},
            'comments': {'sql': sql_comments, 'params': params_comments}
        }

    else:
        # Показываем всё: объекты и комментарии пользователя без фильтра
        sql_objects = """
            SELECT o.id, o.name, o.description, o.created_at, cat.id as category_id, cat.name as category_name
            FROM objects o
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.created_by = ?
            ORDER BY o.created_at DESC
        """
        params_objects = [user_id]

        sql_comments = """
            SELECT c.id, c.text, c.created_at, o.name as object_name, c.object_id, o.category_id, cat.name as category_name
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.created_by = ?
            ORDER BY c.created_at DESC
        """
        params_comments = [user_id]

        return {
            'objects': {'sql': sql_objects, 'params': params_objects},
            'comments': {'sql': sql_comments, 'params': params_comments}
        }
