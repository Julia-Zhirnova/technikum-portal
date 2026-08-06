import pytest
from unittest.mock import patch
from django.core.cache import caches
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_brute_force_graceful_degradation():
    """1.1-048: Graceful degradation при недоступности Redis
    
    Когда Redis недоступен, система должна:
    1. Не падать с HTTP 500
    2. Продолжать обрабатывать логин-запросы
    3. Возвращать стандартные ошибки аутентификации (401)
    """
    client = APIClient()
    url = '/api/token/'
    payload = {
        "email": "graceful_test@luberteh.ru",
        "password": "WrongPassword123!"
    }
    ip = '192.168.1.300'

    print("\n" + "=" * 60)
    print("🔌 ТЕСТ GRACEFUL DEGRADATION (Redis недоступен)")
    print("=" * 60)

    # Имитируем недоступность Redis через mock
    with patch('accounts.brute_force.BruteForceProtection._is_available', return_value=False):
        print("⚠️ Имитируем падение Redis...")
        
        # Делаем 15 неудачных попыток (больше порога блокировки)
        for i in range(1, 16):
            response = client.post(url, payload, format='json', REMOTE_ADDR=ip)
            print(f"Попытка {i}: HTTP {response.status_code}")
            
            # Все попытки должны возвращать 401 (не 429, не 500)
            assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
            
            # Не должно быть флага require_captcha
            assert response.data.get('require_captcha') is not True, "Капча не должна требоваться при недоступном Redis"
            
            # Не должно быть кода ip_blocked
            assert response.data.get('code') != 'ip_blocked', "IP не должен блокироваться при недоступном Redis"
        
        print("✅ Система продолжила работать без Redis (без падений, без блокировок)")
        
        # Проверяем, что кэш не был затронут
        bf_cache = caches['brute_force']
        attempts_key = f"login_attempts:{ip}"
        blocked_key = f"login_blocked:{ip}"
        
        attempts_value = bf_cache.get(attempts_key)
        blocked_value = bf_cache.get(blocked_key)
        
        # Ключи не должны быть созданы (Redis недоступен)
        assert attempts_value is None, "Ключ попыток не должен быть создан при недоступном Redis"
        assert blocked_value is None, "Ключ блокировки не должен быть создан при недоступном Redis"
        print("✅ Кэш Redis не был затронут (ключи не созданы)")

    print("=" * 60)
    print("✅ GRACEFUL DEGRADATION РАБОТАЕТ КОРРЕКТНО!")
    print("=" * 60)
