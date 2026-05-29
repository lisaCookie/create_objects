import sys
from unittest.mock import MagicMock

# 1. Имитируем psycopg2
mock_psycopg2 = MagicMock()
mock_extras = MagicMock()
sys.modules["psycopg2"] = mock_psycopg2
sys.modules["psycopg2.extras"] = mock_extras

import pytest
from unittest.mock import patch
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    
    # --- РЕГИСТРАЦИЯ ВСЕХ НЕОБХОДИМЫХ BLUEPRINTS ---
    
    # Чтобы работал redirect(url_for('login.login'))
    try:
        from RECIPES.users.auth import auth_bp # Замените на ваш реальный путь к auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        # Если путь другой, создадим заглушку, чтобы url_for не падал
        from flask import Blueprint
        fake_auth = Blueprint('login', __name__)
        @fake_auth.route('/login')
        def login(): return "login"
        app.register_blueprint(fake_auth)

    # Чтобы работал redirect(url_for('index')) или url_for('objects.category_page')
    try:
        from RECIPES.categories.objects import objects_bp # Замените на ваш реальный путь
        app.register_blueprint(objects_bp)
    except ImportError:
        from flask import Blueprint
        fake_objects = Blueprint('objects', __name__)
        @fake_objects.route('/<int:category_id>')
        def category_page(category_id): return "category"
        @fake_objects.route('/')
        def index(): return "index"
        app.register_blueprint(fake_objects)

    # Основной Blueprint, который мы тестируем
    from RECIPES.categories.objects_visibility import visibility_bp
    app.register_blueprint(visibility_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# --- ОСТАЛЬНЫЕ ТЕСТЫ БЕЗ ИЗМЕНЕНИЙ ---

def test_toggle_visibility_no_auth(client):
    """Проверка редиректа, если пользователь не авторизован"""
    response = client.post('/object/1/toggle_visibility')
    assert response.status_code == 302
    assert '/login' in response.location

@patch('RECIPES.categories.objects_visibility.get_db_connection')
def test_toggle_visibility_success(mock_get_db, client):
    """Проверка успешного переключения видимости"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['user_id'] = 10

    mock_cursor.fetchone.side_effect = [
        {'id': 1, 'created_by': 10, 'category_id': 5}, 
        {'visible_to_guests': 0}                      
    ]

    response = client.post('/object/1/toggle_visibility', environ_base={'HTTP_REFERER': '/some_page'})
    
    assert response.status_code == 302
    
    found_update = False
    target_sql = "UPDATE objects SET visible_to_guests = %s WHERE id = %s"
    for call in mock_cursor.execute.call_args_list:
        sql_query = call[0][0]
        params = tuple(str(p) for p in call[0][1])
        clean_sql = "".join(sql_query.split())
        clean_target = "".join(target_sql.split())
        if clean_target in clean_sql and params == ('1', '1'):
            found_update = True
            break
    assert found_update

@patch('RECIPES.categories.objects_visibility.get_db_connection')
def test_toggle_visibility_wrong_owner(mock_get_db, client):
    """Проверка, что нельзя менять видимость чужого объекта"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with client.session_transaction() as sess:
        sess['user_id'] = 10 

    mock_cursor.fetchone.return_value = {'id': 1, 'created_by': 20, 'category_id': 5}

    response = client.post('/object/1/toggle_visibility', environ_base={'HTTP_REFERER': '/some_page'})
    
    assert response.status_code == 302
    for call in mock_cursor.execute.call_args_list:
        assert "UPDATE objects" not in call[0][0]