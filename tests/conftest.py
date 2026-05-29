# tests/conftest.py
    # tests/conftest.py
import pytest
from flask import Flask
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False # Отключаем CSRF для тестов

    # Импортируем блюпринты
    from RECIPES.users.login import login_bp
    from RECIPES.users.register import register_bp
    from RECIPES.users.my_contribution import my_contribution_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(my_contribution_bp)

    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db(mocker):
    """
    Мокаем подключение к БД и курсор.
    Подменяем функцию get_db_connection во всех модулях, где она может быть использована,
    чтобы избежать реальных попыток подключения к базе данных.
    """
    # Список всех мест, где может быть импортирована функция get_db_connection
    # Это критически важно, так как 'from module import func' создает локальную копию функции
    targets = [
        'RECIPES.database.db_init.get_db_connection',
        'RECIPES.users.register.get_db_connection',
        'RECIPES.users.login.get_db_connection',
        'RECIPES.users.my_contribution.get_db_connection',
    ]

    # Создаем мок для соединения
    mock_conn = MagicMock()
    # Создаем мок для курсора
    mock_cursor = MagicMock()

    # Настраиваем цепочку вызовов: 
    # get_db_connection() -> возвращает mock_conn
    # mock_conn.__enter__() -> возвращает mock_conn (для использования в with)
    # mock_conn.cursor() -> возвращает mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Применяем мок ко всем целевым модулям
    for target in targets:
        mocker.patch(target, return_value=mock_conn)

    return mock_cursor, mock_conn

