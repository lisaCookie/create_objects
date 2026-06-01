import unittest
from unittest.mock import patch

from RECIPES.admin.services.auth_service import get_current_auth_code, update_auth_code


class TestAuthService(unittest.TestCase):

    @patch('RECIPES.admin.services.auth_service.get_auth_code')
    def test_get_current_auth_code(self, mock_get):
        mock_get.return_value = "secret123"
        result = get_current_auth_code()
        self.assertEqual(result, "secret123")
        mock_get.assert_called_once()

    @patch('RECIPES.admin.services.auth_service.update_settings_auth_code')
    def test_update_auth_code(self, mock_update):
        mock_update.return_value = True
        result = update_auth_code("new_code")
        self.assertTrue(result)
        mock_update.assert_called_once_with("new_code")