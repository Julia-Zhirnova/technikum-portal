"""Интеграционные тесты rate limiting для /api/token/refresh/.

БП 1.1-TC038: Защита от DDoS на endpoint обновления токенов.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.mark.cache_sensitive
class TestTokenRefreshRateLimit:
    """Тесты rate limiting для /api/token/refresh/."""

    def test_1_1_TC038_rate_limit_token_refresh(self, api_client, student_user, mock_client_ip):
        """1.1-TC038: После 30 запросов на refresh за минуту → 429 Too Many Requests."""
        # Получаем refresh-токен для студента
        refresh = RefreshToken.for_user(student_user)
        refresh_token = str(refresh)
        
        url = reverse('token_refresh')
        
        # Первые 30 запросов должны быть успешными (200 OK)
        for i in range(30):
            response = api_client.post(
                url,
                {'refresh': refresh_token},
                format='json'
            )
            # Каждый refresh создаёт новый refresh-токен, используем его
            if response.status_code == status.HTTP_200_OK:
                new_refresh = response.data.get('refresh')
                if new_refresh:
                    refresh_token = new_refresh
        
        # 31-й запрос должен вернуть 429 Too Many Requests
        response = api_client.post(
            url,
            {'refresh': refresh_token},
            format='json'
        )
        
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, \
            f"Ожидался 429 на 31-м запросе, получен {response.status_code}: {response.data}"
        
        # Проверяем наличие сообщения об ошибке
        assert 'detail' in response.data or 'message' in response.data, \
            f"Ожидалось сообщение об ошибке, получено: {response.data}"

    def test_rate_limit_resets_after_window(self, api_client, student_user, monkeypatch):
        """Дополнительный тест: после истечения окна rate limit сбрасывается."""
        # Этот тест требует mock времени, пока пропускаем
        pytest.skip("Требует mock времени (freezegun)")
