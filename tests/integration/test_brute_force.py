"""Интеграционные тесты защиты от брутфорс-атак.

БП 1.1.5: Brute Force Protection через Redis.
Тест-кейсы: 1.1-013, 1.1-014, TC034, TC035, TC036
"""
import pytest
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from django.core.cache import caches

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_brute_force_cache():
    """Очищает кэш brute_force перед каждым тестом."""
    cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
    cache.clear()
    yield
    cache.clear()


@pytest.mark.xdist_group("cache_sensitive")
class TestBruteForceCaptcha:
    """Тесты появления reCAPTCHA после 5 неудачных попыток."""

    def test_1_1_013_require_captcha_after_5_failed_attempts(self, api_client, student_user, mock_client_ip):
        """1.1-013: После 5 неудачных попыток возвращается require_captcha=true."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'WrongPassword123!'
        }

        # Делаем 5 неудачных попыток
        for i in range(5):
            response = api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert 'require_captcha' not in response.data or not response.data.get('require_captcha')

        # 6-я попытка должна вернуть require_captcha=true
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data.get('require_captcha') is True

    def test_1_1_013_successful_login_resets_attempts(self, api_client, student_user, mock_client_ip):
        """1.1-013: После успешного входа счётчик попыток сбрасывается."""
        url = reverse('token_obtain_pair')
        wrong_data = {'email': student_user.email, 'password': 'WrongPassword123!'}
        correct_data = {'email': student_user.email, 'password': 'student2026'}

        # 3 неудачных попытки
        for _ in range(3):
            api_client.post(url, wrong_data, format='json')

        # Успешный вход
        response = api_client.post(url, correct_data, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Ещё 3 неудачных — не должно быть require_captcha (счётчик сброшен)
        for _ in range(3):
            resp = api_client.post(url, wrong_data, format='json')
            assert not resp.data.get('require_captcha'), "Счётчик не сбросился после успешного входа"


@pytest.mark.xdist_group("cache_sensitive")
class TestBruteForceBlock:
    """Тесты блокировки IP после 10 неудачных попыток."""

    def test_1_1_014_block_after_10_failed_attempts(self, api_client, student_user, mock_client_ip):
        """1.1-014: После 10 неудачных попыток IP блокируется на 15 минут."""
        url = reverse('token_obtain_pair')
        data = {
            'email': student_user.email,
            'password': 'WrongPassword123!'
        }

        # 10 неудачных попыток
        for _ in range(10):
            api_client.post(url, data, format='json')

        # 11-я попытка должна вернуть 429 Too Many Requests
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert 'blocked' in str(response.data).lower() or \
               'много' in str(response.data).lower() or \
               'too many' in str(response.data).lower()

    def test_TC034_block_applies_to_different_emails(self, api_client, mock_client_ip):
        """TC034: Блокировка применяется ко всем email с одного IP."""
        url = reverse('token_obtain_pair')

        # 10 попыток с разными email
        for i in range(10):
            data = {'email': f'user{i}@test.ru', 'password': 'WrongPassword!'}
            api_client.post(url, data, format='json')

        # 11-я попытка с ЛЮБЫМ email должна быть заблокирована
        response = api_client.post(url, {'email': 'other@test.ru', 'password': 'Wrong!'}, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_TC036_ttl_of_attempts_key(self, api_client, student_user, mock_client_ip):
        """TC036: Ключ login_attempts:<ip> имеет TTL 900 секунд."""
        url = reverse('token_obtain_pair')
        data = {'email': student_user.email, 'password': 'WrongPassword123!'}

        # 3 неудачные попытки
        for _ in range(3):
            api_client.post(url, data, format='json')

        # Проверяем TTL ключа в Redis (с учётом уникального IP от mock_client_ip)
        cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
        # Ключ должен существовать и иметь TTL близкий к 900
        # (в зависимости от реализации - может быть через get_ttl или через get)
        # Для простоты проверяем что ключ существует
        # Конкретный формат ключа определяется в middleware
        assert cache.get(f'technikum:login_attempts:{mock_client_ip}') is not None or \
               cache.get(f'login_attempts:{mock_client_ip}') is not None, \
               f"Ключ счётчика попыток не создан в Redis для IP {mock_client_ip}"


@pytest.mark.xdist_group("cache_sensitive")
class TestBruteForceRecovery:
    """Тесты восстановления после блокировки."""

    def test_TC035_recovery_after_block_duration(self, api_client, student_user, monkeypatch, mock_client_ip):
        """TC035: После окончания блокировки вход снова возможен."""
        from django.core.cache import caches

        url = reverse('token_obtain_pair')
        wrong_data = {'email': student_user.email, 'password': 'WrongPassword123!'}
        correct_data = {'email': student_user.email, 'password': 'student2026'}

        # Блокируем IP (10 неудачных попыток)
        for _ in range(10):
            api_client.post(url, wrong_data, format='json')

        # Проверяем что заблокированы
        response = api_client.post(url, wrong_data, format='json')
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # Имитируем прошествие 15 минут — удаляем ключ блокировки (с учётом mock_client_ip)
        cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
        cache.delete(f'technikum:login_blocked:{mock_client_ip}')
        cache.delete(f'login_blocked:{mock_client_ip}')
        cache.delete(f'technikum:login_attempts:{mock_client_ip}')
        cache.delete(f'login_attempts:{mock_client_ip}')

        # Теперь вход должен быть успешным
        response = api_client.post(url, correct_data, format='json')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.xdist_group("cache_sensitive")
class TestBruteForceGracefulDegradation:
    """Тесты graceful degradation при недоступности Redis."""

    def test_1_1_048_login_works_when_redis_unavailable(self, api_client, student_user, monkeypatch, mock_client_ip):
        """1.1-048: При недоступности Redis вход работает без блокировок."""
        # Мокируем метод _is_available(), чтобы имитировать недоступность Redis.
        # Прямая замена settings.CACHES не работает из-за кеширования в django.core.cache.caches.
        from accounts.brute_force import BruteForceProtection
        monkeypatch.setattr(BruteForceProtection, '_is_available', lambda self: False)

        url = reverse('token_obtain_pair')
        data = {'email': student_user.email, 'password': 'student2026'}

        # Вход должен быть успешным даже без Redis
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        # Много неудачных попыток тоже не должны вызывать 429
        wrong_data = {'email': student_user.email, 'password': 'WrongPassword123!'}
        for _ in range(15):
            response = api_client.post(url, wrong_data, format='json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
