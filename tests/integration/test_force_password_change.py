import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import User

@pytest.mark.django_db
class TestForcePasswordChangeAPI:
    
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('force-change-password')
        # Создаем тестового пользователя с флагом смены пароля
        self.user = User.objects.create_user(
            email='test_change_pwd@luberteh.ru',
            password='OldPassword123!',
            requires_password_change=True
        )
        self.client.force_authenticate(user=self.user)

    def test_1_2_4_weak_password(self):
        """1.2.4: Слабый пароль должен отклоняться"""
        payload = {
            'new_password': '12345678',
            'confirm_password': '12345678'
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400
        assert 'password' in str(response.data).lower() or 'символ' in str(response.data).lower()

    def test_1_2_5_passwords_mismatch(self):
        """1.2.5: Пароли не совпадают"""
        payload = {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'DifferentPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400
        assert 'совпадают' in str(response.data).lower()

    def test_1_2_6_same_as_current(self):
        """1.2.6: Новый пароль не должен совпадать с текущим"""
        payload = {
            'new_password': 'OldPassword123!',
            'confirm_password': 'OldPassword123!'
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 400
        assert 'совпадать' in str(response.data).lower() or 'текущим' in str(response.data).lower()

    def test_1_2_7_successful_change(self):
        """1.2.7: Успешная смена пароля"""
        payload = {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == 200
        
        # Проверяем, что флаг сброшен в БД
        self.user.refresh_from_db()
        assert self.user.requires_password_change is False
        
        # Проверяем, что пароль действительно изменился (старый не подходит)
        old_auth_client = APIClient()
        old_login = old_auth_client.post(reverse('token_obtain_pair'), {
            'email': 'test_change_pwd@luberteh.ru',
            'password': 'OldPassword123!'
        })
        assert old_login.status_code == 401
