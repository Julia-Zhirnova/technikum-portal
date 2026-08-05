"""Сервис защиты от брутфорс-атак через Redis.

БП 1.1.5: Brute Force Protection.
- После 5 неудачных попыток → require_captcha=true
- После 10 неудачных попыток → блокировка IP на 15 минут
- Graceful degradation при недоступности Redis
"""
import logging
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


class BruteForceProtection:
    """Защита от брутфорс-атак на основе IP-адреса."""

    def __init__(self, ip_address: str):
        self.ip = ip_address
        self.config = settings.BRUTE_FORCE_PROTECTION
        try:
            self.cache = caches[self.config['CACHE_ALIAS']]
        except Exception as e:
            logger.error(f"Не удалось получить кэш {self.config['CACHE_ALIAS']}: {e}")
            self.cache = None

    @property
    def _attempts_key(self) -> str:
        return f"login_attempts:{self.ip}"

    @property
    def _blocked_key(self) -> str:
        return f"login_blocked:{self.ip}"

    def _is_available(self) -> bool:
        """Проверяет доступность Redis. При недоступности — логирует и возвращает False."""
        if self.cache is None:
            return False
        try:
            # Пробуем выполнить простую операцию для проверки связи
            self.cache.get('__connectivity_check__')
            return True
        except Exception as e:
            logger.warning(f"Redis unavailable, bruteforce protection disabled: {e}")
            return False

    def is_blocked(self) -> bool:
        """Проверяет, заблокирован ли IP."""
        if not self._is_available():
            return False
        try:
            return bool(self.cache.get(self._blocked_key))
        except Exception:
            return False

    def get_attempts_count(self) -> int:
        """Возвращает количество неудачных попыток."""
        if not self._is_available():
            return 0
        try:
            value = self.cache.get(self._attempts_key)
            return int(value) if value is not None else 0
        except Exception:
            return 0

    def require_captcha(self) -> bool:
        """Нужна ли reCAPTCHA для следующей попытки.
        
        По БП 1.1.5: после 5 неудачных попыток → reCAPTCHA.
        Это значит, что 5-я попытка ещё без капчи, а 6-я и далее — с капчей.
        Поэтому используем строгое сравнение (>).
        """
        attempts = self.get_attempts_count()
        return attempts > self.config['MAX_ATTEMPTS_BEFORE_CAPTCHA']

    def record_failed_attempt(self) -> int:
        """Записывает неудачную попытку. Возвращает новое количество попыток."""
        if not self._is_available():
            return 0
        try:
            ttl = self.config['ATTEMPTS_TTL_SECONDS']
            # Атомарный инкремент: если ключа нет — создаём со значением 1
            try:
                new_value = self.cache.incr(self._attempts_key)
                # Обновляем TTL, так как incr его не меняет
                self.cache.expire(self._attempts_key, ttl)
            except ValueError:
                # Ключ не существует — создаём
                self.cache.set(self._attempts_key, 1, ttl)
                new_value = 1

            # Если достигнут порог блокировки — блокируем IP
            if new_value >= self.config['MAX_ATTEMPTS_BEFORE_BLOCK']:
                self.block()

            return new_value
        except Exception as e:
            logger.error(f"Ошибка записи неудачной попытки: {e}")
            return 0

    def record_successful_login(self):
        """Сбрасывает счётчик попыток после успешного входа."""
        if not self._is_available():
            return
        try:
            self.cache.delete(self._attempts_key)
            self.cache.delete(self._blocked_key)
        except Exception as e:
            logger.error(f"Ошибка сброса счётчика: {e}")

    def block(self):
        """Блокирует IP на BLOCK_DURATION_SECONDS."""
        if not self._is_available():
            return
        try:
            duration = self.config['BLOCK_DURATION_SECONDS']
            self.cache.set(self._blocked_key, True, duration)
            logger.info(f"IP {self.ip} заблокирован на {duration} сек.")
        except Exception as e:
            logger.error(f"Ошибка блокировки IP: {e}")
