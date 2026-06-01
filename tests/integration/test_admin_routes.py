# tests/integration/test_admin_routes.py

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_services(mocker):
    """Фикстура для мока всех сервисов, используемых в admin.py"""
    return {
        'dashboard': mocker.patch('RECIPES.admin.admin.dashboard_service'),
        'user': mocker.patch('RECIPES.admin.admin.user_service'),
        'category': mocker.patch('RECIPES.admin.admin.category_service'),
        'object': mocker.patch('RECIPES.admin.admin.object_service'),
        'comment': mocker.patch('RECIPES.admin.admin.comment_service'),
        'auth': mocker.patch('RECIPES.admin.admin.auth_service'),
        'db_init': mocker.patch('RECIPES.database.db_init.get_db_connection')
    }

@pytest.fixture
def admin_session(client):
    """Вспомогательная функция для имитации авторизованного админа"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    return client

@pytest.fixture(autouse=True)
def mock_app_url_for(mocker, client):
    """
    Самый глубокий уровень патча. 
    Мы патчим метод url_for непосредственно у объекта приложения, 
    который используется внутри Flask/Werkzeug.
    """
    def fake_url_for(endpoint, **values):
        if endpoint == 'index':
            return '/index'
        return f"/{endpoint.replace('.', '/')}"

    # Патчим метод url_for у экземпляра приложения, который использует клиент
    mocker.patch.object(client.application, 'url_for', side_effect=fake_url_for)

# --- ТЕСТЫ DASHBOARD ---

def test_dashboard_unauthorized(client):
    """Если пользователь не в сессии, должен редирект на login"""
    response = client.get('/admin')
    assert response.status_code == 302
    assert response.location.endswith('/login')

def test_dashboard_not_admin(client, mock_services):
    """Если пользователь авторизован, но не админ, должен редирект на index"""
    with client.session_transaction() as sess:
        sess['user_id'] = 2
    
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': False}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn

    response = client.get('/admin')
    assert response.status_code == 302
    assert response.location == '/index'

def test_dashboard_success(admin_session, mock_services):
    """Успешная загрузка дашборда админом"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    
    mock_services['dashboard'].get_dashboard_data.return_value = {'users': [], 'objects': []}
    mock_services['auth'].get_current_auth_code.return_value = 'secret_code'

    response = admin_session.get('/admin')
    assert response.status_code == 200
    mock_services['dashboard'].get_dashboard_data.assert_called_once()

# --- ТЕСТЫ УДАЛЕНИЯ (DELETE ROUTES) ---

def test_delete_user_success(admin_session, mock_services):
    """Успешное удаление пользователя"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn

    response = admin_session.post('/user/10/delete')
    
    assert response.status_code == 302
    mock_services['user'].delete_user.assert_called_with(10, 1)

def test_delete_user_not_authorized(client):
    """Попытка удаления без авторизации"""
    response = client.post('/user/10/delete')
    assert response.status_code == 302
    assert response.location.endswith('/login')

def test_delete_category_admin(admin_session, mock_services):
    """Успешное удаление категории"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn

    response = admin_session.post('/category/5/delete')
    
    assert response.status_code == 302
    mock_services['category'].delete_category.assert_called_with(5)

def test_delete_object_admin(admin_session, mock_services):
    """Успешное удаление объекта"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn

    response = admin_session.post('/object/100/delete')
    
    assert response.status_code == 302
    mock_services['object'].delete_object.assert_called_with(100)

def test_delete_comment_admin(admin_session, mock_services):
    """Успешное удаление комментария"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn

    response = admin_session.post('/comment/50/delete')
    
    assert response.status_code == 302
    mock_services['comment'].delete_comment.assert_called_with(50)

# --- ТЕСТЫ ОБНОВЛЕНИЯ КОДА ---

def test_update_auth_code_success(admin_session, mock_services):
    """Успешное обновление auth_code"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn
    
    mock_services['auth'].update_auth_code.return_value = True

    response = admin_session.post('/update_auth_code', data={'auth_code': 'new_secret_123'})
    
    assert response.status_code == 302
    mock_services['auth'].update_auth_code.assert_called_with('new_secret_123')

def test_update_auth_code_failure(admin_session, mock_services):
    """Ошибка при обновлении auth_code"""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = {'is_admin': True}
    mock_services['dashboard'].get_db_connection.return_value = mock_conn
    mock_services['db_init'].return_value = mock_conn
    
    mock_services['auth'].update_auth_code.return_value = False

    response = admin_session.post('/update_auth_code', data={'auth_code': 'wrong_code'})
    
    assert response.status_code == 302
    mock_services['auth'].update_auth_code.assert_called()