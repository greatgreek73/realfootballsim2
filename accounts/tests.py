from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

class AuthenticationTestCase(TestCase):
    def setUp(self):
        # Создание пользователя для тестирования
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')

    def test_successful_login(self):
        # Отправка данных аутентификации на проверку
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        # Проверка успешного входа
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вы успешно вошли в систему')
