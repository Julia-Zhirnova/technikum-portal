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

    def test_1_1_047_xss_injection_in_email(self, api_client):
        """1.1-047: XSS-инъекция в email возвращает 400 и не выполняется."""
        url = reverse('token_obtain_pair')
        
        xss_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '"><script>alert(document.cookie)</script>',
            "javascript:alert('XSS')",
            '<svg onload=alert(1)>',
        ]
        
        for payload in xss_payloads:
            data = {
                'email': payload,
                'password': 'student2026'
            }
            response = api_client.post(url, data, format='json')
            
            # Все XSS-попытки должны быть отклонены как невалидный email
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Payload '{payload}': ожидался 400, получен {response.status_code}"
            
            # Проверяем, что в ответе нет неэкранированного скрипта
            response_text = response.content.decode('utf-8')
            for dangerous in ['<script>', 'alert(', 'onerror=', 'javascript:']:
                assert dangerous not in response_text, \
                    f"Payload '{payload}': неэкранированный XSS в ответе: {dangerous}"
            
            # Ответ должен содержать сообщение об ошибке валидации
            assert 'email' in response.data, \
                f"Payload '{payload}': ожидалась ошибка для поля 'email'"

    def test_1_1_047_sql_injection_in_email(self, api_client):
        """Дополнительный тест: SQL-инъекция в email отвергается как невалидный email."""
        url = reverse('token_obtain_pair')
        
        sql_payloads = [
            "' OR '1'='1",
            "admin' --",
            "'; DROP TABLE core_user; --",
        ]
        
        for payload in sql_payloads:
            data = {
                'email': payload,
                'password': 'student2026'
            }
            response = api_client.post(url, data, format='json')
            
            # Все SQL-инъекции отклоняются как невалидный email (EmailValidator)
            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Payload '{payload}': ожидался 400, получен {response.status_code}"
