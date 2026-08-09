"""Celery-задачи для модуля accounts.

Примеры задач:
- add_numbers: тестовая задача для проверки инфраструктуры
- send_test_email: отправка тестового email (шаблон для БП 1.4)

Использование:
    from accounts.tasks import add_numbers
    result = add_numbers.delay(2, 3)
    print(result.get(timeout=5))  # 5
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def add_numbers(self, x: int, y: int) -> int:
    """Тестовая задача: сложение двух чисел.
    
    Используется для проверки работоспособности Celery infrastructure.
    """
    logger.info(f"add_numbers({x}, {y}) выполнен")
    return x + y


@shared_task(bind=True, max_retries=3)
def send_test_email(self, recipient_email: str, subject: str, body: str) -> bool:
    """Отправка тестового email.
    
    Шаблон для реальных задач отправки email в БП 1.4 (recovery),
    БП 3.3 (DOCX), БП 5.4 (XLSX отчёты).
    
    В тестовой среде (EMAIL_BACKEND = 'locmem') email не отправляется реально.
    """
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email отправлен: {recipient_email}")
        return True
    except Exception as exc:
        logger.error(f"Ошибка отправки email на {recipient_email}: {exc}")
        # Retry с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_password_recovery_email(self, user_id: int, recovery_token: str) -> bool:
    """Отправка email для восстановления пароля (БП 1.4).
    
    Args:
        user_id: ID пользователя
        recovery_token: одноразовый токен для восстановления
    
    Returns:
        True при успехе, False при ошибке
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(pk=user_id)
        recovery_url = f"{settings.FRONTEND_URL}/recovery/confirm/?token={recovery_token}"
        
        send_mail(
            subject='Восстановление пароля — ТехноПортал',
            message=(
                f'Здравствуйте, {user.first_name}!\n\n'
                f'Вы запросили восстановление пароля. Перейдите по ссылке:\n'
                f'{recovery_url}\n\n'
                f'Ссылка действительна 15 минут.\n\n'
                f'Если вы не запрашивали восстановление, проигнорируйте это письмо.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Recovery email отправлен: {user.email}")
        return True
    except User.DoesNotExist:
        logger.error(f"Пользователь {user_id} не найден")
        return False
    except Exception as exc:
        logger.error(f"Ошибка отправки recovery email: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
