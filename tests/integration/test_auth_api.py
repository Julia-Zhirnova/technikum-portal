"""Backend-тесты для БП 1.1 (Аутентификация и JWT)."""
import pytest
from django.urls import reverse
from django.core.cache import caches
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestAuthAPI:
    """Тесты эндпоинта /api/token/."""

    def test_1_1_003_jwt_flags_and_cookies(self, api_client, student_user):
        """[1.1-003] Успешный вход возвращает JWT с флагами и HttpOnly cookie."""
        url = reverse('token_obtain_pair')
        response = api_client.post(
            url,
            {'email': 'arhipov_kyu@luberteh.ru', 'password': 'student2026'},
            format='json',
        )

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'roles' in response.data
        assert response.data['requires_password_change'] is False

        # Refresh-токен в httpOnly cookie
        assert 'refresh' in response.cookies
        cookie = response.cookies['refresh']
        assert cookie['httponly'] is True
        # БП 1.1-015: SameSite=Strict для защиты от CSRF
        assert cookie['samesite'] == 'Strict', f"SameSite должен быть 'Strict', получен: {cookie['samesite']!r}"

    def test_1_1_004_wrong_password(self, api_client, student_user):
        """[1.1-004] Существующий email + неверный пароль → 401."""
        url = reverse('token_obtain_pair')
        response = api_client.post(
            url,
            {'email': 'arhipov_kyu@luberteh.ru', 'password': 'WrongPass!'},
            format='json',
        )
        assert response.status_code == 401

    def test_1_1_005_nonexistent_email(self, api_client, db):
        """[1.1-005] Несуществующий email → 401 (защита от энумерации)."""
        url = reverse('token_obtain_pair')
        response = api_client.post(
            url,
            {'email': 'fake@luberteh.ru', 'password': 'ValidPass123!'},
            format='json',
        )
        assert response.status_code == 401

    def test_1_1_010_blocked_user(self, api_client, blocked_user):
        """[1.1-010] Заблокированный пользователь → 401."""
        url = reverse('token_obtain_pair')
        response = api_client.post(
            url,
            {'email': 'blocked_user@luberteh.ru', 'password': 'Password123!'},
            format='json',
        )
        assert response.status_code == 401
