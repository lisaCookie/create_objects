# RECIPES/objects_visibility.py
from flask import Blueprint, request, session, redirect, url_for, flash
from RECIPES.database.db_init import get_db_connection

visibility_bp = Blueprint('visibility', __name__)

@visibility_bp.route('/object/<int:object_id>/toggle_visibility', methods=['POST'])
def toggle_visibility(object_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для изменения видимости объекта.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # Проверяем существование объекта и владельца
            cursor.execute("""
                SELECT id, created_by FROM objects WHERE id = %s
            """, (object_id,))
            obj = cursor.fetchone()

            if not obj:
                flash("Объект не найден.")
                return redirect(url_for('index'))

            if obj['created_by'] != session['user_id']:
                flash("Вы не можете изменять видимость чужих объектов.")
                return redirect(url_for('objects.category_page', category_id=obj['category_id']))

            # Получаем текущую видимость (да/нет)
            cursor.execute("""
                SELECT visible_to_guests FROM objects WHERE id = %s
            """, (object_id,))
            current_visibility = cursor.fetchone()['visible_to_guests']

            # Меняем статус на противоположный
            new_visibility = 1 if current_visibility == 0 else 0  # Или int(not current_visibility)
            cursor.execute("""
                UPDATE objects
                SET visible_to_guests = %s
                WHERE id = %s
            """, (new_visibility, object_id))

            flash(f"Видимость объекта {'включена для всех' if new_visibility else 'отключена для гостей'}.")
            return redirect(request.referrer or url_for('objects.category_page', category_id=obj['category_id']))
    except Exception as e:
        flash(f'Ошибка при изменении видимости: {str(e)}')
        return redirect(url_for('index'))
    finally:
        conn.close()