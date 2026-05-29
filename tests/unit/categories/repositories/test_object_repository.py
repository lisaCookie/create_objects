import pytest
from RECIPES.categories.repositories.object_repository import ObjectRepository

class TestObjectRepository:
    @pytest.fixture
    def mock_db(self, mocker):
        mock_conn = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch('RECIPES.categories.repositories.object_repository.get_db_connection', return_value=mock_conn)
        return mock_conn, mock_cursor

    def test_get_by_category(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'id': 1, 'name': 'Obj'}]
        assert len(ObjectRepository.get_by_category(1)) == 1

    def test_get_by_id_guest_access(self, mock_db):
        _, cursor = mock_db
        # Object visible to guests (1)
        cursor.fetchone.return_value = {'id': 1, 'visible_to_guests': 1}
        assert ObjectRepository.get_by_id(1, user_id=None) is not None
        
        # Object NOT visible to guests (0)
        cursor.fetchone.return_value = {'id': 2, 'visible_to_guests': 0}
        assert ObjectRepository.get_by_id(2, user_id=None) is None

    def test_create(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = [101]
        assert ObjectRepository.create("N", "D", 1, 1) == 101

    def test_get_by_name(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = True
        assert ObjectRepository.get_by_name("Name") is True

    def test_delete(self, mock_db):
        _, cursor = mock_db
        ObjectRepository.delete(1)
        assert cursor.execute.call_count == 3 # ingredients, comments, objects

    def test_add_ingredients(self, mock_db):
        _, cursor = mock_db
        ObjectRepository.add_ingredients(1, [('a', '1', 'u')])
        cursor.execute.assert_called()

    def test_clear_ingredients(self, mock_db):
        _, cursor = mock_db
        ObjectRepository.clear_ingredients(1)
        cursor.execute.assert_called()