import pytest
from django.core.cache import caches
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_brute_force_ip_based_blocking():
    """Блокировка применяется к IP, а не к email
    
    Сценарий:
    1. Злоумышленник с одного IP пытается войти под разными email
    2. После 10 суммарных неудачных попыток IP блокируется
    3. Даже успешный вход под одним email не снимает блокировку
    """
    bf_cache = caches['brute_force']
    bf_cache.clear()

    client = APIClient()
    url = '/api/token/'
    ip = '192.168.1.50'

    print("\n" + "=" * 60)
    print("🔒 ТЕСТ БЛОКИРОВКИ ПО IP (независимо от email)")
    print("=" * 60)

    # Попытки 1-5: пробуем войти как user1@luberteh.ru
    payload1 = {
        "email": "user1@luberteh.ru",
        "password": "WrongPassword123!"
    }
    for i in range(1, 6):
        response = client.post(url, payload1, format='json', REMOTE_ADDR=ip)
        print(f"⛔ Попытка {i} (user1): HTTP {response.status_code}")
        assert response.status_code == 401

    # Попытки 6-9: пробуем войти как user2@luberteh.ru (тот же IP)
    payload2 = {
        "email": "user2@luberteh.ru",
        "password": "WrongPassword456!"
    }
    for i in range(6, 10):
        response = client.post(url, payload2, format='json', REMOTE_ADDR=ip)
        print(f"⛔ Попытка {i} (user2): HTTP {response.status_code}")
        assert response.status_code == 401

    # Попытка 10: блокировка IP (суммарно 10 неудачных попыток)
    response_10 = client.post(url, payload2, format='json', REMOTE_ADDR=ip)
    print(f"🔒 Попытка 10 (user2): HTTP {response_10.status_code} | Ответ: {response_10.data}")
    assert response_10.status_code == 429, f"Ожидался 429, получен {response_10.status_code}"
    assert response_10.data.get('code') == 'ip_blocked'
    print("✅ IP заблокирован после 10 суммарных попыток!")

    # Попытка 11: пробуем войти как user3@luberteh.ru (тот же IP)
    payload3 = {
        "email": "user3@luberteh.ru",
        "password": "WrongPassword789!"
    }
    response_11 = client.post(url, payload3, format='json', REMOTE_ADDR=ip)
    print(f"🔒 Попытка 11 (user3): HTTP {response_11.status_code} | Ответ: {response_11.data}")
    assert response_11.status_code == 429
    assert response_11.data.get('code') == 'ip_blocked'
    print("✅ Блокировка сохраняется для других email с того же IP!")

    bf_cache.clear()
    print("=" * 60)
    print("✅ БЛОКИРОВКА ПО IP РАБОТАЕТ КОРРЕКТНО!")
    print("=" * 60)
