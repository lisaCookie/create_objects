import unittest
from unittest.mock import patch
from flask import Flask
# Импортируем blueprint, чтобы зарегистрировать его в приложении
from RECIPES.categories.delete_objects import delete_objects_bp

class TestDeleteObjectsRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test_key'
        # РЕГИСТРАЦИЯ BLUEPRINT ОБЯЗАТЕЛЬНА
        self.app.register_blueprint(delete_objects_bp)
        
        # Создаем заглушки для url_for, так как в тестах нет полноценного приложения с другими blueprint
        self.client = self.app.test_client()

    @patch('RECIPES.categories.delete_objects.check_authentication')
    @patch('RECIPES.categories.delete_objects.url_for')
    def test_delete_object_unauthorized(self, mock_url_for, mock_auth):
        mock_auth.return_value = False
        mock_url_for.return_value = '/login'
        
        response = self.client.post('/object/1/delete')
        self.assertEqual(response.status_code, 302)

    @patch('RECIPES.categories.delete_objects.check_authentication')
    @patch('RECIPES.categories.delete_objects.get_object_by_id')
    @patch('RECIPES.categories.delete_objects.delete_obj')
    @patch('RECIPES.categories.delete_objects.url_for')
    def test_delete_object_success(self, mock_url_for, mock_delete, mock_get, mock_auth):
        mock_auth.return_value = True
        mock_get.return_value = {'id': 1, 'category_id': 10}
        mock_url_for.return_value = '/category/10'
        
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            
            response = self.client.post('/object/1/delete')
            mock_delete.assert_called_once_with(1, 1)
            self.assertEqual(response.status_code, 302)

    @patch('RECIPES.categories.delete_objects.check_authentication')
    @patch('RECIPES.categories.delete_objects.delete_category_service')
    @patch('RECIPES.categories.delete_objects.url_for')
    def test_delete_category_error(self, mock_url_for, mock_del_cat, mock_auth):
        mock_auth.return_value = True
        mock_del_cat.side_effect = ValueError("Ошибка удаления")
        mock_url_for.return_value = '/'
        
        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            
            response = self.client.post('/category/5/delete')
            self.assertEqual(response.status_code, 302)