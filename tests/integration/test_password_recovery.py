"""БП 1.4: Email-восстановление пароля — тесты модели PasswordRecoveryToken.

Спецификация:
- TC049: Создание токена при запросе восстановления
- TC050: Токен истекает через 15 минут
- TC051: Токен одноразовый (использован → невалиден)
- TC052: Уникальный токен на каждый запрос
- TC053: Токен привязан к пользователю
"""
import pytest
from datetime import timedelta
from django.utils import timezone


pytestmark = pytest.mark.django_db


@pytest.fixture
def recovery_user(db):
    """Пользователь для тестов восстановления пароля."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email='recovery_test@luberteh.ru',
        password='OldPassword123!',
        first_name='Recovery',
        last_name='Test',
    )


class TestPasswordRecoveryTokenModel:
    """БП 1.4: Модель PasswordRecoveryToken."""

    def test_TC049_create_token_via_manager(self, recovery_user):
        """TC049: Менеджер create_for_user создаёт токен с TTL 15 минут."""
        from accounts.models import PasswordRecoveryToken

        token_obj = PasswordRecoveryToken.objects.create_for_user(recovery_user)

        assert token_obj.user == recovery_user
        assert len(token_obj.token) == 64, "Токен должен быть 64 hex-символа (secrets.token_hex(32))"
        assert token_obj.used_at is None
        # TTL = 15 минут
        expected_expiry = token_obj.created_at + timedelta(minutes=15)
        assert abs((token_obj.expires_at - expected_expiry).total_seconds()) < 5

    def test_TC050_token_expires_after_15_minutes(self, recovery_user):
        """TC050: Токен истекает через 15 минут."""
        from accounts.models import PasswordRecoveryToken

        token_obj = PasswordRecoveryToken.objects.create_for_user(recovery_user)

        # Свежий токен валиден
        assert token_obj.is_valid is True

        # Имитируем истечение: сдвигаем expires_at в прошлое
        token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        token_obj.save()
        token_obj.refresh_from_db()

        assert token_obj.is_valid is False, "Истёкший токен должен быть невалиден"

    def test_TC051_token_is_single_use(self, recovery_user):
        """TC051: Токен одноразовый — после mark_used() невалиден."""
        from accounts.models import PasswordRecoveryToken

        token_obj = PasswordRecoveryToken.objects.create_for_user(recovery_user)
        assert token_obj.is_valid is True

        token_obj.mark_used()
        token_obj.refresh_from_db()

        assert token_obj.used_at is not None
        assert token_obj.is_valid is False, "Использованный токен должен быть невалиден"

    def test_TC052_unique_token_per_request(self, recovery_user):
        """TC052: Каждый запрос генерирует уникальный токен."""
        from accounts.models import PasswordRecoveryToken

        tokens = [
            PasswordRecoveryToken.objects.create_for_user(recovery_user).token
            for _ in range(5)
        ]

        assert len(set(tokens)) == 5, "Все токены должны быть уникальными"

    def test_TC053_token_linked_to_user(self, recovery_user):
        """TC053: Токен привязан к пользователю (FK core.User)."""
        from accounts.models import PasswordRecoveryToken

        token_obj = PasswordRecoveryToken.objects.create_for_user(recovery_user)

        # Обратная связь: user.password_recovery_tokens
        assert token_obj in recovery_user.password_recovery_tokens.all()

        # Удаляем пользователя — токены каскадно удаляются
        user_id = recovery_user.pk
        recovery_user.delete()
        assert not PasswordRecoveryToken.objects.filter(user_id=user_id).exists()
