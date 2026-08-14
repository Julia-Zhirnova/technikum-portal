
from celery import shared_task
from django.core.files.base import ContentFile
from django.utils import timezone
from core.models import ImportHistory, AuditLog
from core.views import EmploymentImportExportViewSet
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def async_import_employment(self, user_id, data_rows, mode, file_name, file_size):
    """Асинхронный импорт трудоустройств"""
    from django.contrib.auth import get_user_model
    from django.test import RequestFactory
    from rest_framework.test import force_authenticate
    
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден")
        return {'status': 'failed', 'error': 'User not found'}
    
    # Создание Request объекта для использования views
    factory = RequestFactory()
    request = factory.post('/api/v1/admin/employment/import/')
    request.user = user
    request.FILES = {'file': ContentFile(b'', name=file_name)}
    request.data = {'mode': mode}
    
    # Вызов метода импорта
    view = EmploymentImportExportViewSet()
    view.request = request
    
    try:
        result = view._process_import_data(request, data_rows, mode)
        return result
    except Exception as e:
        logger.error(f"Ошибка при асинхронном импорте: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)
