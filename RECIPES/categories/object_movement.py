# RECIPES/admin/object_movement.py

from flask import Blueprint, jsonify, request, session, flash, redirect, url_for
from RECIPES.users.work_db_users import get_db_connection, get_objects_by_category_id, get_category_by_id, get_all_categories_with_hierarchy

object_movement_bp = Blueprint('object_movement', __name__)


# --- AJAX: Поиск объектов по подстроке ---
@object_movement_bp.route('/admin/ajax/search_objects', methods=['GET'])
def ajax_search_objects():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.name, c.name AS category_name
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            WHERE o.name LIKE ? ORDER BY o.name
        """, ('%' + q + '%',))
        results = [
            {
                'id': row[0],
                'name': row[1],
                'category_name': row[2]
            }
            for row in cursor.fetchall()
        ]
        return jsonify(results)


# --- AJAX: Поиск категорий по подстроке ---
@object_movement_bp.route('/admin/ajax/search_categories', methods=['GET'])
def ajax_search_categories():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    conn = get_db_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name
            FROM categories
            WHERE name LIKE ? ORDER BY name
        """, ('%' + q + '%',))
        results = [
            {
                'id': row[0],
                'name': row[1]
            }
            for row in cursor.fetchall()
        ]
        return jsonify(results)


# --- Перемещение объекта (POST) ---
@object_movement_bp.route('/admin/move_object', methods=['POST'])
def move_object():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403

    object_id = request.form.get('object_id')
    new_category_id = request.form.get('new_category_id')

    if not object_id or not new_category_id:
        return jsonify({'error': 'Object ID and category ID are required'}), 400

    conn = get_db_connection()
    with conn:
        # Проверяем существование объекта
        obj = conn.execute("SELECT id, category_id FROM objects WHERE id = ?", (object_id,)).fetchone()
        if not obj:
            return jsonify({'error': 'Object not found'}), 404

        # Проверяем существование новой категории
        cat = conn.execute("SELECT id FROM categories WHERE id = ?", (new_category_id,)).fetchone()
        if not cat:
            return jsonify({'error': 'Target category not found'}), 404

        # Проверяем, не уже ли объект в этой категории
        if obj['category_id'] == int(new_category_id):
            return jsonify({'error': 'Object is already in this category'}), 400

        # Выполняем перемещение
        conn.execute("UPDATE objects SET category_id = ? WHERE id = ?", (new_category_id, object_id))
        conn.commit()

        return jsonify({'success': True, 'message': 'Object moved successfully!'})


# --- Главная страница админ-панели с формой перемещения ---
@object_movement_bp.route('/admin/dashboard')
def dashboard():
    # Получаем данные для фильтров (уже есть в admin.py — просто передаём)
    conn = get_db_connection()
    with conn:
        users = conn.execute("""
            SELECT u.id, u.username, u.is_admin,
                   (SELECT COUNT(*) FROM objects o WHERE o.created_by = u.id) AS objects_count,
                   (SELECT COUNT(*) FROM comments c WHERE c.user_id = u.id) AS comments_count
            FROM users u
        """).fetchall()

        categories = conn.execute("""
            SELECT c.id, c.name,
                   (SELECT COUNT(*) FROM objects o WHERE o.category_id = c.id) AS objects_count,
                   u.username AS created_by_username
            FROM categories c
            JOIN users u ON c.created_by = u.id
        """).fetchall()

        objects = conn.execute("""
            SELECT o.id, o.name, c.name AS category_name, u.username AS created_by_username, o.created_at
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            JOIN users u ON o.created_by = u.id
        """).fetchall()

        comments = conn.execute("""
            SELECT c.id, c.text, o.name AS object_name, u.username AS user_name, c.created_at, c.object_id
            FROM comments c
            JOIN objects o ON c.object_id = o.id
            JOIN users u ON c.user_id = u.id
        """).fetchall()

        # Для фильтров
        all_users_for_filter = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
        all_categories_for_filter = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        all_objects_for_filter = conn.execute("""
            SELECT o.id, o.name, c.name AS category_name
            FROM objects o
            JOIN categories c ON o.category_id = c.id
            ORDER BY o.name
        """).fetchall()

    return render_template(
        'admin_dashboard.html',
        users=[dict(row) for row in users],
        categories=[dict(row) for row in categories],
        objects=[dict(row) for row in objects],
        comments=[dict(row) for row in comments],
        all_users_for_filter=[dict(row) for row in all_users_for_filter],
        all_categories_for_filter=[dict(row) for row in all_categories_for_filter],
        all_objects_for_filter=[dict(row) for row in all_objects_for_filter]
    )
