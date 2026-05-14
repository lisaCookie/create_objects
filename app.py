# app.py 

from flask import Flask, render_template, session, redirect, url_for, flash, request
from RECIPES.users.register import register_bp
from RECIPES.users.login import login_bp
from RECIPES.users.register import RegistrationForm
from RECIPES.users.login import LoginForm
from RECIPES.users.work_db_users import get_db_connection, get_categories_by_parent, get_category_by_id, get_all_categories_with_hierarchy, init_users_table
from RECIPES.categories.objects import objects_bp
from RECIPES.categories.delete_objects import delete_objects_bp
from RECIPES.categories.edit_objects import edit_objects_bp
from RECIPES.users.my_contribution import my_contribution_bp
from RECIPES.admin.admin import admin_bp
from RECIPES.categories.object_movement import object_movement_bp
from RECIPES.categories.objects_visibility import visibility_bp
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='RECIPES/templates', static_folder='RECIPES/static')
app.secret_key = os.getenv('SECRET_KEY')

# Регистрируем блюпринты
app.register_blueprint(register_bp, url_prefix='/')
app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(objects_bp, url_prefix='/')
app.register_blueprint(edit_objects_bp, url_prefix='/')
app.register_blueprint(delete_objects_bp, url_prefix='/')
app.register_blueprint(my_contribution_bp, url_prefix='/')
app.register_blueprint(admin_bp, url_prefix='/')
app.register_blueprint(object_movement_bp, url_prefix='/')
app.register_blueprint(visibility_bp, url_prefix='/')

@app.template_global('get_categories_by_parent')
def get_categories_by_parent_global(parent_id):
    return get_categories_by_parent(parent_id)

@app.template_global('get_category_by_id')
def get_category_by_id_global(category_id):
    return get_category_by_id(category_id)

# Главная страница — startpage.html
@app.route("/", methods=['GET'])
def index():
    conn = get_db_connection()
    with conn:
        # Получаем все категории с иерархией
        all_categories = get_all_categories_with_hierarchy()

        # --- Поиск по категориям ---
        search_category = request.args.get('search_category', '').strip().lower()
        filtered_categories = []

        if search_category:
            # Рекурсивная функция для фильтрации дерева категорий
            def filter_category_tree(categories):
                result = []
                for cat in categories:
                    # Проверяем, подходит ли текущая категория
                    matches = search_category in cat['name'].lower()
                    # Рекурсивно фильтруем дочерние категории
                    children = filter_category_tree(cat.get('children', []))
                    # Если категория подходит ИЛИ у неё есть подходящие потомки — сохраняем
                    if matches or children:
                        cat_copy = cat.copy()
                        cat_copy['children'] = children
                        result.append(cat_copy)
                return result

            filtered_categories = filter_category_tree(all_categories)
        else:
            filtered_categories = all_categories

        # --- Поиск по объектам ---
        search_object = request.args.get('search_object', '').strip()
        search_results_objects = []

        if search_object:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.name, o.created_at, c.name AS category_name
                FROM objects o
                JOIN categories c ON o.category_id = c.id
                WHERE o.name LIKE ?
                ORDER BY o.created_at DESC
            """, ('%' + search_object + '%',))
            search_results_objects = [
                {
                    'id': row[0],
                    'name': row[1],
                    'created_at': row[2],
                    'category_name': row[3]
                }
                for row in cursor.fetchall()
            ]

        return render_template(
            "startpage.html",
            categories=filtered_categories,
            search_results_objects=search_results_objects
        )

# Обработка создания категории
@app.route("/create_category", methods=['POST'])
def create_category():
    if 'user_id' not in session:
        flash('You must be logged in to create a category.')
        return redirect(url_for('index'))

    category_name = request.form.get('category_name', '').strip()
    if not category_name:
        flash('Category name cannot be empty.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    with conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name, created_by) VALUES (?, ?)", (category_name, session['user_id']))
            flash(f'Category "{category_name}" created successfully!')
        except sqlite3.IntegrityError:
            flash(f'Category "{category_name}" already exists.')
        return redirect(url_for('index'))
    
@app.template_filter('format_datetime')
def format_datetime(value, fmt='%d.%m.%Y'):
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
        return dt.strftime(fmt)
    elif isinstance(value, datetime):
        return value.strftime(fmt)
    return ''

if __name__ == "__main__":
    from RECIPES.users.work_db_users import init_users_table
    init_users_table()
    app.run(host="0.0.0.0", port=5000)