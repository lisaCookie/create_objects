import pytest
from RECIPES.categories.repositories.category_repository import CategoryRepository

class TestCategoryRepository:
    @pytest.fixture
    def mock_db(self, mocker):
        mock_conn = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch('RECIPES.categories.repositories.category_repository.get_db_connection', return_value=mock_conn)
        return mock_conn, mock_cursor

    def test_get_by_id(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = {'id': 1, 'name': 'Test'}
        assert CategoryRepository.get_by_id(1) == {'id': 1, 'name': 'Test'}

    def test_create(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = [10]
        assert CategoryRepository.create("New", 1) == 10

    def test_check_parent_exists(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = (1,)
        assert CategoryRepository.check_parent_exists(1) is True
        cursor.fetchone.return_value = None
        assert CategoryRepository.check_parent_exists(2) is False

    def test_check_subcategory_exists(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = (1,)
        assert CategoryRepository.check_subcategory_exists("Sub", 1) is True

    def test_get_all_with_hierarchy(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'id': 1, 'name': 'Root'}]
        assert len(CategoryRepository.get_all_with_hierarchy()) == 1

    def test_get_by_parent(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'id': 2, 'name': 'Child'}]
        assert len(CategoryRepository.get_by_parent(1)) == 1

    def test_get_owner_check_is_owner(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.side_effect = [
            {'id': 1, 'created_by': 10, 'username': 'user'}, # Category
            {'is_admin': False}                             # User
        ]
        res = CategoryRepository.get_owner_check(1, 10)
        assert res['can_edit'] is True

    def test_update(self, mock_db):
        _, cursor = mock_db
        CategoryRepository.update("New Name", 1)
        cursor.execute.assert_called()

    def test_delete_success(self, mock_db):
        _, cursor = mock_db
        CategoryRepository.delete(1)
        cursor.execute.assert_called()

    def test_delete_error(self, mock_db):
        _, cursor = mock_db
        cursor.execute.side_effect = Exception("Error")
        with pytest.raises(ValueError, match="Ошибка при удалении"):
            CategoryRepository.delete(1)