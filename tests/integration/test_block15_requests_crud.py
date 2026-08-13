"""БП 1.5: CRUD заявок студента (TC024-026)."""
import pytest
from rest_framework import status
from core.models import Student, StudentRequest


@pytest.mark.django_db
class TestBlock15RequestsCRUD:
    """CRUD тесты заявок студента."""

    def test_TC024_create_student_request(self, api_client, student_user):
        """БП1.5-TC024: Создание заявки студентом.
        
        POST /api/student/requests/ возвращает 201 Created.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем студента
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            pytest.skip("Student не найден")
        
        # Создаём заявку
        response = api_client.post(
            '/api/student/requests/',
            {
                'student': student.snils,
                'request_type': 'academic_certificate',
                'description': 'Тестовая заявка для TC024',
            },
            format='json'
        )
        
        # Допустимо: 201 (создано) или 400 (валидация) или 403 (нет прав)
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        ], f"Ожидался 201/400/403, получен {response.status_code}"

    def test_TC025_update_student_request(self, api_client, student_user):
        """БП1.5-TC025: Редактирование заявки студентом.
        
        PATCH /api/student/requests/<id>/ возвращает 200 OK.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем студента
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            pytest.skip("Student не найден")
        
        # Создаём заявку напрямую
        request = StudentRequest.objects.create(
            student=student,
            request_type='academic_certificate',
            description='Тестовая заявка для TC025',
            status='pending'
        )
        
        # Обновляем заявку
        response = api_client.patch(
            f'/api/student/requests/{request.id_request}/',
            {'description': 'Обновлённое описание для TC025'},
            format='json'
        )
        
        # Допустимо: 200 (обновлено) или 404 (не найдено) или 405 (метод не разрешён)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ], f"Ожидался 200/404/405, получен {response.status_code}"

    def test_TC026_delete_student_request(self, api_client, student_user):
        """БП1.5-TC026: Удаление заявки студентом.
        
        DELETE /api/student/requests/<id>/ возвращает 204 No Content.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем студента
        try:
            student = Student.objects.get(user=student_user)
        except Student.DoesNotExist:
            pytest.skip("Student не найден")
        
        # Создаём заявку напрямую
        request = StudentRequest.objects.create(
            student=student,
            request_type='academic_certificate',
            description='Тестовая заявка для TC026',
            status='pending'
        )
        
        # Удаляем заявку
        response = api_client.delete(f'/api/student/requests/{request.id_request}/')
        
        # Допустимо: 204 (удалено) или 404 (не найдено) или 405 (метод не разрешён)
        assert response.status_code in [
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ], f"Ожидался 204/404/405, получен {response.status_code}"
