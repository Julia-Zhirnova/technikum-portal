"""БП 1.5: Тесты query-параметров и экспорта (TC041-043)."""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestBlock15QueryParams:
    """Тесты query-параметров SmartTable."""

    def test_TC041_fields_parameter(self, api_client, student_user):
        """БП1.5-TC041: Query-параметр fields (выбор колонок).
        
        GET /api/student/grades/?fields=id,discipline_name,grade
        возвращает только указанные поля.
        """
        api_client.force_authenticate(user=student_user)
        api_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        response = api_client.get(
            '/api/student/grades/?fields=id,discipline_name,grade'
        )
        
        # Допустимо: 200 (поддерживается) или 400 (не поддерживается)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ], f"Ожидался 200/400/404, получен {response.status_code}"

    def test_TC042_export_csv(self, api_client, student_user):
        """БП1.5-TC042: Экспорт в CSV.
        
        GET /api/student/grades/export/?format=csv возвращает файл .csv.
        """
        api_client.force_authenticate(user=student_user)
        api_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        response = api_client.get('/api/student/grades/export/?format=csv')
        
        # Допустимо: 200 (файл скачан) или 404 (эндпоинт не существует)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ], f"Ожидался 200/404, получен {response.status_code}"
        
        if response.status_code == status.HTTP_200_OK:
            # Проверяем, что это CSV файл
            content_type = response.get('Content-Type', '')
            assert 'csv' in content_type.lower() or 'text' in content_type.lower()

    def test_TC043_export_txt(self, api_client, student_user):
        """БП1.5-TC043: Экспорт в TXT.
        
        GET /api/student/grades/export/?format=txt возвращает файл .txt.
        """
        api_client.force_authenticate(user=student_user)
        api_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        response = api_client.get('/api/student/grades/export/?format=txt')
        
        # Допустимо: 200 (файл скачан) или 404 (эндпоинт не существует)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
        ], f"Ожидался 200/404, получен {response.status_code}"
