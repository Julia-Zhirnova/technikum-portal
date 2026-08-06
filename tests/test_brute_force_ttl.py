import pytest
import time
from django.core.cache import caches
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_brute_force_ttl():
    """TC036: TTL ключей Redis = 900 секунд (15 минут)"""
    bf_cache = caches['brute_force']
    bf_cache.clear()

    client = APIClient()
    url = '/api/token/'
    payload = {
        "email": "ttl_test@luberteh.ru",
        "password": "WrongPassword123!"
    }
    ip = '192.168.1.200'

    print("\n" + "=" * 60)
    print("⏱️ ТЕСТ TTL КЛЮЧЕЙ REDIS")
    print("=" * 60)

    # 1. Делаем 3 неудачные попытки
    for i in range(3):
        client.post(url, payload, format='json', REMOTE_ADDR=ip)

    # 2. Проверяем, что ключ создан
    attempts_key = f"login_attempts:{ip}"
    attempts_value = bf_cache.get(attempts_key)
    assert attempts_value == 3, f"Ожидалось 3 попытки, получено {attempts_value}"
    print(f"✅ Ключ {attempts_key} создан со значением {attempts_value}")

    # 3. Проверяем TTL ключа (должен быть ~900 секунд)
    ttl = bf_cache.ttl(attempts_key)
    assert ttl is not None, "TTL ключа не установлен"
    assert 895 <= ttl <= 900, f"Ожидался TTL ~900 сек, получено {ttl}"
    print(f"✅ TTL ключа: {ttl} сек (ожидалось ~900)")

    # 4. Проверяем, что ключ блокировки НЕ создан (ещё не 10 попыток)
    blocked_key = f"login_blocked:{ip}"
    blocked_value = bf_cache.get(blocked_key)
    assert blocked_value is None, f"Ключ блокировки не должен быть создан, получено {blocked_value}"
    print(f"✅ Ключ блокировки {blocked_key} не создан (попыток < 10)")

    # 5. Делаем ещё 7 попыток (итого 10)
    for i in range(7):
        client.post(url, payload, format='json', REMOTE_ADDR=ip)

    # 6. Проверяем, что ключ блокировки создан
    blocked_value = bf_cache.get(blocked_key)
    assert blocked_value is not None, "Ключ блокировки должен быть создан"
    blocked_ttl = bf_cache.ttl(blocked_key)
    assert 895 <= blocked_ttl <= 900, f"Ожидался TTL блокировки ~900 сек, получено {blocked_ttl}"
    print(f"✅ Ключ блокировки {blocked_key} создан, TTL: {blocked_ttl} сек")

    # 7. Проверяем TTL ключа попыток после блокировки
    attempts_ttl = bf_cache.ttl(attempts_key)
    print(f"✅ TTL ключа попыток после блокировки: {attempts_ttl} сек")

    # Очистка
    bf_cache.clear()
    print("=" * 60)
    print("✅ ТЕСТ TTL ПРОЙДЕН!")
    print("=" * 60)
