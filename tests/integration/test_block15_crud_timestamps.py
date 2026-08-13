"""БП 1.5: CRUD timestamps тест (TC017)."""
import pytest
from django.utils import timezone
from rest_framework import status
from core.models import Student, StudentRequest


@pytest.mark.django_db
class TestBlock15CRUDTimestamps:
    """CRUD timestamps тесты Блока 1.5."""

    def test_TC017_created_at_updated_at_on_crud(self, api_client, student_user):
        """БП1.5-TC017: created_at и updated_at устанавливаются автоматически.
        
        При создании записи created_at не NULL.
        При обновлении записи updated_at обновляется.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем студента
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            pytest.fail("Student не найден для пользователя")
        
        # Создаём заявку напрямую через ORM (надёжнее чем через API)
        request = StudentRequest.objects.create(
            student=student,
            request_type='academic_certificate',
            description='Тестовая заявка для TC017',
            status='pending'
        )
        
        # Проверяем created_at
        assert request.created_at is not None, "created_at должен быть установлен"
        initial_created_at = request.created_at
        initial_updated_at = request.updated_at
        
        # Ждём 1 секунду для изменения updated_at
        import time
        time.sleep(1.1)
        
        # Обновляем заявку
        request.description = 'Обновлённое описание для TC017'
        request.save()
        
        # Перечитываем из БД
        request.refresh_from_db()
        
        # Проверяем что updated_at обновился
        assert request.updated_at > initial_updated_at, (
            f"updated_at должен обновиться после save(). "
            f"Было: {initial_updated_at}, стало: {request.updated_at}"
        )
        
        # Проверяем что created_at не изменился
        assert request.created_at == initial_created_at, (
            "created_at не должен меняться при обновлении"
        )
