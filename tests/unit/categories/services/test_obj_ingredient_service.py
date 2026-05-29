import pytest
from RECIPES.categories.services.obj_ingredient_service import (
    get_ingredients_by_object_id,
    insert_ingredients_for_object,
    parse_ingredients_for_object
)

class TestObjIngredientService:

    @pytest.fixture
    def mock_repo(self, mocker):
        # Мокаем функции из репозитория
        self.mock_get_rep = mocker.patch('RECIPES.categories.services.obj_ingredient_service.get_ingredients_by_object_id_rep')
        self.mock_insert_rep = mocker.patch('RECIPES.categories.services.obj_ingredient_service.insert_ingredients_for_object_rep')

    def test_get_ingredients_by_object_id(self, mock_repo):
        # Проверяем проброс вызова (binding)
        expected_data = [{'name': 'salt', 'amount': 1, 'unit': 'tsp'}]
        self.mock_get_rep.return_value = expected_data
        
        result = get_ingredients_by_object_id(1)
        
        self.mock_get_rep.assert_called_once_with(1)
        assert result == expected_data

    def test_insert_ingredients_valid_data(self, mock_repo):
        # Тест на корректную трансформацию и вставку
        names = [" salt ", "sugar"]
        amounts = ["10", "5"]
        units = ["g", "kg"]
        
        insert_ingredients_for_object(1, names, amounts, units)
        
        # Ожидаемый результат после strip() и int()
        expected_payload = [
            {'name': 'salt', 'amount': 10, 'unit': 'g'},
            {'name': 'sugar', 'amount': 5, 'unit': 'kg'}
        ]
        self.mock_insert_rep.assert_called_once_with(1, expected_payload)

    def test_insert_ingredients_with_defaults_and_filtering(self, mock_repo):
        # Тест: 
        # 1. Проверка дефолтной единицы измерения 'ml'
        # 2. Проверка фильтрации некорректных данных (не число или отрицательное)
        names = ["water", "bad_item", "negative"]
        amounts = ["100", "abc", "-5"] 
        units = ["ml"] # Для 'bad_item' и 'negative' юнитов не будет в списке
        
        insert_ingredients_for_object(1, names, amounts, units)
        
        # 'bad_item' (abc) и 'negative' (-5) должны быть отфильтрованы
        expected_payload = [
            {'name': 'water', 'amount': 100, 'unit': 'ml'}
        ]
        self.mock_insert_rep.assert_called_once_with(1, expected_payload)

    def test_insert_ingredients_empty_data(self, mock_repo):
        # Если данных после фильтрации нет, репозиторий не должен вызываться
        insert_ingredients_for_object(1, ["name"], ["not_a_number"], ["ml"])
        self.mock_insert_rep.assert_not_called()

    def test_parse_ingredients_for_object(self):
        # Тест функции парсинга (она возвращает кортежи)
        names = [" Salt ", "Sugar ", "Water"]
        amounts = [" 10 ", " 20 ", " 30 "]
        units = ["g", "kg"] # Для Water не указан юнит
        
        result = parse_ingredients_for_object(names, amounts, units)
        
        expected = [
            ("Salt", "10", "g"),
            ("Sugar", "20", "kg"),
            ("Water", "30", "ml") # Проверка дефолтного 'ml'
        ]
        assert result == expected

    def test_parse_ingredients_only_name_check(self):
        # В parse_ingredients проверяется только наличие имени
        names = ["Salt", ""]
        amounts = ["10", "20"]
        units = ["g", "g"]
        
        result = parse_ingredients_for_object(names, amounts, units)
        
        # Пустое имя должно быть проигнорировано
        assert len(result) == 1
        assert result[0][0] == "Salt"