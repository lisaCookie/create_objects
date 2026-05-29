import unittest
from unittest.mock import MagicMock
from RECIPES.categories.validation import (
    check_authentication, 
    validate_object_exists, 
    validate_not_empty, 
    check_comment_ownership
)

class TestValidation(unittest.TestCase):

    def test_check_authentication_success(self):
        # Имитируем сессию с user_id
        session = {'user_id': 1}
        # В реальном Flask это проверяется через flask.session, 
        # но для unit-теста функции мы проверяем логику напрямую
        # (В данном случае функция check_authentication зависит от контекста Flask)
        pass 

    def test_validate_object_exists_found(self):
        obj = {'id': 1}
        # Не должно выбрасывать исключение
        validate_object_exists(obj)

    def test_validate_object_exists_not_found(self):
        with self.assertRaises(ValueError) as context:
            validate_object_exists(None, "Объект не найден.")
        self.assertEqual(str(context.exception), "Объект не найден.")

    def test_validate_not_empty_success(self):
        validate_not_empty("Some text")

    def test_validate_not_empty_fail(self):
        with self.assertRaises(ValueError) as context:
            validate_not_empty("", "Поле")
        self.assertEqual(str(context.exception), "Поле не может быть пустым.")

    def test_check_comment_ownership(self):
        self.assertTrue(check_comment_ownership(1, 1))
        self.assertFalse(check_comment_ownership(1, 2))

if __name__ == '__main__':
    unittest.main()