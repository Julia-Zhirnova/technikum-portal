"""Интеграционные тесты валидации email при аутентификации.

БП 1.1-046: Валидация формата email на сервере.
"""
import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestEmailValidation:
    """Тесты серверной валидации email при входе."""

    def test_1_1_046_email_without_at_symbol(self, api_client):
        """1.1-046: Email без символа @ возвращает 400 Bad Request."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuserluberteh.ru',  # нет @
            'password': 'student2026'
        }
        
        response = api_client.post(url, data, format='json')
        
        # Ожидаем 400 Bad Request, а не 401 (валидация, а не аутентификация)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, \
            f"Ожидался 400, получен {response.status_code}: {response.data}"
        
        # Проверяем наличие ошибки валидации для поля email
        assert 'email' in response.data, \
            f"Ожидалась ошибка для поля 'email', получено: {response.data}"
        
        # Проверяем текст ошибки
        email_errors = response.data['email']
        assert any('email' in str(err).lower() for err in email_errors), \
            f"Ожидалось сообщение об ошибке email, получено: {email_errors}"

    def test_1_1_046_email_with_invalid_format(self, api_client):
        """Дополнительный тест: различные невалидные форматы email."""
        url = reverse('token_obtain_pair')
        
        invalid_emails = [
            'notanemail',
            '@nodomain.com',
            'user@',
            'user@.com',
        ]
        
        for invalid_email in invalid_emails:
            data = {
                'email': invalid_email,
                'password': 'student2026'
            }
            response = api_client.post(url, data, format='json')
            
            # Все невалидные email должны возвращать 400
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Email '{invalid_email}': ожидался 400, получен {response.status_code}"
