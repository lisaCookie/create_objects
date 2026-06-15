# RECIPES/categories/objects.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from RECIPES.categories.services.object_service import get_objects_by_category_id, create_obj, get_object_by_id
from RECIPES.categories.services.obj_category_service import get_all_categories_with_hierarchy, create_subcat, get_category_by_id, get_category_detail_owner_check
from RECIPES.categories.services.obj_ingredient_service import get_ingredients_by_object_id_rep, insert_ingredients_for_object
from RECIPES.categories.services.obj_comment_service import get_comments_by_object_id, create_comment
from RECIPES.categories.repositories.sitemap_repository import SitemapRepository
from RECIPES.utils.filters import search_objects_in_db, filter_categories_by_search
from flask import g
from RECIPES.database.db_init import get_db_connection



objects_bp = Blueprint('objects', __name__, template_folder='../templates')


# --- Категория: список объектов ---
@objects_bp.route('/category/<int:category_id>')
def category_page(category_id):
    category = get_category_by_id(category_id)
    if not category:
        flash("Category not found.")
        return redirect(url_for('index'))

    objects = get_objects_by_category_id(category_id, session.get('user_id'))
    objects_with_ingredients = []
    for obj in objects:
        ingredients = get_ingredients_by_object_id_rep(obj['id'])
        comments = get_comments_by_object_id(obj['id'])
        objects_with_ingredients.append({
            'object': obj,
            'ingredients': ingredients,
            'comments': comments
        })

    return render_template('categorypage.html', category=category, objects_with_ingredients=objects_with_ingredients)


# --- Создание объекта ---
@objects_bp.route('/category/<int:category_id>/create_object', methods=['POST'])
def create_object(category_id):  # Имя изменено, чтобы не конфликтовать с сервисом!
    if 'user_id' not in session:
        flash('You must be logged in to create an object.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    try:
        object_id = create_obj(
            name=request.form.get('object_name', '').strip(),
            description=request.form.get('object_description', '').strip(),
            category_id=category_id,
            created_by=session['user_id'],
            technology=request.form.get('object_technology', '').strip()
        )
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('objects.category_page', category_id=category_id))
    except Exception:
        flash('Объект с таким названием уже существует.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    # Передаём всё в сервис — он сам разберётся с ингредиентами
    insert_ingredients_for_object(
        object_id=object_id,
        ingredient_names=request.form.getlist('ingredient_name[]'),
        ingredient_amounts=request.form.getlist('ingredient_amount[]'),
        ingredient_units=request.form.getlist('ingredient_unit[]')
    )

    flash('Объект создан успешно!')
    return redirect(url_for('objects.category_page', category_id=category_id))


# --- Добавление комментария ---
@objects_bp.route('/object/<int:object_id>/add_comment', methods=['POST'])
def add_comment(object_id):
    if 'user_id' not in session:
        flash('You must be logged in to add a comment.')
        return redirect(url_for('login.login'))

    text = request.form.get('comment_text', '').strip()
    if not text:
        flash('Comment cannot be empty.')
        return redirect(url_for('objects.object_detail', object_id=object_id))

    create_comment(object_id, session['user_id'], text)
    flash('Comment added successfully!')

    # Редирект на страницу деталей объекта
    return redirect(url_for('objects.object_detail', object_id=object_id))



# --- Создание подкатегории ---
@objects_bp.route('/category/<int:category_id>/create_category', methods=['POST'])
def create_subcategory(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для создания категории.')
        return redirect(url_for('login.login'))

    name = request.form.get('category_name', '').strip()
    if not name:
        flash('Название категории не может быть пустым.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    try:
        create_subcat(name, session['user_id'], category_id)
        flash(f'Подкатегория "{name}" создана!')
    except ValueError as e:
        flash(str(e))
    except Exception:
        flash('Ошибка при создании подкатегории.')

    return redirect(url_for('objects.category_page', category_id=category_id))



# --- Детали объекта ---
@objects_bp.route('/object/<int:object_id>')
def object_detail(object_id):
    obj = get_object_by_id(object_id, session.get('user_id'))
    if not obj:
        flash("Объект не найден или недоступен.")
        return redirect(url_for('index'))

    ingredients = get_ingredients_by_object_id_rep(object_id)
    comments = get_comments_by_object_id(object_id)

    return render_template('object_detail.html', object=obj, ingredients=ingredients, comments=comments, category_id=obj['category_id'])


# --- Sitemap: корневые категории ---
@objects_bp.route('/sitemap')
def sitemap():
    root_categories = SitemapRepository.get_root_categories()
    return render_template('sitemap_lazy.html', root_categories=root_categories)

@objects_bp.route('/sitemap/children/<int:category_id>')
def sitemap_children(category_id):
    children, objects = SitemapRepository.get_children_and_objects(category_id, session.get('user_id'))
    return jsonify({'children': children, 'objects': objects})


# --- Детали категории (редактирование) ---
@objects_bp.route('/category/<int:category_id>/detail', methods=['GET'])
def category_detail(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования категории.')
        return redirect(url_for('login.login'))

    result = get_category_detail_owner_check(category_id, session['user_id'])
    if not result:
        flash("Категория не найдена.")
        return redirect(url_for('index'))

    category = result['category']
    if not result['can_edit']:
        flash("Вы не можете редактировать эту категорию.")
        return redirect(url_for('objects.category_page', category_id=category_id))

    return render_template('category_detail.html', category=category)


@objects_bp.route('/api/search/categories')
def api_search_categories():
    query = request.args.get('q', '').strip()
    # 1. Получаем дерево категорий из сервиса
    all_categories_tree = get_all_categories_with_hierarchy()
    # 2. Фильтруем его
    filtered_tree = filter_categories_by_search(all_categories_tree, query)
   
    # 3. Превращаем дерево в плоский список для JS
    def flatten(nodes):
        flat = []
        for n in nodes:
            flat.append({'id': n['id'], 'name': n['name']})
            if n.get('children'):
                flat.extend(flatten(n['children']))
        return flat

    return jsonify(flatten(filtered_tree))

@objects_bp.route('/api/search/objects')
def api_search_objects():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    # Пытаемся взять соединение из g, если его нет - создаем новое
    conn = getattr(g, 'db', None)
    if conn is None:
        conn = get_db_connection()
   
    try:
        results = search_objects_in_db(conn, query)
        return jsonify(results)
    finally:
        # Если мы создали соединение специально для этого запроса, закрываем его
        if conn not in [getattr(g, 'db', None)]:
            conn.close()