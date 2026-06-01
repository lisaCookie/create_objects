import unittest
from unittest.mock import MagicMock, patch

from RECIPES.admin.services.category_service import delete_category
from RECIPES.admin.services.comment_service import delete_comment
from RECIPES.admin.services.object_service import delete_object
from RECIPES.admin.services.user_service import delete_user


class TestCrudServices(unittest.TestCase):

    # --- Tests for category_service.py ---
    @patch('RECIPES.admin.services.category_service.get_db_connection')
    def test_delete_category(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.side_effect = [[{'id': 10}, {'id': 11}]]

        result = delete_category(1)
        
        self.assertTrue(result)
        self.assertEqual(mock_cursor.execute.call_count, 7)

    # --- Tests for object_service.py ---
    @patch('RECIPES.admin.services.object_service.get_db_connection')
    def test_delete_object(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = delete_object(5)
        
        self.assertTrue(result)
        calls = [
            unittest.mock.call("DELETE FROM ingredients WHERE object_id = %s", (5,)),
            unittest.mock.call("DELETE FROM comments WHERE object_id = %s", (5,)),
            unittest.mock.call("DELETE FROM objects WHERE id = %s", (5,)),
        ]
        mock_cursor.execute.assert_has_calls(calls)

    # --- Tests for comment_service.py ---
    @patch('RECIPES.admin.services.comment_service.get_db_connection')
    def test_delete_comment(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = delete_comment(99)
        
        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with("DELETE FROM comments WHERE id = %s", (99,))

    # --- Tests for user_service.py ---
    @patch('RECIPES.admin.services.user_service.get_db_connection')
    def test_delete_user_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        result = delete_user(user_id=2, current_user_id=1)
        
        self.assertTrue(result)
        self.assertEqual(mock_cursor.execute.call_count, 4)

    def test_delete_self_raises_error(self):
        with self.assertRaises(ValueError) as context:
            delete_user(user_id=1, current_user_id=1)
        self.assertEqual(str(context.exception), "Нельзя удалить самого себя")