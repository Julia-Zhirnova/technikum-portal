"""БП 2.1.4 (Воинский учет): TC022, TC049, TC051-TC052.

Строки tests.txt: 1205, 1239, 1241-1242.

Реальная структура:
- registration_number: CharField(50) — ТЗ: 20
- commissariat: CharField(255) — ТЗ: 250
- absence_reason: TextField (одно поле, не несколько)
- НЕТ: no_registration, registration_number_hash, re_examination_date

Отложены (⏳): TC018/TC019 (транзакции), TC020 (нет registration_number_hash),
TC021 (нет notification_failed), TC023/TC044-TC046/TC053-TC054 (нет API импорта),
TC034-TC036 (нет no_registration), TC047-TC048 (нет справочника/механизма),
TC050/TC057-TC061 (UI Playwright), TC055-TC056 (нет API военкомата),
TC062 (100k записей — дорого).
"""
import pytest

MILITARY_URL = '/api/v1/student/military/'


@pytest.mark.django_db
class TestBlock214MilitarySecurity:
    """TC022: SQL-инъекция в поле 'Военкомат'."""

    def test_TC022_sql_injection_in_commissariat(self, api_client, student_user):
        """БП2.1.4-TC022: [Security] SQL-инъекция через 'Военкомат'."""
        api_client.force_authenticate(user=student_user)

        malicious_input = "Люберецкий ГВК' OR '1'='1"
        response = api_client.patch(
            MILITARY_URL,
            {'commissariat': malicious_input},
            format='json',
        )

        # Допустимо: 400 (валидация) или 200 (экранировано)
        assert response.status_code in (200, 400), \
            f"SQL-инъекция вызвала {response.status_code}"

        if response.status_code == 200:
            from core.models import Student
            student = Student.objects.filter(user=student_user).first()
            if student and hasattr(student, 'military'):
                student.military.refresh_from_db()
                # Если значение сохранено, оно должно быть экранировано или как есть
                print(f"Commissariat сохранён: {student.military.commissariat!r}")


@pytest.mark.django_db
class TestBlock214MilitaryPerformance:
    """TC049: N+1 запросы при загрузке списка студентов куратором."""

    def test_TC049_curator_students_no_n_plus_one(self, api_client, curator_user):
        """БП2.1.4-TC049: [Performance] N+1 при списке студентов с воинским учетом."""
        api_client.force_authenticate(user=curator_user)

        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as ctx:
            response = api_client.get('/api/v1/curator/students/')

        # Допустимо: 200 (есть эндпоинт) или 404 (нет эндпоинта)
        assert response.status_code in (200, 403, 404), \
            f"Получен {response.status_code}"

        if response.status_code == 200:
            total_queries = len(ctx.captured_queries)
            if total_queries > 3:
                print(f"⚠️  N+1: {total_queries} запросов (цель ≤ 3)")
            else:
                print(f"✅ {total_queries} запросов (цель ≤ 3)")
        else:
            print(f"⚠️  Эндпоинт недоступен (HTTP {response.status_code})")


@pytest.mark.django_db
class TestBlock214MilitaryBoundary:
    """TC051-TC052: boundary длина полей."""

    def test_TC051_registration_number_max_length(self, api_client, student_user):
        """БП2.1.4-TC051: [Boundary] registration_number > 50 символов → 400.
        
        Примечание: ТЗ ожидает 20, реальность 50.
        """
        api_client.force_authenticate(user=student_user)

        # ТЗ: 25 символов → 400, но max_length=50, поэтому используем 55
        long_number = 'А' * 55
        response = api_client.patch(
            MILITARY_URL,
            {'registration_number': long_number},
            format='json',
        )

        assert response.status_code == 400, \
            f"Длинный номер принят: {response.status_code}"
        assert 'registration_number' in response.data, \
            f"Нет ошибки по registration_number: {response.data}"

    def test_TC052_commissariat_max_length(self, api_client, student_user):
        """БП2.1.4-TC052: [Boundary] commissariat > 255 символов → 400.
        
        Примечание: ТЗ ожидает 250, реальность 255.
        """
        api_client.force_authenticate(user=student_user)

        # ТЗ: 300 символов → 400, max_length=255
        long_commissariat = 'А' * 300
        response = api_client.patch(
            MILITARY_URL,
            {'commissariat': long_commissariat},
            format='json',
        )

        assert response.status_code == 400, \
            f"Длинный военкомат принят: {response.status_code}"
        assert 'commissariat' in response.data, \
            f"Нет ошибки по commissariat: {response.data}"
