import sys
from unittest.mock import MagicMock

import pytest
from flask import Flask
from unittest.mock import patch

# 1. Имитируем структуру пакета psycopg2
mock_psycopg2 = MagicMock()
mock_extras = MagicMock()
sys.modules["psycopg2"] = mock_psycopg2
sys.modules["psycopg2.extras"] = mock_extras


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    
    from RECIPES.categories.object_movement import object_movement_bp
    app.register_blueprint(object_movement_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@patch('RECIPES.categories.object_movement.get_db_connection')
def test_ajax_search_objects_empty(mock_get_db, client):
    """Проверка пустого запроса поиска"""
    response = client.get('/admin/ajax/search_objects?q= ')
    assert response.status_code == 200
    assert response.json == []

@patch('RECIPES.categories.object_movement.get_db_connection')
def test_ajax_search_objects_success(mock_get_db, client):
    """Проверка успешного поиска объектов"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.return_value = [(1, 'Apple', 'Fruits')]
    
    response = client.get('/admin/ajax/search_objects?q=app')
    assert response.status_code == 200
    assert response.json == [{'id': 1, 'name': 'Apple', 'category_name': 'Fruits'}]

@patch('RECIPES.categories.object_movement.get_db_connection')
def test_move_object_access_denied(mock_get_db, client):
    """Проверка запрета доступа для не-админа"""
    with client.session_transaction() as sess:
        sess['is_admin'] = False
    
    response = client.post('/admin/move_object', data={'object_id': 1, 'new_category_id': 2})
    assert response.status_code == 403
    assert response.json['error'] == 'Access denied'

@patch('RECIPES.categories.object_movement.get_db_connection')
def test_move_object_success(mock_get_db, client):
    """Проверка успешного перемещения объекта"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    with client.session_transaction() as sess:
        sess['is_admin'] = True

    # Имитация: Объект найден (category_id=1) + Категория найдена
    mock_cursor.fetchone.side_effect = [
        {'id': 1, 'category_id': 1}, 
        {'id': 2}                    
    ]

    response = client.post('/admin/move_object', data={'object_id': 1, 'new_category_id': 2})
    
    assert response.status_code == 200
    assert response.json['success'] is True
    
    # Проверка SQL запроса
    found_update = False
    target_sql = "UPDATE objects SET category_id = %s WHERE id = %s"
    
    # Ожидаемые значения (приводим к строкам для надежности сравнения)
    expected_params = ('2', '1') 
    
    for call in mock_cursor.execute.call_args_list:
        sql_query = call[0][0]
        # Преобразуем все элементы кортежа в строки, чтобы не зависеть от int/str
        params = tuple(str(p) for p in call[0][1])
        
        clean_sql = "".join(sql_query.split())
        clean_target = "".join(target_sql.split())
        
        if clean_target in clean_sql and params == expected_params:
            found_update = True
            break
            
    assert found_update, f"SQL UPDATE call not found. Actual calls: {mock_cursor.execute.call_args_list}"

@patch('RECIPES.categories.object_movement.get_db_connection')
def test_move_object_not_found(mock_get_db, client):
    """Проверка ошибки, если объект не найден"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    with client.session_transaction() as sess:
        sess['is_admin'] = True

    mock_cursor.fetchone.return_value = None 

    response = client.post('/admin/move_object', data={'object_id': 99, 'new_category_id': 2})
    assert response.status_code == 404
    assert 'Объект не найден' in response.json['error']