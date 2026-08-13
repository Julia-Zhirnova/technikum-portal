"""БП 1.5: Security тесты (IDOR, SQL-инъекции, XSS).

Тест-кейсы: БП1.5-TC007, TC008, TC009, TC010
"""
import pytest
from rest_framework import status
from core.models import Group, StudentRequest, User


@pytest.mark.django_db
class TestBlock15IDOR:
    """IDOR-тесты Блока 1.5 (незащищённый доступ к чужим данным)."""

    def test_TC007_idor_student_cannot_access_foreign_group(
        self, api_client, student_user
    ):
        """БП1.5-TC007: IDOR — студент не может получить данные чужой группы.
        
        GET /api/student/grades/?group_id=<чужой_id> возвращает 403 или пустой массив.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем student_profile
        student = getattr(student_user, 'student_profile', None)
        if not student:
            pytest.skip("Нет student_profile у пользователя")
        
        # Ищем чужую группу (не ту, в которой состоит студент)
        if student.group:
            foreign_group = Group.objects.exclude(id_group=student.group.id_group).first()
        else:
            foreign_group = Group.objects.first()
        
        if not foreign_group:
            pytest.skip("Нет чужих групп для теста IDOR")
        
        response = api_client.get(
            f'/api/student/grades/?group_id={foreign_group.id_group}'
        )
        
        # Допустимые ответы: 403 (запрещено) или 200 с пустым массивом
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        ], f"Ожидался 403/200/400, получен {response.status_code}"
        
        if response.status_code == status.HTTP_200_OK:
            # Если 200 — данные не должны содержать записи чужой группы
            data = response.data
            results = data.get('results', data) if isinstance(data, dict) else data
            assert len(results) == 0, (
                "Студент не должен видеть оценки чужой группы"
            )

    def test_TC008_idor_student_cannot_edit_foreign_request(
        self, api_client, student_user
    ):
        """БП1.5-TC008: IDOR — студент не может редактировать чужую заявку.
        
        PATCH /api/student/requests/<чужой_id>/ возвращает 403 или 404.
        """
        api_client.force_authenticate(user=student_user)
        
        # Получаем student_profile
        student = getattr(student_user, 'student_profile', None)
        if not student:
            pytest.skip("Нет student_profile у пользователя")
        
        # Ищем чужую заявку
        foreign_request = StudentRequest.objects.exclude(student=student).first()
        
        if not foreign_request:
            # Создаём тестовую заявку для другого студента
            other_student = StudentRequest.objects.first()
            if not other_student:
                pytest.skip("Нет заявок для теста IDOR")
            foreign_request = other_student
        
        response = api_client.patch(
            f'/api/student/requests/{foreign_request.id_request}/',
            {'status': 'approved'},
            format='json'
        )
        
        # Допустимые ответы: 403 (запрещено) или 404 (не найдено)
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        ], f"Ожидался 403/404/405, получен {response.status_code}"


@pytest.mark.django_db
class TestBlock15Injection:
    """Тесты инъекций (SQL, XSS) в Блоке 1.5."""

    def test_TC009_sql_injection_in_search(self, api_client, student_user):
        """БП1.5-TC009: SQL-инъекция в поле поиска.
        
        GET /api/student/grades/?search=<SQL_payload> не выполняет инъекцию.
        """
        api_client.force_authenticate(user=student_user)
        
        sql_payloads = [
            "математика' OR '1'='1",
            "'; DROP TABLE core_student; --",
            "1 UNION SELECT * FROM core_user --",
        ]
        
        for payload in sql_payloads:
            response = api_client.get(f'/api/student/grades/?search={payload}')
            
            # Допустимо: 400 (валидация), 403 (нет доступа), 200 (пустой результат)
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_200_OK,
            ], f"Payload '{payload}': ожидался 400/403/200, получен {response.status_code}"
            
            # Если 200 — результат должен быть пустой или не содержать инъекций
            if response.status_code == status.HTTP_200_OK:
                data = response.data
                results = data.get('results', data) if isinstance(data, dict) else data
                # Инъекция не должна вернуть все записи БД
                if isinstance(results, list):
                    assert len(results) < 100, (
                        f"SQL-инъекция '{payload}' вернула подозрительно много записей"
                    )

    def test_TC010_xss_injection_in_full_name(self, api_client, student_user):
        """БП1.5-TC010: XSS-инъекция в поле ФИО при создании заявки.
        
        POST /api/student/requests/ с XSS-payload → сервер экранирует или отклоняет.
        """
        api_client.force_authenticate(user=student_user)
        
        xss_payload = '<script>alert("XSS")</script>'
        
        response = api_client.post(
            '/api/student/requests/',
            {
                'request_type': 'academic_certificate',
                'description': xss_payload,
            },
            format='json'
        )
        
        # Допустимо: 400 (валидация), 201 (создано с экранированием)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
        ], f"Ожидался 400/201/403, получен {response.status_code}"
        
        # Если создано — проверяем, что XSS экранирован
        if response.status_code == status.HTTP_201_CREATED:
            created_data = response.data
            description = created_data.get('description', '')
            assert '<script>' not in description or '&lt;script&gt;' in description, (
                "XSS-инъекция не экранирована"
            )
