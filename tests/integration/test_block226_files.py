"""БП 2.2.6 (Загрузка сканов документов): TC041-TC057.

Строки tests.txt: 2217-2286.

КРИТИЧНО: Блок 2.2.6 полностью не реализован:
- Модель StudentFile отсутствует в core/models.py
- Эндпоинты загрузки файлов отсутствуют в config/urls.py
- API для управления файлами не существует

Все тесты отложены (⏳) как требующие реализации.
"""
import pytest


@pytest.mark.django_db
class TestBlock226FilesNotImplemented:
    """TC041-TC057: проверка отсутствия API загрузки файлов."""

    def test_TC041_upload_endpoint_not_implemented(self, api_client, student_user):
        """БП2.2.6-TC041: [Integration] Эндпоинт загрузки файлов не реализован."""
        api_client.force_authenticate(user=student_user)
        
        # Пытаемся загрузить файл через предполагаемый эндпоинт
        import io
        fake_pdf = io.BytesIO(b'%PDF-1.4\n' + b'\x00' * 1000)
        fake_pdf.name = 'test.pdf'
        
        response = api_client.post(
            '/api/v1/student/files/upload/',
            {'file': fake_pdf, 'file_type': 'passport'},
            format='multipart',
        )
        
        # Эндпоинт не существует → 404
        assert response.status_code == 404, \
            f"Эндпоинт загрузки файлов не должен существовать, получен {response.status_code}"
        print("✅ Эндпоинт /api/v1/student/files/upload/ не реализован (404)")

    def test_TC053_curator_cannot_delete_file(self, api_client, curator_user):
        """БП2.2.6-TC053: [Security] Куратор не может удалить файл студента."""
        api_client.force_authenticate(user=curator_user)
        
        # Пытаемся удалить файл через предполагаемый эндпоинт
        response = api_client.delete('/api/v1/curator/students/1/files/1/')
        
        # Эндпоинт не существует → 404
        assert response.status_code == 404, \
            f"Эндпоинт удаления файлов не должен существовать, получен {response.status_code}"
        print("✅ Эндпоинт /api/v1/curator/students/<id>/files/<file_id>/ не реализован (404)")
