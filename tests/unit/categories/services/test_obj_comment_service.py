import pytest
from RECIPES.categories.services.obj_comment_service import (
    create_comment, edit_comment_service, delete_comment_service
)

class TestObjCommentService:
    @pytest.fixture
    def mocks(self, mocker):
        self.mock_repo = mocker.patch('RECIPES.categories.services.obj_comment_service.CommentRepository')
        self.mock_admin = mocker.patch('RECIPES.categories.services.obj_comment_service.has_admin_access')
        self.mock_val_not_empty = mocker.patch('RECIPES.categories.services.obj_comment_service.validate_not_empty')
        self.mock_val_exists = mocker.patch('RECIPES.categories.services.obj_comment_service.validate_object_exists')

    def test_create_comment_success(self, mocks):
        create_comment(1, 1, "text")
        self.mock_repo.create.assert_called_once()

    def test_edit_comment_fail_not_owner(self, mocks):
        self.mock_repo.get_by_id.return_value = {'user_id': 5} # Owner is 5
        self.mock_admin.return_value = False # Current user is not admin
        self.mock_val_exists.return_value = None

        with pytest.raises(ValueError, match="Вы не можете редактировать этот комментарий"):
            edit_comment_service(1, "new text", 1) # User 1 is not owner

    def test_delete_comment_fail_not_owner(self, mocks):
        self.mock_repo.get_dependencies.return_value = {'user_id': 5}
        self.mock_admin.return_value = False
        self.mock_val_exists.return_value = None

        with pytest.raises(ValueError, match="Вы можете удалять только свои комментарии"):
            delete_comment_service(1, 1) # User 1 is not owner