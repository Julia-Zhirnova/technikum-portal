import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestForcePasswordChange:
    """Тесты Функции 1.2: Принудительная смена пароля."""

    def _create_user_with_role(self, email='test@test.ru', password='OldPass123!'):
        """Хелпер: создаёт пользователя со ролью student."""
        user = User.objects.create_user(
            email=email,
            password=password,
            requires_password_change=True
        )
        role, _ = Role.objects.get_or_create(id_role='student', name='Студент')
        UserRole.objects.get_or_create(user=user, role=role)
        return user

    def test_force_change_password_success(self):
        """1. Успешная смена пароля: флаг becomes False."""
        user = self._create_user_with_role(email='force@test.ru')
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

    def test_force_change_password_weak_password(self):
        """2. Слабый пароль "12345678" отклоняется."""
        user = self._create_user_with_role(email='weak@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': '12345678',
            'confirm_password': '12345678'
        })

        assert response.status_code == 400
        assert 'new_password' in response.data
        user.refresh_from_db()
        assert user.requires_password_change is True

    def test_force_change_password_same_as_current(self):
        """3. Пароль, совпадающий с текущим, отклоняется."""
        user = self._create_user_with_role(email='same@test.ru', password='OldPass123!')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'OldPass123!',
            'confirm_password': 'OldPass123!'
        })

        assert response.status_code == 400
        assert 'Новый пароль не должен совпадать с текущим' in str(response.data)

    def test_force_change_password_mismatch(self):
        """4. Поля "Новый пароль" и "Подтверждение" не совпадают."""
        user = self._create_user_with_role(email='mismatch@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'DifferentPass123!'
        })

        assert response.status_code == 400
        assert 'Пароли не совпадают' in str(response.data)

    def test_force_change_password_no_uppercase(self):
        """5. Пароль без заглавной буквы отклоняется."""
        user = self._create_user_with_role(email='noupper@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'newpassword123!',
            'confirm_password': 'newpassword123!'
        })

        assert response.status_code == 400
        assert 'заглавную' in str(response.data)

    def test_force_change_password_no_digit(self):
        """6. Пароль без цифры отклоняется."""
        user = self._create_user_with_role(email='nodigit@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewPassword!!',
            'confirm_password': 'NewPassword!!'
        })

        assert response.status_code == 400
        assert 'цифру' in str(response.data)

    def test_force_change_password_no_special(self):
        """7. Пароль без спецсимвола отклоняется."""
        user = self._create_user_with_role(email='nospecial@test.ru')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        })

        assert response.status_code == 400
        assert 'спецсимвол' in str(response.data)

    def test_force_change_password_unauthenticated(self):
        """8. Неаутентифицированный запрос отклоняется (403)."""
        client = APIClient()
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        })
        assert response.status_code == 403
