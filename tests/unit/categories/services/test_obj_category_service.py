import pytest
from unittest.mock import MagicMock
from RECIPES.categories.services.obj_category_service import (
    create_category, create_subcat, edit_category_service,
    delete_category_service, CategoryRepository
)

class TestCommonSetup:
    """Базовый класс для общих моков"""

    def setup_method(self, method):
        # Создаем общие моки для тестов
        self.mock_repo = MagicMock(spec=CategoryRepository)
        self.mock_validate_not_empty = MagicMock()
        self.mock_validate_exists = MagicMock()
        self.mock_ownership = MagicMock()

    def patch_module(self, mocker):
        return mocker.patch.multiple(
            'RECIPES.categories.services.obj_category_service',
            validate_not_empty=self.mock_validate_not_empty,
            validate_object_exists=self.mock_validate_exists,
            check_category_ownership=self.mock_ownership,
            CategoryRepository=self.mock_repo
        )

class TestCreateCategory(TestCommonSetup):
    def test_create_category_success(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.check_parent_exists.return_value = True
        self.mock_repo.create.return_value = {'id': 1, 'name': 'New'}

        result = create_category("New", 1)
        assert result == {'id': 1, 'name': 'New'}
        self.mock_repo.create.assert_called_once_with("New", 1, None)
        self.mock_validate_not_empty.assert_called_once_with("New", "Имя категории")

    def test_create_category_fail_no_parent(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.check_parent_exists.return_value = False

        with pytest.raises(ValueError, match="Родительская категория не найдена"):
            create_category("New", 1, parent_id=99)
        self.mock_repo.check_parent_exists.assert_called_once_with(99)

class TestCreateSubcategory(TestCommonSetup):
    def test_create_subcat_success(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.check_parent_exists.return_value = True
        self.mock_repo.check_subcategory_exists.return_value = False
        self.mock_repo.create.return_value = {'id': 2, 'name': 'SubNew'}

        result = create_subcat("SubNew", 1, 1)
        assert result == {'id': 2, 'name': 'SubNew'}
        self.mock_repo.create.assert_called_once_with("SubNew", 1, 1)

    def test_create_subcat_fail_no_parent(self, mocker):
        self.patch_module(mocker)
        with pytest.raises(ValueError, match="Не указан родительский идентификатор категории"):
            create_subcat("SubNew", 1, None)

    def test_create_subcat_fail_parent_not_exists(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.check_parent_exists.return_value = False
        with pytest.raises(ValueError, match="Родительская категория не найдена"):
            create_subcat("SubNew", 1, 99)

    def test_create_subcat_fail_exists(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.check_parent_exists.return_value = True
        self.mock_repo.check_subcategory_exists.return_value = True
        with pytest.raises(ValueError, match="Подкатегория с таким именем уже существует"):
            create_subcat("Existing", 1, 1)

class TestEditCategory(TestCommonSetup):
    def test_edit_category_success(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.get_owner_check.return_value = {'id': 1}
        self.mock_ownership.return_value = True

        edit_category_service(1, "Updated", 1)
        self.mock_repo.update.assert_called_once_with("Updated", 1)

    def test_edit_category_fail_no_permission(self, mocker):
        self.patch_module(mocker)
        self.mock_repo.get_owner_check.return_value = {'id': 2}
        self.mock_ownership.return_value = False

        with pytest.raises(ValueError, match="У вас нет прав на редактирование"):
            edit_category_service(1, "Updated", 1)

class TestDeleteCategory:
    def test_delete_category_admin_success(self, mocker):
        # Настройка моков
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = (True,)  # Админ права
        mock_conn.cursor.return_value = mock_cursor

        # Патчинг без контекстных менеджеров
        mocker.patch(
            'RECIPES.categories.services.obj_category_service.get_db_connection',
            return_value=mock_conn
        )

        mock_repo = mocker.patch(
            'RECIPES.categories.services.obj_category_service.CategoryRepository'
        )
        mock_repo.get_by_id.return_value = {'id': 1, 'name': 'Test'}

        # Выполнение
        delete_category_service(1, 1)

        # Проверки
        mock_repo.delete.assert_called_once_with(1)
        mock_conn.close.assert_called_once()

    def test_delete_category_admin_fail(self, mocker):
        # Настройка моков
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = (False,)  # Нет админ прав
        mock_conn.cursor.return_value = mock_cursor

        # Патчинг без контекстных менеджеров
        mocker.patch(
            'RECIPES.categories.services.obj_category_service.get_db_connection',
            return_value=mock_conn
        )

        # Выполнение и проверка исключения
        with pytest.raises(ValueError, match="Только администратор может удалять"):
            delete_category_service(1, 1)

        mock_conn.close.assert_called_once()
