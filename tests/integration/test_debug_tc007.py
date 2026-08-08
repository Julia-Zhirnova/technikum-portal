"""Временный отладочный тест для TC007."""
import pytest
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.conf import settings


@pytest.mark.django_db
def test_debug_tc007(api_client):
    User = get_user_model()
    user = User.objects.create_user(
        email='debug@test.ru',
        password='OldPassword123!',
        requires_password_change=True,
    )

    cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
    attempts_key = f'pwd_change_attempts:{user.pk}'
    blocked_key = f'pwd_change_blocked:{user.pk}'

    print(f"\n=== DEBUG: user.pk={user.pk} ===")
    print(f"attempts_key={attempts_key!r}")
    print(f"blocked_key={blocked_key!r}")

    api_client.force_authenticate(user=user)

    for i in range(1, 5):
        response = api_client.post(
            '/api/auth/force-change-password/',
            {'new_password': '12345678', 'confirm_password': '12345678'},
            format='json',
        )
        attempts_val = cache.get(attempts_key)
        blocked_val = cache.get(blocked_key)
        print(f"\n--- Запрос {i}: status={response.status_code} ---")
        print(f"    cache[attempts]={attempts_val!r}")
        print(f"    cache[blocked]={blocked_val!r}")
        if response.status_code == 400:
            print(f"    body={response.data}")

    cache.delete(attempts_key)
    cache.delete(blocked_key)
