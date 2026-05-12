# RECIPES/categories/delete_objects.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from RECIPES.users.work_db_users import get_db_connection, get_objects_by_category_id, get_ingredients_by_object_id, get_comments_by_object_id, insert_object, insert_ingredient, insert_comment

delete_objects_bp = Blueprint('delete_objects', __name__)

@delete_objects_bp.route('/object/<int:object_id>/delete', methods=['POST'])
def delete_object(object_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для удаления объекта.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        obj = conn.execute("""
            SELECT created_by, category_id, u.is_admin
            FROM objects o
            JOIN users u ON o.created_by = u.id
            WHERE o.id = ?
        """, (object_id,)).fetchone()

        if not obj:
            flash("Объект не найден.")
            return redirect(url_for('index'))

        # Разрешаем удаление: если это свой объект ИЛИ пользователь — админ
        if obj['created_by'] != session['user_id'] and not session.get('is_admin'):
            flash("Вы можете удалять только свои объекты.")
            return redirect(url_for('objects.category_page', category_id=obj['category_id']))

        # Удаляем зависимости
        conn.execute("DELETE FROM ingredients WHERE object_id = ?", (object_id,))
        conn.execute("DELETE FROM comments WHERE object_id = ?", (object_id,))
        conn.execute("DELETE FROM objects WHERE id = ?", (object_id,))

        flash("Объект и его ингредиенты/комментарии удалены.")
        return redirect(url_for('objects.category_page', category_id=obj['category_id']))



# ================================================
# ✅ ДОБАВЛЕНО: УДАЛЕНИЕ КОММЕНТАРИЯ
# ================================================
@delete_objects_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для удаления комментария.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        comment = conn.execute("""
            SELECT c.user_id, c.object_id, u.is_admin
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        """, (comment_id,)).fetchone()

        if not comment:
            flash("Комментарий не найден.")
            return redirect(url_for('index'))

        # Разрешаем удаление: если это свой комментарий ИЛИ админ
        if comment['user_id'] != session['user_id'] and not session.get('is_admin'):
            flash("Вы можете удалять только свои комментарии.")
            return redirect(url_for('objects.category_page', category_id=comment['object_id']))

        conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        flash("Комментарий удалён.")

        return redirect(url_for('objects.category_page', category_id=comment['object_id']))


# ================================================
# ✅ ДОБАВЛЕНО: УДАЛЕНИЕ КАТЕГОРИИ
# ================================================
@delete_objects_bp.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    if 'user_id' not in session:
        flash('Вы должны быть авторизованы для удаления категории.')
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    with conn:
        category = conn.execute("""
            SELECT c.created_by, u.is_admin, c.parent_id
            FROM categories c
            JOIN users u ON c.created_by = u.id
            WHERE c.id = ?
        """, (category_id,)).fetchone()

        if not category:
            flash("Категория не найдена.")
            return redirect(url_for('index'))

        # Проверка прав: только создатель или админ
        if category['created_by'] != session['user_id'] and not session.get('is_admin'):
            flash("Вы можете удалять только свои категории.")
            return redirect(url_for('index'))

        # Удаляем категорию — CASCADE автоматически удалит подкатегории и связанные объекты
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        flash("Категория и все её подкатегории/объекты удалены.")
        return redirect(url_for('index'))
