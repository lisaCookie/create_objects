# RECIPES/categories/object_movement.py

from flask import Blueprint, jsonify, request, session, render_template
from RECIPES.database.db_init import get_db_connection

object_movement_bp = Blueprint('object_movement', __name__)

# --- AJAX: Поиск объектов по подстроке ---
@object_movement_bp.route('/admin/ajax/search_objects', methods=['GET'])
def ajax_search_objects():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.name, c.name AS category_name
                FROM objects o
                JOIN categories c ON o.category_id = c.id
                WHERE o.name LIKE %s ORDER BY o.name
            """, ('%' + q + '%',))
            results = [
                {'id': row[0], 'name': row[1], 'category_name': row[2]}
                for row in cursor.fetchall()
            ]
            return jsonify(results)
    finally:
        conn.close()

# --- AJAX: Поиск категорий по подстроке ---
@object_movement_bp.route('/admin/ajax/search_categories', methods=['GET'])
def ajax_search_categories():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name
                FROM categories
                WHERE name LIKE %s ORDER BY name
            """, ('%' + q + '%',))
            results = [
                {'id': row[0], 'name': row[1]}
                for row in cursor.fetchall()
            ]
            return jsonify(results)
    finally:
        conn.close()

# --- Перемещение объекта (POST) ---
@object_movement_bp.route('/admin/move_object', methods=['POST'])
def move_object():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403

    object_id = request.form.get('object_id')
    new_category_id = request.form.get('new_category_id')

    if not object_id or not new_category_id:
        return jsonify({'error': 'ID объекта и ID категории обязательны'}), 400

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Проверяем существование объекта
            cursor.execute("""
                SELECT id, category_id FROM objects WHERE id = %s
            """, (object_id,))
            obj = cursor.fetchone()

            if not obj:
                return jsonify({'error': 'Объект не найден'}), 404

            # Проверяем существование новой категории
            cursor.execute("""
                SELECT id FROM categories WHERE id = %s
            """, (new_category_id,))
            cat = cursor.fetchone()

            if not cat:
                return jsonify({'error': 'Целевая категория не найдена'}), 404

            # Проверяем, не уже ли объект в этой категории
            if obj['category_id'] == int(new_category_id):
                return jsonify({'error': 'Объект уже находится в этой категории'}), 400

            # Выполняем перемещение
            cursor.execute("""
                UPDATE objects SET category_id = %s WHERE id = %s
            """, (new_category_id, object_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Объект успешно перемещен!'})
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()

# --- Главная страница админ-панели ---
@object_movement_bp.route('/admin/dashboard')
def dashboard():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # Получаем пользователей
            cursor.execute("""
                SELECT u.id, u.username, u.is_admin,
                       (SELECT COUNT(*) FROM objects o WHERE o.created_by = u.id) AS objects_count,
                       (SELECT COUNT(*) FROM comments c WHERE c.user_id = u.id) AS comments_count
                FROM users u
            """)
            users = [dict(row) for row in cursor.fetchall()]

            # Получаем категории
            cursor.execute("""
                SELECT c.id, c.name,
                       (SELECT COUNT(*) FROM objects o WHERE o.category_id = c.id) AS objects_count,
                       u.username AS created_by_username
                FROM categories c
                JOIN users u ON c.created_by = u.id
            """)
            categories = [dict(row) for row in cursor.fetchall()]

            # Получаем объекты
            cursor.execute("""
                SELECT o.id, o.name, c.name AS category_name, u.username AS created_by_username, o.created_at
                FROM objects o
                JOIN categories c ON o.category_id = c.id
                JOIN users u ON o.created_by = u.id
            """)
            objects = [dict(row) for row in cursor.fetchall()]

            # Получаем комментарии
            cursor.execute("""
                SELECT c.id, c.text, o.name AS object_name, u.username AS user_name, c.created_at, c.object_id
                FROM comments c
                JOIN objects o ON c.object_id = o.id
                JOIN users u ON c.user_id = u.id
            """)
            comments = [dict(row) for row in cursor.fetchall()]

            # Фильтры
            cursor.execute("SELECT id, username FROM users ORDER BY username")
            all_users_for_filter = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            all_categories_for_filter = [dict(row) for row in cursor.fetchall()]

            cursor.execute("""
                SELECT o.id, o.name, c.name AS category_name
                FROM objects o
                JOIN categories c ON o.category_id = c.id
                ORDER BY o.name
            """)
            all_objects_for_filter = [dict(row) for row in cursor.fetchall()]

            return render_template(
                'admin_dashboard.html',
                users=users,
                categories=categories,
                objects=objects,
                comments=comments,
                all_users_for_filter=all_users_for_filter,
                all_categories_for_filter=all_categories_for_filter,
                all_objects_for_filter=all_objects_for_filter
            )
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        conn.close()
