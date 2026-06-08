# RECIPES/categories/edit_objects.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from RECIPES.categories.services.object_service import edit_obj, get_object_by_id
from RECIPES.categories.services.obj_category_service import  edit_category_service, get_category_detail_owner_check, get_category_by_id
from RECIPES.categories.services.obj_comment_service import edit_comment_service, get_comment_by_id, can_edit
from RECIPES.categories.services.obj_ingredient_service import parse_ingredients_for_object, get_ingredients_by_object_id
from RECIPES.categories.validation import check_authentication, validate_object_exists, validate_not_empty


edit_objects_bp = Blueprint('edit_objects', __name__)

@edit_objects_bp.route('/object/<int:object_id>/edit', methods=['GET', 'POST'])
def edit_object(object_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    obj = get_object_by_id(object_id, user_id=session['user_id'])
    validate_object_exists(obj, 'Объект не найден.')

    try:
        if request.method == 'POST':
            object_name = request.form.get('object_name', '').strip()
            description = request.form.get('object_description', '').strip()
            technology = request.form.get('object_technology', '').strip()

            validate_not_empty(object_name, 'Название объекта')

            ingredient_names = request.form.getlist('ingredient_name[]')
            ingredient_amounts = request.form.getlist('ingredient_amount[]')
            ingredient_units = request.form.getlist('ingredient_unit[]')
            ingredients = parse_ingredients_for_object(
                ingredient_names,
                ingredient_amounts,
                ingredient_units
            )

            edit_obj(
                object_id=object_id,
                name=object_name,
                description=description,
                technology=technology,
                ingredients=ingredients,
                user_id=session['user_id']
            )
            flash('Объект успешно обновлён!')
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))
        else:
            ingredients = get_ingredients_by_object_id(object_id)
            return render_template(
                'categorypage.html',
                category=obj,
                object_to_edit=obj,
                ingredients=ingredients,
                editing=True
            )
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('edit_objects.edit_object', object_id=object_id))

    
@edit_objects_bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для редактирования комментария.')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        text = request.form.get('comment_text', '').strip()
        try:
            validate_not_empty(text, 'Текст комментария')
            edit_comment_service(comment_id, text, session['user_id'])
            flash('Комментарий успешно обновлён!')
            comment = get_comment_by_id(comment_id)
            # ПРАВИЛЬНО! Передаем object_id, так как комментарий привязан к объекту, а не категории
            return redirect(url_for('objects.object_detail', object_id=comment['object_id']))
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('edit_objects_bp.edit_comment', comment_id=comment_id))

    comment = get_comment_by_id(comment_id)
    validate_object_exists(comment, 'Комментарий не найден.')

    if not can_edit(session['user_id'], comment['user_id']):
        flash("Вы не можете редактировать чужой комментарий.")
        # ТАКЖЕ ИСПРАВЛЯЕМ ЗДЕСЬ (если маршрут ожидает category_id, а не object_id)
        return redirect(url_for('objects.category_page', category_id=comment['object_id']))  # Исправлено

    session['editing_comment'] = {
        'id': comment_id,
        'text': comment['text'],
        'object_id': comment['object_id']
    }
    return render_template('comment_edit.html')



@edit_objects_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    owner_check = get_category_detail_owner_check(category_id, session['user_id'])
    if not owner_check or not owner_check['can_edit']:
        flash('У вас нет прав на редактирование этой категории')
        return redirect(url_for('index'))

    try:
        if request.method == 'POST':
            name = request.form.get('category_name', '').strip()
            validate_not_empty(name, 'Имя категории')

            edit_category_service(category_id, name, session['user_id'])
            flash('Категория успешно обновлена!')
            return redirect(url_for('objects.category_page', category_id=category_id))
        else:
            category = get_category_by_id(category_id)
            return render_template('edit_category.html', category=category, category_id=category_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))