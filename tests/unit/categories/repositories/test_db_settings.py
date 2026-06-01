from unittest.mock import MagicMock, patch
from RECIPES.database.db_settings import get_auth_code, update_settings_auth_code

@patch("RECIPES.database.db_settings.get_db_connection")
def test_get_auth_code_success(mock_get_conn):
    """Проверка успешного получения кода."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = ("SECRET123",)
    
    code = get_auth_code()
    assert code == "SECRET123"
    mock_conn.close.assert_called_once()

@patch("RECIPES.database.db_settings.get_db_connection")
def test_get_auth_code_none(mock_get_conn):
    """Проверка, когда записи нет."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchone.return_value = None
    
    code = get_auth_code()
    assert code is None

@patch("RECIPES.database.db_settings.get_db_connection")
def test_update_settings_auth_code_success(mock_get_conn):
    """Проверка успешного обновления кода."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.rowcount = 1
    
    result = update_settings_auth_code("NEW_CODE")
    assert result is True
    mock_cursor.execute.assert_called()
    args, _ = mock_cursor.execute.call_args
    assert "NEW_CODE" in args[1]

@patch("RECIPES.database.db_settings.get_db_connection")
def test_update_settings_auth_code_fail(mock_get_conn):
    """Проверка, что обновление не затрагивает строк."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.rowcount = 0
    
    result = update_settings_auth_code("NEW_CODE")
    assert result is False