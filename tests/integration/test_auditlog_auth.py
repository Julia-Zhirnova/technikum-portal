"""Интеграционные тесты логирования событий аутентификации.

БП 1.1.2: Логирование аутентификации.
Тест-кейсы: 1.1-011, 1.1-012, 1.1-049
"""
import pytest
from django.urls import reverse
from rest_framework import status
from core.models import AuditLog

pytestmark = pytest.mark.django_db


class TestAuditLogAuthentication:
    """Тесты логирования событий входа и выхода."""

    def test_1_1_011_login_success_creates_audit_log(self, api_client, student_user):
        """1.1-011: После успешного входа в core_auditlog создана запись."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'TestPass123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем создание записи в AuditLog
        audit_entry = AuditLog.objects.filter(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS
        ).first()
        
        assert audit_entry is not None
        assert audit_entry.ip_address is not None
        assert audit_entry.details.get('email') == student_user.email

    def test_1_1_012_login_failed_creates_audit_log(self, api_client, student_user):
        """1.1-012: После неудачного входа в core_auditlog создана запись."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'WrongPassword123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Проверяем создание записи в AuditLog
        audit_entry = AuditLog.objects.filter(
            action_type=AuditLog.ActionType.LOGIN_FAIL,
            details__email=student_user.email
        ).first()
        
        assert audit_entry is not None
        assert audit_entry.ip_address is not None
        # user_id может быть None для неудачных попыток

    def test_1_1_049_logout_creates_audit_log(self, authenticated_client, student_user):
        """1.1-049: После выхода в core_auditlog создана запись."""
        # Предполагаем, что endpoint /api/logout/ существует
        url = reverse('logout')
        
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем создание записи в AuditLog
        audit_entry = AuditLog.objects.filter(
            user=student_user,
            action_type=AuditLog.ActionType.LOGOUT
        ).first()
        
        assert audit_entry is not None
        assert audit_entry.ip_address is not None
