# utils/my_contrib_filters.py

# utils/my_contrib_filters.py

def generate_my_contribution_filters_sql(user_id, category_id=None, object_id=None):
    """
    Генерирует SQL-параметры для получения данных пользователя (объектов и/или комментариев)
    с учетом фильтрации по категории и/или объекту.

    Args:
        user_id (int): ID текущего пользователя.
        category_id (int, optional): ID категории для фильтрации объектов.
        object_id (int, optional): ID объекта для фильтрации комментариев.

    Returns:
        dict: Словарь с ключами 'sql' (SQL-запрос) и 'params' (параметры).
              Если нет подходящих данных или фильтры несовместимы, может вернуть пустые значения.
    """
    
    # --- Определяем, что мы ищем: объекты или комментарии ---
    
    # Если есть object_id, мы ищем комментарии к этому объекту.
    if object_id:
        # Фильтруем комментарии, связанные с конкретным объектом, который принадлежит пользователю.
        # Требование: "фильтр по объектам показывает комменты этого объекта"
        sql = """
            SELECT c.id, c.text, c.created_at, o.name as object_name, o.id as object_id, cat.name as category_name, cat.id as category_id
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.id = ? AND o.created_by = ?
            ORDER BY c.created_at DESC
        """
        params = [object_id, user_id]
        return {'sql': sql, 'params': params}

    # Если есть category_id (и нет object_id), мы ищем объекты в этой категории.
    # Требование: "фильтр по категории показывает объекты в этой категории"
    elif category_id:
        sql = """
            SELECT o.id, o.name, o.description, o.created_at, cat.id as category_id, cat.name as category_name
            FROM objects o
            JOIN categories cat ON o.category_id = cat.id
            WHERE o.category_id = ? AND o.created_by = ?
            ORDER BY o.created_at DESC
        """
        params = [category_id, user_id]
        return {'sql': sql, 'params': params}

    # Если нет ни object_id, ни category_id, значит, мы показываем все данные пользователя.
    # Это включает в себя и объекты, и комментарии.
    # Здесь нужно вернуть два SQL-запроса: один для объектов, другой для комментариев.
    # Это сделано для того, чтобы в my_contribution.py можно было получить оба списка.
    else:
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
