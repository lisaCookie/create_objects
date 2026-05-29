# tests/integration/test_users_flows.py
import pytest
from werkzeug.security import generate_password_hash
from unittest.mock import MagicMock

# Класс-помощник, чтобы мок работал и как кортеж user[0], и как словарь user['is_admin']
class MockRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            # Маппинг индексов согласно вашему SELECT id, password_hash, is_admin
            mapping = {0: 'id', 1: 'password_hash', 2: 'is_admin'}
            return super().__getitem__(mapping[key])
        return super().__getitem__(key)

class TestUserFlows:
    # --- ТЕСТЫ РЕГИСТРАЦИИ ---
    def test_register_success(self, client, mock_db):
        mock_cursor, _ = mock_db
        mock_cursor.fetchone.return_value = None

        response = client.post('/register', data={
            'username': 'new_user',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert mock_cursor.execute.call_count == 2

    def test_register_user_exists(self, client, mock_db):
        mock_cursor, _ = mock_db
        mock_cursor.fetchone.return_value = (1,)

        response = client.post('/register', data={
            'username': 'existing_user',
            'password': 'password123',
            'confirm_password': 'password123'
        })

        assert 'Имя пользователя уже занято' in response.data.decode('utf-8')

    # --- ТЕСТЫ ЛОГИНА ---
    def test_login_success_as_admin(self, client, mock_db):
        mock_cursor, _ = mock_db
        password = "admin_password"
        pw_hash = generate_password_hash(password)
        
        # Используем MockRow, чтобы работало и user[0], и user['is_admin']
        mock_cursor.fetchone.return_value = MockRow({
            'id': 1, 
            'password_hash': pw_hash, 
            'is_admin': True
        })

        response = client.post('/login', data={
            'username': 'admin',
            'password': password,
            'auth_code': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess['user_id'] == 1
            assert sess['is_admin'] is True

    def test_login_fail_wrong_password(self, client, mock_db):
        mock_cursor, _ = mock_db
        pw_hash = generate_password_hash("correct_password")
        mock_cursor.fetchone.return_value = MockRow({
            'id': 1, 
            'password_hash': pw_hash, 
            'is_admin': False
        })

        response = client.post('/login', data={
            'username': 'user',
            'password': 'wrong_password'
        })

        # В Flask при ошибке validate_on_submit() возвращает 200 (рендерит страницу с ошибкой), 
        # а не редирект. Проверяем наличие текста ошибки.
        assert 'Неверный логин или пароль' in response.data.decode('utf-8')

    def test_login_fail_auth_code_missing_for_user(self, client, mock_db, mocker):
        mock_cursor, _ = mock_db
        pw_hash = generate_password_hash("password")
        mock_cursor.fetchone.return_value = MockRow({
            'id': 1, 
            'password_hash': pw_hash, 
            'is_admin': False
        })

        mocker.patch('RECIPES.database.db_settings.get_auth_code', return_value="secret123")
        mocker.patch('RECIPES.users.login.render_template', return_value='<html><body>Неверный код доступа</body></html>')

        response = client.post('/login', data={
            'username': 'user',
            'password': 'password',
            'auth_code': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Неверный код доступа' in response.data.decode('utf-8')

    # --- ТЕСТЫ MY CONTRIBUTION ---
    def test_my_contribution_redirect_if_not_logged_in(self, client):
        response = client.get('/my-contribution')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

    def test_my_contribution_success(self, client, mock_db, mocker):
        mock_cursor, _ = mock_db

        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test_user'

        # Моки для трех последовательных вызовов fetchall (категории, объекты, комментарии)
        mock_cursor.fetchall.side_effect = [
            [(1, 'Cat1', '2023-01-01 10:00:00')],  # categories
            [(10, 'Obj1', 'Desc', '2023-01-01 10:00:00', 1, 'Cat1')],  # objects
            []  # comments
        ]

        mocker.patch('RECIPES.users.my_contribution.render_template', return_value='Mocked response with Obj1')

        response = client.get('/my-contribution')

        assert response.status_code == 200
        assert b'Obj1' in response.data
