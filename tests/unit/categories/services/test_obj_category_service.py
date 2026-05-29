import pytest
from RECIPES.categories.services.obj_category_service import (
    create_category, create_subcat, edit_category_service, delete_category_service
)

class TestObjCategoryService:
    @pytest.fixture
    def mocks(self, mocker):
        self.mock_repo = mocker.patch('RECIPES.categories.services.obj_category_service.CategoryRepository')
        self.mock_admin_svc = mocker.patch('RECIPES.categories.services.obj_category_service.has_admin_access')
        self.mock_val = mocker.patch('RECIPES.categories.services.obj_category_service.validate_not_empty')
        self.mock_val_exists = mocker.patch('RECIPES.categories.services.obj_category_service.validate_object_exists')
        self.mock_ownership = mocker.patch('RECIPES.categories.services.obj_category_service.check_category_ownership')
        # Мы не сохраняем этот мок в self, так как он нужен только для тестов, где идет прямой SQL
        mocker.patch('RECIPES.categories.services.obj_category_service.get_db_connection')

    def test_create_category_success(self, mocks):
        self.mock_repo.check_parent_exists.return_value = True
        create_category("New", 1)
        self.mock_repo.create.assert_called_once()

    def test_create_category_fail_no_parent(self, mocks):
        self.mock_repo.check_parent_exists.return_value = False
        with pytest.raises(ValueError, match="Родительская категория не найдена"):
            create_category("New", 1, parent_id=99)

    def test_edit_category_fail_no_permission(self, mocks):
        self.mock_repo.get_owner_check.return_value = {'id': 1}
        self.mock_ownership.return_value = False
        with pytest.raises(ValueError, match="У вас нет прав на редактирование"):
            edit_category_service(1, "Name", 2)

    def test_delete_category_admin_only(self, mocks, mocker):
        # Добавили 'mocker' в аргументы функции выше ^
        
        # Создаем мок соединения
        mock_conn = mocker.MagicMock()
        # Подменяем функцию подключения, чтобы она возвращала наш мок
        mocker.patch('RECIPES.categories.services.obj_category_service.get_db_connection', return_value=mock_conn)
        
        # Имитируем, что fetchone возвращает (False,), т.е. пользователь не админ
        mock_conn.cursor.return_value.fetchone.return_value = (False,)

        with pytest.raises(ValueError, match="Только администратор может удалять"):
            delete_category_service(1, 1)