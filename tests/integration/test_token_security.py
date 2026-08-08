"""Интеграционные тесты безопасности токенов.

БП 1.1.4: Безопасность токенов и password_version.
Тест-кейсы: 1.1-015, 1.1-016, 1.1-050
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()


class TestHttpOnlyRefreshCookie:
    """Тесты httpOnly cookie для refresh-токена (1.1-015)."""

    def test_1_1_015_refresh_token_in_httponly_cookie(self, api_client, student_user):
        """1.1-015: Refresh-токен установлен как httpOnly cookie."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'student2026'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK, \
            f"Ожидался 200, получен {response.status_code}: {response.data}"
        # Проверяем наличие httpOnly cookie с refresh-токеном
        assert 'refresh' in response.cookies
        refresh_cookie = response.cookies['refresh']
        assert refresh_cookie['httponly'] is True
        assert refresh_cookie['samesite'] in ['Strict', 'Lax']


class TestPasswordVersion:
    """Тесты инвалидации токенов при смене пароля (1.1-016, 1.1-050)."""

    def test_1_1_016_old_access_token_invalid_after_password_change(
        self, api_client, password_change_user
    ):
        """1.1-016: Старый access-токен невалиден после смены пароля."""
        # 1. Получаем access-токен со старым паролем
        url = reverse('token_obtain_pair')
        data = {'email': password_change_user.email, 'password': 'OldPassword123!'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK, \
            f"Ожидался 200, получен {response.status_code}: {response.data}"
        old_access_token = response.data['access']

        # 2. Меняем пароль
        change_url = reverse('force-change-password')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_access_token}')
        change_data = {
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        change_response = api_client.post(change_url, change_data, format='json')
        assert change_response.status_code == status.HTTP_200_OK

        # 3. Пытаемся использовать старый access-токен
        # Очищаем credentials и устанавливаем старый токен
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {old_access_token}')
        
        # Делаем запрос к защищённому endpoint
        profile_url = reverse('user-profile')
        profile_response = api_client.get(profile_url)

        # Старый токен должен быть отклонён (401)
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED
        # Проверяем наличие специального кода ошибки в теле ответа.
        # Middleware возвращает JsonResponse, поэтому парсим .content
        import json as json_lib
        try:
            body = json_lib.loads(profile_response.content)
            assert body.get('code') == 'password_changed'
        except (ValueError, AttributeError):
            pass  # Главное — статус 401

    def test_1_1_050_old_refresh_token_blacklisted_after_password_change(
        self, api_client, password_change_user
    ):
        """1.1-050: Старый refresh-токен в blacklist после смены пароля."""
        # 1. Получаем refresh-токен со старым паролем
        url = reverse('token_obtain_pair')
        data = {'email': password_change_user.email, 'password': 'OldPassword123!'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK, \
            f"Ожидался 200, получен {response.status_code}: {response.data}"
        refresh_cookie = response.cookies.get('refresh')
        old_refresh_token = response.data.get('refresh') or (
            refresh_cookie.value if refresh_cookie else None
        )
        assert old_refresh_token, "Refresh-токен не найден ни в теле, ни в cookie"

        # 2. Меняем пароль
        access_token = response.data['access']
        change_url = reverse('force-change-password')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        change_data = {
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        change_response = api_client.post(change_url, change_data, format='json')
        assert change_response.status_code == status.HTTP_200_OK

        # 3. Пытаемся обновить access-токен с помощью старого refresh
        refresh_url = reverse('token_refresh')
        api_client.credentials()  # Очищаем authorization header
        refresh_data = {'refresh': old_refresh_token}
        refresh_response = api_client.post(refresh_url, refresh_data, format='json')

        # Старый refresh-токен должен быть отклонён (401)
        assert refresh_response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_400_BAD_REQUEST
        ]
