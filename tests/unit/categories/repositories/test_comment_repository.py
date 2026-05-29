import pytest
from RECIPES.categories.repositories.comment_repository import CommentRepository

class TestCommentRepository:
    @pytest.fixture
    def mock_db(self, mocker):
        mock_conn = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mocker.patch('RECIPES.categories.repositories.comment_repository.get_db_connection', return_value=mock_conn)
        return mock_conn, mock_cursor

    def test_get_by_object_id(self, mock_db):
        _, cursor = mock_db
        cursor.fetchall.return_value = [{'id': 1, 'text': 'hi'}]
        assert len(CommentRepository.get_by_object_id(1)) == 1

    def test_get_by_id(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = {'id': 1, 'text': 'hi'}
        assert CommentRepository.get_by_id(1)['text'] == 'hi'

    def test_get_dependencies(self, mock_db):
        _, cursor = mock_db
        cursor.fetchone.return_value = (1, True)
        assert CommentRepository.get_dependencies(1) == (1, True)

    def test_create(self, mock_db):
        _, cursor = mock_db
        CommentRepository.create(1, 1, "text")
        cursor.execute.assert_called()

    def test_update(self, mock_db):
        _, cursor = mock_db
        CommentRepository.update(1, "new text")
        cursor.execute.assert_called()

    def test_delete(self, mock_db):
        _, cursor = mock_db
        CommentRepository.delete(1)
        cursor.execute.assert_called()