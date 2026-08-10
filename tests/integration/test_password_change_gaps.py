"""БП 1.2: закрытие пробелов покрытия (TC009, TC021, TC022, TC027)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def force_user(db):
    user = User.objects.create_user(email='gap_test@luberteh.ru', password='OldPassword123!')
    user.first_name = 'Test'
    user.last_name = 'Gap'
    user.middle_name = 'Change'
    user.requires_password_change = True
    user.save()
    return user


def auth(client, user):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(user)}')


class TestBP12Gaps:
    def test_TC009_flag_false_returns_403(self, api_client, force_user):
        """TC009: requires_password_change=False → 403 Forbidden."""
        force_user.requires_password_change = False
        force_user.save()
        auth(api_client, force_user)
        r = api_client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!',
        }, format='json')
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_TC021_first_name_substring_not_error(self, api_client, force_user):
        """TC021: подстрока first_name (не полное совпадение) → 200 OK."""
        auth(api_client, force_user)
        r = api_client.post('/api/auth/force-change-password/', {
            'new_password': 'MyTestPass123!',   # содержит 'Test' как подстроку
            'confirm_password': 'MyTestPass123!',
        }, format='json')
        assert r.status_code == status.HTTP_200_OK

    def test_TC022_middle_name_not_checked(self, api_client, force_user):
        """TC022: middle_name не проверяется → 200 OK."""
        auth(api_client, force_user)
        r = api_client.post('/api/auth/force-change-password/', {
            'new_password': 'ChangePass123!',   # содержит middle_name 'Change'
            'confirm_password': 'ChangePass123!',
        }, format='json')
        assert r.status_code == status.HTTP_200_OK

    def test_TC027_empty_new_password(self, api_client, force_user):
        """TC027: пустое поле new_password → 400 Bad Request."""
        auth(api_client, force_user)
        r = api_client.post('/api/auth/force-change-password/', {
            'new_password': '',
            'confirm_password': '',
        }, format='json')
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_TC004_db_state_after_successful_change(self, api_client, force_user):
        """TC004: проверка БД — флаг, password_version, password_changed_at, сброс счётчика."""
        from django.core.cache import caches
        cache = caches['brute_force']
        auth(api_client, force_user)
        cache.set(f'pwd_change_attempts:{force_user.pk}', 1, 300)
        old_version = force_user.password_version

        r = api_client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!',
        }, format='json')

        assert r.status_code == status.HTTP_200_OK
        force_user.refresh_from_db()
        assert force_user.requires_password_change is False
        assert force_user.password_version == old_version + 1, "password_version инкрементирован"
        if hasattr(force_user, 'password_changed_at'):
            assert force_user.password_changed_at is not None, "password_changed_at обновлён"
        assert cache.get(f'pwd_change_attempts:{force_user.pk}') is None, "счётчик попыток удалён"
