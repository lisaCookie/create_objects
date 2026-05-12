# RECIPES/users/my_contribution.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from datetime import datetime
from RECIPES.users.work_db_users import get_db_connection

my_contribution_bp = Blueprint('my_contribution', __name__)

@my_contribution_bp.route('/my-contribution')
def my_contribution():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы, чтобы просмотреть свой вклад.')
        return redirect(url_for('login.login'))

    user_id = session['user_id']
    conn = get_db_connection()

    with conn:
        # 1. Получить все категории, созданные пользователем
        categories_raw = conn.execute("""
            SELECT id, name, created_at FROM categories WHERE created_by = ? ORDER BY created_at DESC
        """, (user_id,)).fetchall()

        # Преобразуем строки дат в datetime
        categories = []
        for cat in categories_raw:
            created_at = datetime.strptime(cat['created_at'], '%Y-%m-%d %H:%M:%S')  # Уточните формат, если другой
            categories.append({
                'id': cat['id'],
                'name': cat['name'],
                'created_at': created_at
            })

        # 2. Получить все объекты (рецепты), созданные пользователем
        objects_raw = conn.execute("""
            SELECT o.id, o.name, o.description, o.created_at, c.id as category_id, c.name as category_name
            FROM objects o JOIN categories c ON o.category_id = c.id
            WHERE o.created_by = ? ORDER BY o.created_at DESC
        """, (user_id,)).fetchall()

        objects = []
        for obj in objects_raw:
            created_at = datetime.strptime(obj['created_at'], '%Y-%m-%d %H:%M:%S')
            objects.append({
                'id': obj['id'],
                'name': obj['name'],
                'description': obj['description'],
                'created_at': created_at,
                'category_id': obj['category_id'],
                'category_name': obj['category_name']
            })

        # 3. Получить все комментарии, оставленные пользователем
        comments_raw = conn.execute("""
            SELECT c.id, c.text, c.created_at, o.name as object_name, c.object_id, o.category_id, cat.name as category_name
            FROM comments c JOIN objects o ON c.object_id = o.id JOIN categories cat ON o.category_id = cat.id
            WHERE c.user_id = ? ORDER BY c.created_at DESC
        """, (user_id,)).fetchall()

        comments = []
        for comment in comments_raw:
            created_at = datetime.strptime(comment['created_at'], '%Y-%m-%d %H:%M:%S')
            comments.append({
                'id': comment['id'],
                'text': comment['text'],
                'created_at': created_at,
                'object_name': comment['object_name'],
                'object_id': comment['object_id'],
                'category_name': comment['category_name'],
                'category_id': comment['category_id']
            })

    return render_template(
        'my_contribution.html',
        categories=categories,
        objects=objects,
        comments=comments
    )
