import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestAuthAndRouting:
    """Тесты Функции 1.1: Авторизация и умная маршрутизация"""

    def test_successful_login_returns_tokens_and_flags(self):
        """1. Успешный вход с валидными данными → код 200 + выдача JWT + флаг смены пароля."""
        user = User.objects.create_user(email='test@luberteh.ru', password='ValidPass123!', requires_password_change=True)
        role = Role.objects.create(id_role='student', name='Студент')
        UserRole.objects.create(user=user, role=role)
        
        client = APIClient()
        response = client.post('/api/token/', {'email': 'test@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['requires_password_change'] is True

    def test_login_with_nonexistent_email_returns_generic_401(self):
        """2. Вход с несуществующим email → код 401 + общая ошибка."""
        client = APIClient()
        response = client.post('/api/token/', {'email': 'fake@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.data.get("detail", "")

    def test_login_with_wrong_password_returns_generic_401(self):
        """2.1. Вход с неверным паролем → код 401 + общая ошибка (защита от перебора)."""
        User.objects.create_user(email='test2@luberteh.ru', password='ValidPass123!')
        client = APIClient()
        response = client.post('/api/token/', {'email': 'test2@luberteh.ru', 'password': 'WrongPassword!'})
        
        assert response.status_code == 401
        assert "Неверный email или пароль" in response.data.get("detail", "")

    def test_login_with_blocked_user_returns_specific_401(self):
        """3. Вход с заблокированным пользователем (is_active=False) → код 401 + спец. сообщение."""
        User.objects.create_user(email='blocked@luberteh.ru', password='ValidPass123!', is_active=False)
        client = APIClient()
        response = client.post('/api/token/', {'email': 'blocked@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 401
        assert "заблокирована" in response.data.get("detail", "").lower()

    def test_routing_for_curator_with_teacher_role(self):
        """4. Пользователь с ролями [curator, teacher] получает обе роли в токене (фронтенд направит на /teacher)."""
        user = User.objects.create_user(email='curator@luberteh.ru', password='ValidPass123!')
        role_teacher = Role.objects.create(id_role='teacher', name='Преподаватель')
        role_curator = Role.objects.create(id_role='curator', name='Куратор')
        UserRole.objects.create(user=user, role=role_teacher)
        UserRole.objects.create(user=user, role=role_curator)
        
        client = APIClient()
        response = client.post('/api/token/', {'email': 'curator@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 200
        assert set(response.data['roles']) == {'teacher', 'curator'}

    def test_routing_for_admin_has_highest_priority(self):
        """5. Пользователь с ролями [admin, teacher, curator] получает все роли (фронтенд направит на /admin)."""
        user = User.objects.create_user(email='admin@luberteh.ru', password='ValidPass123!')
        role_admin = Role.objects.create(id_role='admin', name='Администратор')
        role_teacher = Role.objects.create(id_role='teacher', name='Преподаватель')
        UserRole.objects.create(user=user, role=role_admin)
        UserRole.objects.create(user=user, role=role_teacher)
        
        client = APIClient()
        response = client.post('/api/token/', {'email': 'admin@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 200
        assert 'admin' in response.data['roles']

    def test_force_password_change_flag_is_present(self):
        """6. Пользователь с requires_password_change=True получает этот флаг в ответе при логине."""
        user = User.objects.create_user(email='newbie@luberteh.ru', password='ValidPass123!', requires_password_change=True)
        Role.objects.create(id_role='student', name='Студент')
        # Роль добавляется через сигнал или вручную, для теста проверим флаг в ответе
        client = APIClient()
        response = client.post('/api/token/', {'email': 'newbie@luberteh.ru', 'password': 'ValidPass123!'})
        
        assert response.status_code == 200
        assert response.data['requires_password_change'] is True
