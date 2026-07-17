import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()

@pytest.mark.django_db
class TestAuthFlow:
    """Тесты Функции 1.1 и 1.2: Авторизация, маршрутизация и смена пароля"""

    # --- ФУНКЦИЯ 1.1 ---
    def test_login_blocked_user_returns_specific_401(self):
        User.objects.create_user(email='blocked@test.ru', password='Pass123!', is_active=False)
        client = APIClient()
        response = client.post('/api/token/', {'email': 'blocked@test.ru', 'password': 'Pass123!'})
        assert response.status_code == 401
        assert "заблокирована" in response.data.get("detail", "").lower()

    def test_login_invalid_credentials_returns_generic_401(self):
        User.objects.create_user(email='user@test.ru', password='Pass123!')
        client = APIClient()
        response = client.post('/api/token/', {'email': 'user@test.ru', 'password': 'WrongPass!'})
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.data.get("detail", "")

    def test_login_success_returns_flags_and_roles(self):
        user = User.objects.create_user(email='success@test.ru', password='Pass123!', requires_password_change=True)
        role = Role.objects.create(id_role='student', name='Студент')
        UserRole.objects.create(user=user, role=role)
        
        client = APIClient()
        response = client.post('/api/token/', {'email': 'success@test.ru', 'password': 'Pass123!'})
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['requires_password_change'] is True
        assert 'student' in response.data['roles']

    # --- ФУНКЦИЯ 1.2 ---
    def test_force_change_password_weak_password_rejected(self):
        user = User.objects.create_user(email='weak@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': '12345678',
            'confirm_password': '12345678'
        })
        
        assert response.status_code == 400
        assert "Пароль должен содержать минимум 8 символов, включая заглавную букву, цифру и спецсимвол" in str(response.data)

    def test_force_change_password_same_as_current_rejected(self):
        user = User.objects.create_user(email='same@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'OldPass123!',
            'confirm_password': 'OldPass123!'
        })
        
        assert response.status_code == 400
        assert "Новый пароль не должен совпадать с текущим" in str(response.data)

    def test_force_change_password_mismatch_rejected(self):
        user = User.objects.create_user(email='mismatch@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'DifferentPass123!'
        })
        
        assert response.status_code == 400
        assert "Пароли не совпадают" in str(response.data)

    def test_force_change_password_success(self):
        user = User.objects.create_user(email='success_pwd@test.ru', password='OldPass123!', requires_password_change=True)
        Role.objects.create(id_role='student', name='Студент')
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        })
        
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.requires_password_change is False
        assert user.check_password('NewSuperPass123!') is True
