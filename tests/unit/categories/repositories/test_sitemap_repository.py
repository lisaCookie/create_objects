import pytest
from RECIPES.categories.repositories.sitemap_repository import SitemapRepository

class TestSitemapRepository:
    @pytest.fixture
    def mock_db(self, mocker):
        mock_conn = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch('RECIPES.categories.repositories.sitemap_repository.get_db_connection', return_value=mock_conn)
        return mock_conn, mock_cursor

    def test_get_root_categories(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'id': 1}]
        assert len(SitemapRepository.get_root_categories()) == 1

    def test_get_children_and_objects(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.side_effect = [[{'id': 2}], [{'id': 10}]] # children, then objects
        children, objects = SitemapRepository.get_children_and_objects(1)
        assert len(children) == 1
        assert len(objects) == 1