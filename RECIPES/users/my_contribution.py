# RECIPES/users/my_contribution.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from datetime import datetime
from RECIPES.database.db_init import get_db_connection
from RECIPES.utils.my_contrib_filters import generate_my_contribution_filters_sql

my_contribution_bp = Blueprint('my_contribution', __name__)

@my_contribution_bp.route('/my-contribution')
def my_contribution():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы, чтобы просмотреть свой вклад.')
        return redirect(url_for('login.login'))

    user_id = session['user_id']
    conn = get_db_connection()

    # Получаем фильтр только по категории — object_id игнорируется
    category_id = request.args.get('category_id')
    # object_id = request.args.get('object_id')  # УДАЛЕН — не используется

    # Генерируем SQL-параметры (только по category_id или без него)
    filter_params = generate_my_contribution_filters_sql(user_id=user_id, category_id=category_id)

    # Получаем все категории для выпадающего списка
    categories_for_filter = []
    with conn:
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

    # Инициализируем данные
    objects_for_display = []
    comments_for_display = []

    # Обрабатываем результаты: всегда возвращаются 'objects' и 'comments'
    with conn:
        # Объекты
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

        # Комментарии
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
        categories=categories_for_filter,
        objects=objects_for_display,
        comments=comments_for_display,
        all_categories_for_filter=categories_for_filter,
        current_category_id=category_id,
        current_object_id=None  # Убрано — не используется
    )
