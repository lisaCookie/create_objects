# RECIPES/categories/objects.py
from flask import jsonify  
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from RECIPES.users.work_db_users import get_db_connection, get_all_categories_with_hierarchy, get_objects_by_category_id, get_ingredients_by_object_id, insert_category, get_comments_by_object_id, insert_object, insert_ingredient, insert_comment

objects_bp = Blueprint('objects', __name__)


@objects_bp.route('/category/<int:category_id>')
def category_page(category_id):
    conn = get_db_connection()
    with conn:
        category = conn.execute("""
            SELECT c.id, c.name, c.parent_id, c.created_by, u.username AS created_by_username
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,)).fetchone()
        if not category:
            flash("Category not found.")
            return redirect(url_for('index'))
        category = dict(category)
        objects = get_objects_by_category_id(category_id, user_id=session.get('user_id')) 
        objects_with_ingredients = []
        for obj in objects:
            obj_dict = dict(obj)
            ingredients = get_ingredients_by_object_id(obj['id'])
            comments = get_comments_by_object_id(obj['id'])
            objects_with_ingredients.append({
                'object': obj,
                'ingredients': ingredients,
                'comments': comments
            })
    return render_template('categorypage.html', category=category, objects_with_ingredients=objects_with_ingredients)


@objects_bp.route('/category/<int:category_id>/create_object', methods=['POST'])
def create_object(category_id):
    if 'user_id' not in session:
        flash('You must be logged in to create an object.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    name = request.form.get('object_name', '').strip()
    description = request.form.get('object_description', '').strip()

    if not name:
        flash('Object name cannot be empty.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    # Insert object
    object_id = insert_object(name, description, category_id, session['user_id'])

    # Process ingredients
    ingredient_names = request.form.getlist('ingredient_name[]')
    ingredient_amounts = request.form.getlist('ingredient_amount[]')

    ingredient_units = request.form.getlist('ingredient_unit[]') #new

    for i in range(len(ingredient_names)):
        name = ingredient_names[i].strip()
        amount = ingredient_amounts[i].strip()
        unit = ingredient_units[i] if i < len(ingredient_units) else 'ml'
        if name and amount and amount.isdigit() and int(amount) >= 0:
            insert_ingredient(object_id, name, int(amount), unit)

    flash('Object created successfully!')
    return redirect(url_for('objects.category_page', category_id=category_id))


@objects_bp.route('/object/<int:object_id>/add_comment', methods=['POST'])
def add_comment(object_id):
    if 'user_id' not in session:
        flash('You must be logged in to add a comment.')
        return redirect(url_for('login.login'))

    text = request.form.get('comment_text', '').strip()
    if not text:
        flash('Comment cannot be empty.')
        return redirect(url_for('objects.category_page', category_id=object_id))

    insert_comment(object_id, session['user_id'], text)
    flash('Comment added successfully!')

    # Find the category of this object to redirect back
    conn = get_db_connection()
    with conn:
        category_id = conn.execute("""
            SELECT c.id FROM categories c
            JOIN objects o ON o.category_id = c.id
            WHERE o.id = ?
        """, (object_id,)).fetchone()['id']

    return redirect(url_for('objects.category_page', category_id=category_id))


@objects_bp.route('/category/<int:category_id>/create_category', methods=['POST'])
def create_subcategory(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для создания категории.')
        return redirect(url_for('login.login'))

    name = request.form.get('category_name', '').strip()
    if not name:
        flash('Название категории не может быть пустым.')
        return redirect(url_for('objects.category_page', category_id=category_id))

    # Создаём подкатегорию в указанной категории
    subcategory_id = insert_category(name, session['user_id'], parent_id=category_id)
    flash(f'Подкатегория "{name}" создана!')
    return redirect(url_for('objects.category_page', category_id=category_id))


@objects_bp.route('/object/<int:object_id>')
def object_detail(object_id):
    conn = get_db_connection()
    with conn:
        # Получаем объект с учетом видимости
        obj = conn.execute("""
            SELECT o.id, o.name, o.description, o.created_at, c.name AS category_name, o.visible_to_guests
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            WHERE o.id = ?
        """, (object_id,)).fetchone()

        # Если объект не найден ИЛИ объект скрыт для гостей И пользователь не авторизован
        if not obj or (obj['visible_to_guests'] == 0 and 'user_id' not in session):
            flash("Объект не найден или недоступен.")
            return redirect(url_for('index'))

        obj = dict(obj)

        # Получаем ингредиенты
        ingredients = conn.execute("""
            SELECT name, amount, unit FROM ingredients WHERE object_id = ?
        """, (object_id,)).fetchall()
        ingredients = [dict(row) for row in ingredients]

        # Получаем комментарии с именами пользователей
        comments = conn.execute("""
            SELECT co.text, co.created_at, u.username
            FROM comments co
            JOIN users u ON co.user_id = u.id
            WHERE co.object_id = ?
            ORDER BY co.created_at DESC
        """, (object_id,)).fetchall()
        comments = [dict(row) for row in comments]

        return render_template('object_detail.html', object=obj, ingredients=ingredients, comments=comments)
    

@objects_bp.route('/sitemap')
def sitemap():
    conn = get_db_connection()
    with conn:
        # Получаем только корневые категории (parent_id IS NULL)
        root_categories = conn.execute("""
            SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.parent_id IS NULL
            ORDER BY c.name
        """).fetchall()

        # Преобразуем в список словарей
        root_categories = [dict(row) for row in root_categories]

        return render_template('sitemap_lazy.html', root_categories=root_categories)


@objects_bp.route('/sitemap/children/<int:category_id>')
def sitemap_children(category_id):
    conn = get_db_connection()
    with conn:
        # Получаем подкатегории (всегда видны, если есть — они не зависят от visible_to_guests)
        children = conn.execute("""
            SELECT c.id, c.name, c.parent_id, u.username AS created_by_username
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.parent_id = ?
            ORDER BY c.name
        """, (category_id,)).fetchall()

        # Получаем объекты — с фильтрацией по видимости для гостей
        if 'user_id' in session:
            # Авторизованный пользователь: видит ВСЕ объекты в категории
            objects = conn.execute("""
                SELECT o.id, o.name, o.visible_to_guests
                FROM objects o
                WHERE o.category_id = ?
                ORDER BY o.name
            """, (category_id,)).fetchall()
        else:
            # Гость: видит ТОЛЬКО объекты, видимые для всех
            objects = conn.execute("""
                SELECT o.id, o.name, o.visible_to_guests
                FROM objects o
                WHERE o.category_id = ? AND o.visible_to_guests = 1
                ORDER BY o.name
            """, (category_id,)).fetchall()

        # Преобразуем в списки словарей
        children = [dict(row) for row in children]
        objects = [dict(row) for row in objects]

        return jsonify({
            'children': children,
            'objects': objects
        })


@objects_bp.route('/category/<int:category_id>/detail', methods=['GET'])
def category_detail(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования категории.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        category = conn.execute("""
            SELECT c.id, c.name, c.created_by, u.username AS created_by_username
            FROM categories c
            LEFT JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,)).fetchone()

        if not category:
            flash("Категория не найдена.")
            return redirect(url_for('index'))

        category = dict(category)

        user_id = session['user_id']
        owner_id = category['created_by']

        # Проверка: может ли пользователь редактировать?
        is_admin = conn.execute(
            "SELECT is_admin FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        if user_id != owner_id and (not is_admin or not is_admin['is_admin']):
            flash("Вы не можете редактировать эту категорию.")
            return redirect(url_for('objects.category_page', category_id=category_id))

        # ✅ Если прошли проверку — показываем форму редактирования
        return render_template('category_detail.html', category=category)
