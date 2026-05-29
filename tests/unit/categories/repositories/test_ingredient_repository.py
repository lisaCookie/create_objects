import pytest
from RECIPES.categories.repositories.ingredient_repository import get_ingredients_by_object_id_rep, insert_ingredients_for_object_rep

class TestIngredientRepository:
    @pytest.fixture
    def mock_db(self, mocker):
        mock_conn = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch('RECIPES.categories.repositories.ingredient_repository.get_db_connection', return_value=mock_conn)
        return mock_conn, mock_cursor

    def test_get_ingredients_by_object_id(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'name': 'salt', 'amount': '1', 'unit': 'tsp'}]
        res = get_ingredients_by_object_id_rep(1)
        assert res[0]['name'] == 'salt'

    def test_insert_ingredients_for_object_rep(self, mock_db):
        _, cursor = mock_db
        data = [{'name': 'a', 'amount': '1', 'unit': 'u'}]
        insert_ingredients_for_object_rep(1, data)
        cursor.executemany.assert_called()