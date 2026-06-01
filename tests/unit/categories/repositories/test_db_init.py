import pytest
from unittest.mock import MagicMock, patch
from RECIPES.database.db_init import get_db_connection, init_users_table

@patch("RECIPES.database.db_init.psycopg2.connect")
def test_get_db_connection_success(mock_connect):
    """Проверка успешного подключения."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    conn = get_db_connection()
    assert conn == mock_conn
    mock_connect.assert_called_once()

@patch("RECIPES.database.db_init.psycopg2.connect")
@patch("RECIPES.database.db_init.sleep", return_value=None) 
def test_get_db_connection_retries_and_fails(mock_sleep, mock_connect):
    """Тест, что после всех попыток выбрасывается RuntimeError."""
    
    # ИМПОРТИРУЕМ класс ошибки прямо из модуля, где он используется.
    # Это гарантирует, что except psycopg2.OperationalError поймает ошибку от мока.
    import RECIPES.database.db_init as db_init
    mock_connect.side_effect = db_init.psycopg2.OperationalError("Connection failed")
    
    with pytest.raises(RuntimeError, match="Не удалось подключиться к базе данных"):
        get_db_connection()
    
    assert mock_connect.call_count == 5

@patch("RECIPES.database.db_init.psycopg2.connect")
def test_init_users_table(mock_connect):
    """Проверка вызова SQL при инициализации."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchone.side_effect = [(0,), (0,)]  

    init_users_table()

    assert mock_cursor.execute.called
    mock_conn.close.assert_called_once()