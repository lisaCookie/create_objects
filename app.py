# app.py

from flask import Flask, render_template, session, redirect, url_for, flash, request, g # Добавили g
from RECIPES.users.register import register_bp
from RECIPES.users.login import login_bp
from RECIPES.database.db_init import get_db_connection # Это ваш файл с подключением
from RECIPES.categories.services.obj_category_service import get_categories_by_parent, get_category_by_id, get_all_categories_with_hierarchy
from RECIPES.categories.objects import objects_bp
from RECIPES.categories.delete_objects import delete_objects_bp
from RECIPES.categories.edit_objects import edit_objects_bp
from RECIPES.users.my_contribution import my_contribution_bp
from RECIPES.admin.admin import admin_bp
from RECIPES.categories.object_movement import object_movement_bp
from RECIPES.categories.objects_visibility import visibility_bp
from RECIPES.utils.filters import filter_categories_by_search, search_objects_in_db
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime
from time import sleep

load_dotenv()

app = Flask(__name__, template_folder='RECIPES/templates', static_folder='RECIPES/static')
app.secret_key = os.getenv('SECRET_KEY')


@app.before_request
def before_request():
    """Открывает соединение перед каждым запросом и кладет его в g.db"""
    g.db = get_db_connection()

@app.teardown_appcontext
def teardown_db(exception):
    """Закрывает соединение после завершения запроса"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- [КОНЕЦ НОВОГО БЛОКА] ---

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

# Глобальные шаблонные функции
@app.template_global('get_categories_by_parent')
def get_categories_by_parent_global(parent_id):
    return get_categories_by_parent(parent_id)

@app.template_global('get_category_by_id')
def get_category_by_id_global(category_id):
    return get_category_by_id(category_id)

# Главная страница
@app.route("/", methods=['GET'])
def index():
    # Теперь не нужно conn = get_db_connection(), берем из g.db
    conn = g.db
   
    # Получаем все категории с иерархией
    all_categories = get_all_categories_with_hierarchy()

    # --- Поиск по категориям ---
    search_category = request.args.get('search_category', '').strip().lower()
    filtered_categories = filter_categories_by_search(all_categories, search_category)

    # --- Поиск по объектам ---
    search_object = request.args.get('search_object', '').strip()
    search_results_objects = search_objects_in_db(conn, search_object)

    return render_template(
        "startpage.html",
        categories=filtered_categories,
        search_results_objects=search_results_objects
    )

# Обработка создания категории
@app.route("/create_category", methods=['POST'])
def create_category():
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для создания категории.')
        return redirect(url_for('index'))

    category_name = request.form.get('category_name', '').strip()
    if not category_name:
        flash('Название категории не должно быть пустым.')
        return redirect(url_for('index'))

    conn = g.db # Используем g.db
    try:
        with conn: # Автоматический commit/rollback
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name, created_by) VALUES (%s, %s)", (category_name, session['user_id']))
            flash(f'Категория "{category_name}" создана успешно!')
    except psycopg2.IntegrityError:
        flash(f'Категория "{category_name}" с таким названием уже существует.')
   
    return redirect(url_for('index'))

# Фильтр для даты
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

# Sitemap
@app.route('/sitemap', endpoint='sitemap_lazy')
def sitemap():
    return render_template('sitemap_lazy.html')

if __name__ == "__main__":
    from RECIPES.database.db_init import init_users_table
    try:
        sleep(3)  # Задержка для запуска PostgreSQL
        init_users_table()
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")