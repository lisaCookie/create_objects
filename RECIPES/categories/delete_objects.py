# RECIPES/categories/delete_objects.py

from flask import Blueprint, redirect, url_for, flash, session
from RECIPES.categories.services.object_service import get_object_by_id, delete_obj
from RECIPES.categories.services.obj_category_service import delete_category_service
from RECIPES.categories.services.obj_comment_service import delete_comment_service, get_comment_by_id
from RECIPES.categories.validation import check_authentication, validate_object_exists


delete_objects_bp = Blueprint('delete_objects', __name__)

@delete_objects_bp.route('/object/<int:object_id>/delete', methods=['POST'])
def delete_object(object_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для удаления объекта.')
        return redirect(url_for('login.login'))

    obj = get_object_by_id(object_id, user_id=session['user_id'])
    validate_object_exists(obj, 'Объект не найден.')

    try:
        delete_obj(object_id, session['user_id'])
        flash("Объект и его ингредиенты/комментарии удалены.")
        return redirect(url_for('objects.category_page', category_id=obj['category_id']))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('objects.category_page', category_id=obj['category_id']))
    

@delete_objects_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для удаления комментария.')
        return redirect(url_for('login.login'))

    try:
        delete_comment_service(comment_id, session['user_id'])
        flash("Комментарий удалён.")
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

    comment = get_comment_by_id(comment_id)
    if comment:
        return redirect(url_for('objects.category_page', category_id=comment['object_id']))
    return redirect(url_for('index'))


@delete_objects_bp.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    if not check_authentication():
        flash('Вы должны быть авторизованы для удаления категории.')
        return redirect(url_for('login.login'))

    try:
        delete_category_service(category_id, session['user_id'])
        flash("Категория и все её подкатегории/объекты удалены.")
        return redirect(url_for('index'))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))
