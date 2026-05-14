# RECIPES/objects_visibility.py
from flask import Blueprint, jsonify, request, session, redirect, url_for, flash
from RECIPES.users.work_db_users import get_db_connection

visibility_bp = Blueprint('visibility', __name__)

@visibility_bp.route('/object/<int:object_id>/toggle_visibility', methods=['POST'])
def toggle_visibility(object_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для изменения видимости объекта.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        # Проверяем, существует ли объект и принадлежит ли он текущему пользователю
        obj = conn.execute("""
            SELECT id, created_by FROM objects WHERE id = ?
        """, (object_id,)).fetchone()

        if not obj:
            flash("Объект не найден.")
            return redirect(url_for('index'))

        if obj['created_by'] != session['user_id']:
            flash("Вы не можете изменять видимость чужих объектов.")
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))

        # Добавляем поле `visible_to_guests` в таблицу objects, если его нет
        # (Это должно быть сделано при инициализации БД — см. ниже)
        current_visibility = conn.execute("""
            SELECT visible_to_guests FROM objects WHERE id = ?
        """, (object_id,)).fetchone()['visible_to_guests']

        new_visibility = not current_visibility

        conn.execute("""
            UPDATE objects SET visible_to_guests = ? WHERE id = ?
        """, (new_visibility, object_id))

        flash(f"Видимость объекта {'включена для всех' if new_visibility else 'отключена для гостей'}.")

    return redirect(request.referrer or url_for('objects.category_page', category_id=obj['category_id']))
