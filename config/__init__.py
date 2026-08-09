# Импорт Celery приложения при запуске Django
# Это позволяет использовать @shared_task decorator
from .celery import app as celery_app

__all__ = ('celery_app',)

