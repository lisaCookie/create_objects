# RECIPES/users/my_contribution.py


from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from datetime import datetime
from RECIPES.database.db_init import get_db_connection
from RECIPES.utils.db_filters import build_my_contribution_sql

my_contribution_bp = Blueprint('my_contribution', __name__)

@my_contribution_bp.route('/my-contribution')
def my_contribution():
    if 'user_id' not in session:
        flash('Авторизуйтесь для просмотра вашего вклада.', 'warning')
        return redirect(url_for('login.login'))

    user_id = session['user_id']
    category_id = request.args.get('category_id')

    # 1. Получаем SQL-запросы и параметры через рефакторинг-функцию
    filter_data = build_my_contribution_sql(user_id, category_id)

    # 2. Инициализируем списки
    categories_for_filter = []
    objects = []
    comments = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # --- ПОЛУЧАЕМ КАТЕГОРИИ ДЛЯ ФИЛЬТРА ---
        cursor.execute("""
            SELECT id, name, created_at
            FROM categories
            WHERE created_by = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows_cat = cursor.fetchall()
        for row in rows_cat:
            # Обработка даты (на случай если она приходит строкой или объектом)
            dt = row[2]
            if isinstance(dt, str):
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            
            categories_for_filter.append({
                'id': row[0],
                'name': row[1],
                'created_at': dt
            })

        # --- ПОЛУЧАЕМ ОБЪЕКТЫ ---
        cursor.execute(filter_data['objects']['sql'], filter_data['objects']['params'])
        rows_obj = cursor.fetchall()
        for row in rows_obj:
            dt = row[3]
            if isinstance(dt, str):
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            
            objects.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': dt,
                'category_id': row[4],
                'category_name': row[5]
            })

        # --- ПОЛУЧАЕМ КОММЕНТАРИИ ---
        cursor.execute(filter_data['comments']['sql'], filter_data['comments']['params'])
        rows_com = cursor.fetchall()
        for row in rows_com:
            dt = row[2]
            if isinstance(dt, str):
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')

            comments.append({
                'id': row[0],
                'text': row[1],
                'created_at': dt,
                'object_name': row[3],
                'object_id': row[4],
                'category_id': row[5],
                'category_name': row[6]
            })

    # 3. ПЕРЕДАЕМ ДАННЫЕ В ШАБЛОН
    # ВАЖНО: Мы передаем и categories, и all_categories_for_filter, 
    # чтобы удовлетворить требования вашего шаблона.
    return render_template(
        'my_contribution.html',
        categories=categories_for_filter,               # Для основного списка (если используется)
        all_categories_for_filter=categories_for_filter, # ДЛЯ ВЫПАДАЮЩЕГО СПИСКА (критично!)
        objects=objects,
        comments=comments,
        current_category_id=category_id
    )