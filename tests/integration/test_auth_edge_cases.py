"""Интеграционные тесты edge-кейсов аутентификации.

БП 1.1.3: Выход из системы и полная маршрутизация.
Тест-кейсы: 1.1-052 (email case-insensitive), 1.1-018 (пользователь без ролей).
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def user_without_roles(db):
    """Пользователь без назначенных ролей."""
    return User.objects.create_user(
        email="no_roles@test.ru",
        password="TestPass123!",
        first_name="Без",
        last_name="Ролей",
        is_active=True,
        requires_password_change=False,
    )


class TestEmailNormalization:
    """Тесты нормализации email при входе (1.1-052)."""

    def test_1_1_052_login_with_uppercase_email(self, api_client, student_user):
        """1.1-052: Вход с email в ВЕРХНЕМ регистре должен быть успешным."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email.upper(),  # ARHIPOV_KYU@TEST.RU
            'password': 'TestPass123!'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data or response.cookies.get('refresh')

    def test_1_1_052_login_with_mixed_case_email(self, api_client, student_user):
        """1.1-052: Вход с email в СМЕШАННОМ регистре должен быть успешным."""
        url = reverse('token_obtain_pair')
        # Преобразуем email в смешанный регистр: ArHiPoV_KyU@TeSt.Ru
        mixed_email = ''.join(
            c.upper() if i % 2 == 0 else c.lower()
            for i, c in enumerate(student_user.email)
        )
        data = {
            'email': mixed_email,
            'password': 'TestPass123!'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


class TestUserWithoutRoles:
    """Тесты пользователя без ролей (1.1-018)."""

    def test_1_1_018_user_without_roles_returns_empty_roles(self, api_client, user_without_roles):
        """1.1-018: Пользователь без ролей получает пустой roles и флаг no_roles=True."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'no_roles@test.ru',
            'password': 'TestPass123!'
        }

        response = api_client.post(url, data, format='json')

        # Вход технически успешный (200), но без ролей
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('roles') == []
        assert response.data.get('no_roles') is True
        # access-токен всё равно выдаётся (фронтенд сам решит, что делать)
        assert 'access' in response.data
