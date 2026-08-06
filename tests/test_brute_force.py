import pytest
from django.core.cache import caches
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_brute_force_protection():
    bf_cache = caches['brute_force']
    bf_cache.clear()  # чистый старт

    client = APIClient()
    url = '/api/token/'
    payload = {
        "email": "brute_force_test@luberteh.ru",
        "password": "WrongPassword123!"
    }
    ip = '192.168.1.100'

    print("\n" + "=" * 60)
    print("🛡️ ТЕСТ BRUTE FORCE PROTECTION")
    print("=" * 60)

    try:
        # Попытки 1-5: обычный 401 без капчи
        for i in range(1, 6):
            response = client.post(url, payload, format='json', REMOTE_ADDR=ip)
            print(f"⛔ Попытка {i}: HTTP {response.status_code} | require_captcha: {response.data.get('require_captcha', False)}")
            assert response.status_code == 401
            assert response.data.get('require_captcha') is not True

        # Попытка 6: появляется require_captcha: true
        response_6 = client.post(url, payload, format='json', REMOTE_ADDR=ip)
        print(f"⚠️ Попытка 6: HTTP {response_6.status_code} | Ответ: {response_6.data}")
        assert response_6.status_code == 401
        assert response_6.data.get('require_captcha') is True
        assert response_6.data.get('attempts_count') == 6
        print("✅ На 6-й попытке API потребовал капчу!")

        # Попытки 7-9: продолжаем без капчи -> 401
        for i in range(7, 10):
            response = client.post(url, payload, format='json', REMOTE_ADDR=ip)
            print(f"⛔ Попытка {i} (без капчи): HTTP {response.status_code}")
            assert response.status_code == 401

        # Попытка 10: счётчик достигает MAX_ATTEMPTS_BEFORE_BLOCK=10 -> блокировка
        response_10 = client.post(url, payload, format='json', REMOTE_ADDR=ip)
        print(f"🔒 Попытка 10: HTTP {response_10.status_code} | Ответ: {response_10.data}")
        assert response_10.status_code == 429, f"Ожидался 429 на 10-й попытке, получен {response_10.status_code}"
        assert response_10.data.get('code') == 'ip_blocked'
        print("✅ На 10-й попытке IP заблокирован (HTTP 429 Too Many Requests)!")

        # Попытка 11: блокировка сохраняется
        response_11 = client.post(url, payload, format='json', REMOTE_ADDR=ip)
        print(f"🔒 Попытка 11: HTTP {response_11.status_code} | Ответ: {response_11.data}")
        assert response_11.status_code == 429
        assert response_11.data.get('code') == 'ip_blocked'
        assert '15 минут' in response_11.data.get('detail', '')
        print("✅ Блокировка сохраняется на последующих попытках!")

    finally:
        bf_cache.clear()  # всегда убираем за собой, даже если тест упал
        print("=" * 60 + "\n")
