import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestLoginAPI:
    
    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse('token_obtain_pair')

    def test_1_1_12_login_invalid_credentials(self):
        """1.1.12: Неверные данные должны возвращать 401"""
        payload = {
            'email': 'arhipov_kyu@luberteh.ru',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        assert response.status_code == 401
        # Проверка общего сообщения об ошибке
        assert 'detail' in response.data

    def test_1_1_13_login_blocked_user(self):
        """1.1.13: Заблокированный пользователь получает 401 с ОБЩИМ сообщением (защита от перебора)"""
        payload = {
            'email': 'blocked_user@luberteh.ru',
            'password': 'Password123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        # С точки зрения безопасности, бэкенд не должен раскрывать, что пользователь заблокирован,
        # чтобы злоумышленники не могли подтверждать существование email в базе.
        assert response.status_code == 401
        
        # Проверяем, что возвращается стандартное общее сообщение
        detail_msg = response.data.get('detail', '').lower()
        assert 'неверный' in detail_msg or 'ошибка' in detail_msg

    def test_1_1_7_backend_email_validation(self):
        """1.1.7: Backend отвергает невалидный email (возвращает 401 для защиты от перебора)"""
        payload = {
            'email': 'invalid-email-without-at',
            'password': 'student2026'
        }
        response = self.client.post(self.login_url, payload, format='json')
        
        # SimpleJWT по умолчанию возвращает 401 при любой неудачной аутентификации, 
        # чтобы не подсказывать злоумышленнику формат или существование email.
        assert response.status_code == 401 
        assert 'detail' in response.data
