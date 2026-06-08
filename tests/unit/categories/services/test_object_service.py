import pytest
from RECIPES.categories.services.object_service import delete_obj, edit_obj

class TestObjectService:
    @pytest.fixture
    def mocks(self, mocker):
        self.mock_repo = mocker.patch('RECIPES.categories.services.object_service.ObjectRepository')
        self.mock_admin = mocker.patch('RECIPES.categories.services.object_service.has_admin_access')
        self.mock_val_exists = mocker.patch('RECIPES.categories.services.object_service.validate_object_exists')
        self.mock_val_not_empty = mocker.patch('RECIPES.categories.services.object_service.validate_not_empty')

    def test_delete_obj_success_as_owner(self, mocks):
        self.mock_repo.get_dependencies.return_value = {'created_by': 1}
        self.mock_admin.return_value = False
        delete_obj(10, 1)
        self.mock_repo.delete.assert_called_once_with(10)

    def test_delete_obj_fail_not_owner(self, mocks):
        self.mock_repo.get_dependencies.return_value = {'created_by': 1}
        self.mock_admin.return_value = False
        with pytest.raises(ValueError, match="Вы можете удалять только свои объекты"):
            delete_obj(10, 2)

    def test_edit_obj_success(self, mocks):
        self.mock_repo.get_dependencies.return_value = {'created_by': 1}
        self.mock_admin.return_value = False
        self.mock_repo.get_by_name.return_value = None # Name unique
        
        edit_obj(10, "New", "Desc", "Tech", [], 1)
        
        self.mock_repo.update.assert_called()
        self.mock_repo.clear_ingredients.assert_called_with(10)
        self.mock_repo.add_ingredients.assert_called()

    def test_edit_obj_duplicate_name(self, mocks):
        self.mock_repo.get_dependencies.return_value = {'created_by': 1}
        self.mock_admin.return_value = False
        self.mock_repo.get_by_name.return_value = True # Simulate duplicate
        
        with pytest.raises(ValueError, match="Объект с таким именем уже существует"):
            edit_obj(10, "Duplicate", "D", "T", [], 1)