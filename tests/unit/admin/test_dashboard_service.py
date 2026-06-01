import unittest
from unittest.mock import MagicMock, patch

from RECIPES.admin.services.dashboard_service import get_dashboard_data


class TestDashboardService(unittest.TestCase):

    @patch('RECIPES.admin.services.dashboard_service.build_users_filter_sql')
    @patch('RECIPES.admin.services.dashboard_service.build_categories_filter_sql')
    @patch('RECIPES.admin.services.dashboard_service.build_objects_filter_sql')
    @patch('RECIPES.admin.services.dashboard_service.build_comments_filter_sql')
    @patch('RECIPES.admin.services.dashboard_service.get_db_connection')
    def test_get_dashboard_data(self, mock_get_conn, mock_comm_sql, mock_obj_sql, mock_cat_sql, mock_user_sql):
        mock_user_sql.return_value = ("SELECT...", (1,))
        mock_cat_sql.return_value = ("SELECT...", (1,))
        mock_obj_sql.return_value = ("SELECT...", (1,))
        mock_comm_sql.return_value = ("SELECT...", (1,))

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchall.side_effect = [
            [('u1',)],        # all_users_for_filter
            [('c1',)],        # all_categories_for_filter
            [('o1',)],        # all_objects_for_filter
            [('u_f1',)],      # users (filtered)
            [('c_f1',)],      # categories (filtered)
            [('o_f1',)],      # objects (filtered)
            [('cm_f1',)],     # comments (filtered)
        ]

        result = get_dashboard_data(creator_id_filter=1)

        self.assertIn('users', result)
        self.assertEqual(result['current_creator_id'], 1)
        self.assertEqual(result['users'], [('u_f1',)])
        mock_conn.close.assert_called_once()