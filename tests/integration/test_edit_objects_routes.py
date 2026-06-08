import unittest
from unittest.mock import patch
from flask import Flask
from RECIPES.categories.edit_objects import edit_objects_bp

class TestEditObjectsRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test_key'
        self.app.register_blueprint(edit_objects_bp)
        self.client = self.app.test_client()

    @patch('RECIPES.categories.edit_objects.check_authentication')
    @patch('RECIPES.categories.edit_objects.get_object_by_id')
    @patch('RECIPES.categories.edit_objects.get_ingredients_by_object_id')
    @patch('RECIPES.categories.edit_objects.url_for')
    @patch('RECIPES.categories.edit_objects.render_template') # МОКАЕМ ШАБЛОН
    def test_edit_object_get_request(self, mock_render, mock_url_for, mock_ingredients, mock_get, mock_auth):
        mock_auth.return_value = True
        mock_get.return_value = {'id': 1, 'category_id': 5}
        mock_ingredients.return_value = []
        mock_url_for.return_value = '/category/5'
        mock_render.return_value = "Mocked HTML"

        with self.client.session_transaction() as sess:
            sess['user_id'] = 1

        response = self.client.get('/object/1/edit')
        self.assertEqual(response.status_code, 200)

    @patch('RECIPES.categories.edit_objects.check_authentication')
    @patch('RECIPES.categories.edit_objects.get_object_by_id')
    @patch('RECIPES.categories.edit_objects.edit_obj')
    @patch('RECIPES.categories.edit_objects.parse_ingredients_for_object')
    @patch('RECIPES.categories.edit_objects.url_for')
    def test_edit_object_post_success(self, mock_url_for, mock_parse, mock_edit, mock_get, mock_auth):
        mock_auth.return_value = True
        mock_get.return_value = {'id': 1, 'category_id': 5}
        mock_parse.return_value = []
        mock_url_for.return_value = '/category/5'

        payload = {
            'object_name': 'New Name',
            'object_description': 'Desc',
            'object_technology': 'Tech',
            'ingredient_name[]': ['Salt'],
            'ingredient_amount[]': ['1'],
            'ingredient_unit[]': ['gram']
        }

        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            
            response = self.client.post('/object/1/edit', data=payload)
            mock_edit.assert_called()
            self.assertEqual(response.status_code, 302)

    @patch('RECIPES.categories.edit_objects.check_authentication')
    @patch('RECIPES.categories.edit_objects.get_comment_by_id')
    @patch('RECIPES.categories.edit_objects.can_edit')
    @patch('RECIPES.categories.edit_objects.edit_comment_service') # МОКАЕМ СЕРВИС
    @patch('RECIPES.categories.edit_objects.url_for')
    def test_edit_comment_permission_denied(self, mock_url_for, mock_edit_service, mock_can_edit, mock_get_comm, mock_auth):
        mock_auth.return_value = True
        mock_get_comm.return_value = {'id': 1, 'user_id': 99, 'object_id': 1, 'text': 'hi'}
        mock_can_edit.return_value = False 
        mock_url_for.return_value = '/category/1'

        with self.app.test_request_context():
            with self.client.session_transaction() as sess:
                sess['user_id'] = 1
            
            response = self.client.post('/comment/1/edit', data={'comment_text': 'new text'})
            self.assertEqual(response.status_code, 302)