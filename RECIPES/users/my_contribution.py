# RECIPES/users/my_contribution.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from datetime import datetime
from RECIPES.database.db_init import get_db_connection
# Импортируем функцию генерации SQL
from RECIPES.utils.my_contrib_filters import generate_my_contribution_filters_sql


my_contribution_bp = Blueprint('my_contribution', __name__)

@my_contribution_bp.route('/my-contribution')
def my_contribution():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы, чтобы просмотреть свой вклад.')
        return redirect(url_for('login.login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Получение фильтров из запроса
    category_id = request.args.get('category_id')
    object_id = request.args.get('object_id')

    # Получаем SQL-параметры для нужных данных
    filter_params = generate_my_contribution_filters_sql(
        user_id=user_id,
        category_id=category_id,
        object_id=object_id
    )

    # Инициализируем переменные для отображения
    categories_for_filter = []
    objects_for_display = []
    comments_for_display = []

    with conn:
        # 1. Получаем все категории пользователя (для выпадающего списка фильтров)
        # Эта часть не зависит от фильтров, она нужна для заполнения селекта.
        categories_raw = conn.execute("""
            SELECT id, name, created_at FROM categories WHERE created_by = ? ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        for cat in categories_raw:
            created_at = datetime.strptime(cat['created_at'], '%Y-%m-%d %H:%M:%S')
            categories_for_filter.append({
                'id': cat['id'],
                'name': cat['name'],
                'created_at': created_at
            })

        # 2. Обрабатываем результаты в зависимости от того, что вернула функция генерации SQL
        if isinstance(filter_params, dict) and 'sql' in filter_params: 
            sql = filter_params['sql']
            params = filter_params['params']
            
            # Простой способ определить, что мы запросили:
            if object_id: # Если был object_id, то это точно комментарии
                results_raw = conn.execute(sql, params).fetchall()
                for row in results_raw:
                    created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                    comments_for_display.append({
                        'id': row['id'],
                        'text': row['text'],
                        'created_at': created_at,
                        'object_name': row['object_name'],
                        'object_id': row['object_id'],
                        'category_name': row['category_name'],
                        'category_id': row['category_id']
                    })
            elif category_id: # Если был category_id (и не object_id), то это объекты
                results_raw = conn.execute(sql, params).fetchall()
                for row in results_raw:
                    created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                    objects_for_display.append({
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'created_at': created_at,
                        'category_id': row['category_id'],
                        'category_name': row['category_name']
                    })

        elif isinstance(filter_params, dict) and 'objects' in filter_params and 'comments' in filter_params: # Если вернулись два SQL (все данные пользователя)
            # Получаем объекты
            objects_sql_params = filter_params['objects']
            results_objects_raw = conn.execute(objects_sql_params['sql'], objects_sql_params['params']).fetchall()
            for row in results_objects_raw:
                created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                objects_for_display.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': created_at,
                    'category_id': row['category_id'],
                    'category_name': row['category_name']
                })

            # Получаем комментарии
            comments_sql_params = filter_params['comments']
            results_comments_raw = conn.execute(comments_sql_params['sql'], comments_sql_params['params']).fetchall()
            for row in results_comments_raw:
                created_at = datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S')
                comments_for_display.append({
                    'id': row['id'],
                    'text': row['text'],
                    'created_at': created_at,
                    'object_name': row['object_name'],
                    'object_id': row['object_id'],
                    'category_name': row['category_name'],
                    'category_id': row['category_id']
                })

    return render_template(
        'my_contribution.html',
        categories=categories_for_filter, # Для выпадающего списка категорий
        objects=objects_for_display,       # Объекты для отображения на странице
        comments=comments_for_display,     # Комментарии для отображения на странице
        all_categories_for_filter=categories_for_filter, # Все категории для выпадающего списка
        current_category_id=category_id,
        current_object_id=object_id
    )
