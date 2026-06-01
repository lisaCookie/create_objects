# tests/unit/utils/test_filters.py

import pytest
from RECIPES.utils.db_filters import (
    build_users_filter_sql,
    build_categories_filter_sql,
    build_objects_filter_sql,
    search_objects_sql,
    build_my_contribution_sql
)
from RECIPES.utils.admin_filters import (
    build_users_filter_sql_wrapper,
)
from RECIPES.utils.filters import filter_categories_by_search
from RECIPES.utils.my_contrib_filters import generate_my_contribution_filters_sql

# =================================================================
# 1. Тесты DB FILTERS (Генерация SQL)
# =================================================================

class TestDbFilters:
    
    def test_build_users_filter_sql_no_params(self):
        sql, params = build_users_filter_sql()
        assert "WHERE 1=1" in sql
        assert "GROUP BY u.id" in sql
        assert params == []

    def test_build_users_filter_sql_with_creator(self):
        creator_id = "user_123"
        sql, params = build_users_filter_sql(creator_id=creator_id)
        assert "AND u.id = %s" in sql
        assert params == [creator_id]

    def test_build_categories_filter_sql_multi_params(self):
        # Проверка комбинации creator_id и object_id
        sql, params = build_categories_filter_sql(creator_id="u1", object_id="o1")
        assert "AND c.created_by = %s" in sql
        assert "AND c.id IN (SELECT category_id FROM objects WHERE id = %s)" in sql
        assert params == ["u1", "o1"]

    def test_build_objects_filter_sql_logic(self):
        sql, params = build_objects_filter_sql(category_id="cat_1")
        assert "AND o.category_id = %s" in sql
        assert params == ["cat_1"]

    def test_search_objects_sql_empty(self):
        sql, params = search_objects_sql("")
        assert sql == ""
        assert params == []

    def test_search_objects_sql_with_term(self):
        sql, params = search_objects_sql("pizza")
        assert "ILIKE %s" in sql
        assert params == ["%pizza%"]

    def test_build_my_contribution_sql_logic(self):
        user_id = "user_1"
        # Тест без category_id
        res = build_my_contribution_sql(user_id)
        assert "WHERE o.created_by = %s" in res['objects']['sql']
        assert res['objects']['params'] == [user_id]
        
        # Тест с category_id
        res_with_cat = build_my_contribution_sql(user_id, category_id="cat_1")
        assert "AND o.category_id = %s" in res_with_cat['objects']['sql']
        assert res_with_cat['objects']['params'] == [user_id, "cat_1"]


# =================================================================
# 2. Тесты ADMIN FILTERS (Wrappers)
# =================================================================

class TestAdminFiltersWrappers:
    """Проверяем, что обертки просто делегируют вызов и не ломают параметры"""
    
    def test_wrappers_delegate_correctly(self):
        # Тестируем одну из оберток для примера
        sql, params = build_users_filter_sql_wrapper(creator_id="admin_1")
        assert "AND u.id = %s" in sql
        assert params == ["admin_1"]


# =================================================================
# 3. Тесты FILTERS (Рекурсивная логика)
# =================================================================

class TestBusinessLogicFilters:

    @pytest.fixture
    def mock_categories_tree(self):
        """Создает дерево категорий для тестирования рекурсии"""
        return [
            {
                'id': '1', 'name': 'Fruit', 'children': [
                    {'id': '1.1', 'name': 'Apple', 'children': []},
                    {'id': '1.2', 'name': 'Banana', 'children': []},
                ]
            },
            {
                'id': '2', 'name': 'Vegetable', 'children': [
                    {'id': '2.1', 'name': 'Carrot', 'children': []},
                ]
            }
        ]

    def test_filter_categories_by_search_no_term(self, mock_categories_tree):
        # Если поиска нет, возвращаем всё дерево
        result = filter_categories_by_search(mock_categories_tree, "")
        assert len(result) == 2
        assert result[0]['name'] == 'Fruit'

    def test_filter_categories_by_search_match_leaf(self, mock_categories_tree):
        # Ищем 'Apple' (лист дерева)
        result = filter_categories_by_search(mock_categories_tree, "apple")
        assert len(result) == 1
        assert result[0]['name'] == 'Fruit'
        assert len(result[0]['children']) == 1
        assert result[0]['children'][0]['name'] == 'Apple'

    def test_filter_categories_by_search_no_match(self, mock_categories_tree):
        # Ищем то, чего нет
        result = filter_categories_by_search(mock_categories_tree, "Zebra")
        assert result == []

    def test_filter_categories_by_search_partial_match(self, mock_categories_tree):
        # Ищем 'Veg' (часть слова Vegetable)
        result = filter_categories_by_search(mock_categories_tree, "veg")
        assert len(result) == 1
        assert result[0]['name'] == 'Vegetable'


# =================================================================
# 4. Тесты MY CONTRIBUTION FILTERS
# =================================================================

class TestMyContributionFilters:
    
    def test_generate_my_contribution_filters_sql(self):
        user_id = "tester"
        # Проверка вызова обертки
        res = generate_my_contribution_filters_sql(user_id)
        assert 'objects' in res
        assert 'comments' in res
        assert res['objects']['params'] == [user_id]