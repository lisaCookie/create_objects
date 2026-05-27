# RECIPES/categories/services/obj_comment_service.py

from RECIPES.categories.repositories.comment_repository import CommentRepository
from RECIPES.database.db_init import get_db_connection
from RECIPES.categories.services.admin_permission_service import has_admin_access
from RECIPES.categories.validation import validate_not_empty, validate_object_exists, check_comment_ownership


def get_comments_by_object_id(object_id):
    """Возвращает список комментариев по ID объекта."""
    return CommentRepository.get_by_object_id(object_id)

def create_comment(object_id, user_id, text):
    """Создает новый комментарий."""
    validate_not_empty(text, "Текст комментария")
    CommentRepository.create(object_id, user_id, text)

def get_comment_by_id(comment_id):
    """Возвращает комментарий по ID."""
    return CommentRepository.get_by_id(comment_id)

def can_edit(user_id, owner_id):
    """Проверяет, может ли пользователь редактировать комментарий"""
    return has_admin_access(user_id) or user_id == owner_id

def edit_comment_service(comment_id, text, user_id):
    """Редактирует комментарий. Админ может редактировать любые комментарии."""
    validate_not_empty(text, "Текст комментария")
    comment = CommentRepository.get_by_id(comment_id)
    validate_object_exists(comment, "Комментарий не найден")

    # Если юзер - автор комментария или админ, разрешаем редактирование
    if not (has_admin_access(user_id) or user_id == comment['user_id']):
        raise ValueError("Вы не можете редактировать этот комментарий")

    CommentRepository.update(comment_id, text)
    

def delete_comment_service(comment_id, user_id):
    dependencies = CommentRepository.get_dependencies(comment_id)
    validate_object_exists(dependencies, "Комментарий не найден")

    if dependencies['user_id'] != user_id and not has_admin_access(user_id):
        raise ValueError("Вы можете удалять только свои комментарии")

    CommentRepository.delete(comment_id)
