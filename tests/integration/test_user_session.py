"""Интеграционные тесты модели UserSession.

БП 1.1-051: Создание записи в core_usersession при успешном входе.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import UserSession

pytestmark = pytest.mark.django_db
User = get_user_model()


class TestUserSession:
    """Тесты создания записей UserSession при аутентификации."""

    def test_1_1_051_user_session_created_on_login(self, api_client, student_user):
        """1.1-051: После успешного входа создаётся запись в core_usersession."""
        # Очищаем старые сессии
        UserSession.objects.filter(user=student_user).delete()
        initial_count = UserSession.objects.filter(user=student_user).count()
        
        # Выполняем вход
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'student2026'
        }
        response = api_client.post(url, data, format='json')
        
        # Проверяем успешный вход
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        
        # Проверяем создание записи UserSession
        new_count = UserSession.objects.filter(user=student_user).count()
        assert new_count == initial_count + 1, \
            f"Ожидалось создание 1 записи UserSession, создано {new_count - initial_count}"
        
        # Проверяем данные записи
        session = UserSession.objects.filter(user=student_user).order_by('-created_at').first()
        assert session is not None
        assert session.ip_address is not None
        assert session.user_agent is not None
        assert session.expires_at is not None
        assert session.is_active is True

    def test_multiple_sessions_for_same_user(self, api_client, student_user):
        """Пользователь может иметь несколько активных сессий (разные устройства)."""
        UserSession.objects.filter(user=student_user).delete()
        
        # Первый вход
        url = reverse('token_obtain_pair')
        data = {'email': student_user.email, 'password': 'student2026'}
        response1 = api_client.post(url, data, format='json')
        assert response1.status_code == status.HTTP_200_OK
        
        # Второй вход (имитация другого устройства)
        api_client2 = type(api_client)()
        response2 = api_client2.post(url, data, format='json')
        assert response2.status_code == status.HTTP_200_OK
        
        # Проверяем, что создано 2 сессии
        sessions = UserSession.objects.filter(user=student_user)
        assert sessions.count() == 2, \
            f"Ожидалось 2 сессии, создано {sessions.count()}"
        
        # Проверяем, что session_id разные
        session_ids = [s.session_id for s in sessions]
        assert len(session_ids) == len(set(session_ids)), \
            "session_id должны быть уникальными"
