"""Celery приложение для проекта Technikum Portal.

Это основной файл конфигурации Celery, который:
1. Инициализирует Celery app с настройками из Django settings
2. Автоматически обнаруживает tasks во всех установленных приложениях
3. Использует Redis как broker и result backend

Запуск worker:
    celery -A config worker -l info --concurrency=4

Запуск beat (периодические задачи):
    celery -A config beat -l info
"""
import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Загружаем конфигурацию из Django settings (все ключи с префиксом CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение tasks.py во всех INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестовая задача для отладки Celery worker."""
    print(f'Request: {self.request!r}')
