# RECIPES/categories/edit_objects.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from RECIPES.categories.services.object_service import edit_obj, get_object_by_id
from RECIPES.categories.repositories.object_repository import ObjectRepository
from RECIPES.categories.services.obj_category_service import get_all_categories_with_hierarchy, edit_category_service, get_category_detail_owner_check, get_category_by_id
from RECIPES.categories.services.obj_comment_service import edit_comment_service, get_comment_by_id, can_edit 

edit_objects_bp = Blueprint('edit_objects', __name__)


@edit_objects_bp.route('/object/<int:object_id>/edit', methods=['GET', 'POST'])
def edit_object(object_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    obj = get_object_by_id(object_id)
    if not obj:
        flash('Объект не найден.')
        return redirect(url_for('index'))

    try:
        if request.method == 'POST':
            # Сохраняем название объекта в отдельную переменную
            object_name = request.form.get('object_name', '').strip()
            description = request.form.get('object_description', '').strip()
            technology = request.form.get('object_technology', '').strip()

            if not object_name:
                flash('Название объекта не может быть пустым.')
                return redirect(url_for('edit_objects.edit_object', object_id=object_id))

            # Обработка ингредиентов
            ingredients = []
            ingredient_names = request.form.getlist('ingredient_name[]')
            ingredient_amounts = request.form.getlist('ingredient_amount[]')
            ingredient_units = request.form.getlist('ingredient_unit[]')

            for i in range(len(ingredient_names)):
                # Используем новую переменную для имени ингредиента
                ingr_name = ingredient_names[i].strip()
                amount = ingredient_amounts[i].strip()
                unit = ingredient_units[i].strip() if i < len(ingredient_units) else 'ml'

                if ingr_name:
                    ingredients.append((ingr_name, amount, unit))

            # Передаём правильные параметры: object_name вместо name!
            edit_obj(
                object_id=object_id,
                name=object_name,  # Исправлено: передаём сохранившееся название
                description=description,
                technology=technology,
                ingredients=ingredients,
                user_id=session['user_id']
            )
            flash('Объект успешно обновлён!')
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))

        else:  # GET-запрос (отображение формы)
            ingredients = ObjectRepository.get_ingredients(object_id)
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
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования комментария.')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        text = request.form.get('comment_text', '').strip()
        try:
            edit_comment_service(comment_id, text, session['user_id'])
            flash('Комментарий успешно обновлён!')
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('edit_objects.edit_comment', comment_id=comment_id))

        comment = get_comment_by_id(comment_id)
        # Получаем объект после редактирования
        object_id = comment['object_id']
        # Сразу редиректим на страницу категории объекта
        return redirect(url_for('objects.category_page', category_id=object_id, object_id=object_id))

    # Заполнение формы через сессию (для GET-запроса)
    comment = get_comment_by_id(comment_id)
    if not comment:
        flash("Комментарий не найден.")
        return redirect(url_for('index'))

    if not can_edit(session['user_id'], comment['user_id']):
        flash("Вы не можете редактировать чужой комментарий.")
        return redirect(url_for('objects.category_page', category_id=comment['object_id']))

    session['editing_comment'] = {
        'id': comment_id,
        'text': comment['text'],
        'object_id': comment['object_id']
    }
    # Во всех случаях редирект на страцу категории объекта
    return redirect(url_for('objects.category_page', category_id=comment['object_id']))



@edit_objects_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для редактирования.')
        return redirect(url_for('login.login'))

    owner_check = get_category_detail_owner_check(category_id, session['user_id'])
    if not owner_check or not owner_check['can_edit']:
        flash('У вас нет прав на редактирование этой категории')
        return redirect(url_for('index'))

    try:
        if request.method == 'POST':
            name = request.form.get('category_name', '').strip()
            if not name:
                flash('Имя категории не может быть пустым')
                return redirect(url_for('edit_objects.edit_category', category_id=category_id))

            # Вызов исправленной функции
            edit_category_service(category_id, name, session['user_id'])  # ← Теперь это корректно
            flash('Категория успешно обновлена!')
            return redirect(url_for('objects.category_page', category_id=category_id))
        else:  # GET-запрос
            category = get_category_by_id(category_id)
            return render_template('edit_category.html',
                                category=category,
                                category_id=category_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

