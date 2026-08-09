from django.db import models

# Create your models here.


# ============================================
# БП 1.4: Email-восстановление пароля
# ============================================
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordRecoveryTokenManager(models.Manager):
    """Менеджер токенов восстановления пароля."""

    def create_for_user(self, user, ttl_minutes: int = 15):
        """Создать токен восстановления с TTL 15 минут (БП 1.4)."""
        return self.create(
            user=user,
            token=secrets.token_hex(32),  # 64 hex-символа
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes),
        )


class PasswordRecoveryToken(models.Model):
    """Одноразовый токен восстановления пароля (БП 1.4).

    Спецификация:
    - TTL 15 минут (expires_at)
    - Одноразовый (used_at → невалиден)
    - Привязан к пользователю (CASCADE при удалении)
    - Уникальный токен (secrets.token_hex(32))
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_recovery_tokens',
        verbose_name='Пользователь',
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    objects = PasswordRecoveryTokenManager()

    class Meta:
        verbose_name = 'Токен восстановления пароля'
        verbose_name_plural = 'Токены восстановления пароля'
        ordering = ['-created_at']

    def __str__(self):
        return f'RecoveryToken(user={self.user_id}, expires={self.expires_at:%Y-%m-%d %H:%M})'

    @property
    def is_valid(self) -> bool:
        """Токен валиден, если не истёк и не использован."""
        return self.used_at is None and self.expires_at > timezone.now()

    def mark_used(self):
        """Пометить токен использованным (одноразовость)."""
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])
