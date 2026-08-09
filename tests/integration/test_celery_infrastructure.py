"""Тесты инфраструктуры Celery для асинхронных задач.

Эти тесты проверяют, что Celery worker может:
- Принимать задачи из очереди
- Выполнять их
- Возвращать результаты

БП 1.4 (email recovery), БП 3.3 (DOCX), БП 5.4 (XLSX) зависят от Celery.
"""
import pytest
from django.test import override_settings


class TestCeleryInfrastructure:
    """Проверка базовой инфраструктуры Celery."""

    def test_celery_app_configured(self):
        """Celery приложение должно быть доступно через django.conf.settings."""
        from django.conf import settings
        
        assert hasattr(settings, 'CELERY_BROKER_URL'), "CELERY_BROKER_URL не настроен"
        assert hasattr(settings, 'CELERY_RESULT_BACKEND'), "CELERY_RESULT_BACKEND не настроен"
        
        # Проверяем, что broker — это Redis
        assert 'redis' in settings.CELERY_BROKER_URL.lower(),             f"Celery broker должен использовать Redis, получено: {settings.CELERY_BROKER_URL}"

    def test_celery_can_import_app(self):
        """Celery приложение должно импортироваться из config.celery."""
        try:
            from config.celery import app
            assert app is not None, "Celery app не импортирован"
            assert app.main == 'config', f"Ожидалось main='config', получено: {app.main}"
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать config.celery: {e}")

    def test_celery_task_can_be_defined(self):
        """Должна быть возможность определить Celery task."""
        try:
            from accounts.tasks import add_numbers
            assert callable(add_numbers), "add_numbers должна быть вызываемой"
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать accounts.tasks.add_numbers: {e}")

    @pytest.mark.django_db
    def test_celery_task_can_be_executed_sync(self):
        """Celery task должна выполняться синхронно (для тестов)."""
        from accounts.tasks import add_numbers
        
        # В режиме тестов Celery использует eager mode (синхронное выполнение)
        result = add_numbers.delay(2, 3)
        
        # Проверяем результат
        assert result.get(timeout=5) == 5, "add_numbers(2, 3) должна вернуть 5"

    @pytest.mark.django_db
    def test_celery_task_can_send_test_email(self):
        """Celery task должна уметь отправлять тестовый email (заглушка)."""
        from accounts.tasks import send_test_email
        
        # В режиме тестов email не отправляется реально (EMAIL_BACKEND = 'locmem')
        result = send_test_email.delay('test@example.com', 'Test Subject', 'Test Body')
        
        # Проверяем, что задача выполнилась без ошибок
        assert result.successful(), f"Задача завершилась с ошибкой: {result.result}"
        assert result.get(timeout=5) is True, "send_test_email должна вернуть True"

    def test_celery_beat_installed(self):
        """django-celery-beat должен быть установлен (для периодических задач)."""
        try:
            import django_celery_beat
            assert django_celery_beat.__version__, "django_celery_beat установлен, но версия не определена"
        except ImportError:
            pytest.fail("django-celery-beat не установлен (нужен для периодических задач)")
