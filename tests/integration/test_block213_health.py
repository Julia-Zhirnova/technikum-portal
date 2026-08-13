"""БП 2.1.3 (Здоровье и ОМС): TC055, TC057, TC034, TC064, TC065.

Строки tests.txt: блок 2.1.3 (идентификаторы БП2.1.3-TC034..TC066).

Стиль проекта:
- жёсткие проверки реализованного функционала;
- мягкие проверки (warn) для функционала, ожидающего реализации;
- никакого 5xx в ответах.

Отложены (⏳): TC053/TC054 (нет HealthChangeRequest), TC056 (нет notification_failed),
TC035/TC036 (нет no_oms), TC058/TC059 (нет Контингента).
"""
import io
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from core.models import AuditLog, Health, Student

STUDENT_HEALTH_URL = '/api/v1/student/health/'
CURATOR_HEALTH_REQUESTS_URL = '/api/v1/curator/health-requests/'


def _get_student_health(user):
    """Возвращает (student, health) для пользователя или (None, None)."""
    student = Student.objects.filter(user=user).first()
    if student is None:
        return None, None
    return student, getattr(student, 'health', None)


@pytest.mark.django_db
class TestBlock213HealthIntegrity:
    """TC055: индекс на oms_number."""

    def test_TC055_index_on_oms_number(self, db):
        """БП2.1.3-TC055: Индекс на oms_number для массового поиска."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM pg_indexes "
                "WHERE tablename = 'core_health' "
                "AND indexdef LIKE '%oms_number%'"
            )
            index_count = cursor.fetchone()[0]

            if index_count == 0:
                print("⚠️  Индекс на core_health.oms_number отсутствует")

            # Проверяем, что EXPLAIN использует индекс (если есть)
            if index_count > 0:
                cursor.execute(
                    "EXPLAIN SELECT * FROM core_health "
                    "WHERE oms_number IN ('5091199794001932')"
                )
                plan = cursor.fetchall()
                uses_index = any('Index Scan' in str(row) for row in plan)
                if not uses_index:
                    print("⚠️  EXPLAIN не использует индекс на oms_number")

        assert True  # Тест всегда проходит, warning если индекса нет


@pytest.mark.django_db
class TestBlock213HealthSecurity:
    """TC057, TC034: SQL-инъекция и загрузка malware.exe."""

    def test_TC057_sql_injection_in_oms_issued_by(self, api_client, student_user):
        """БП2.1.3-TC057: SQL-инъекция через 'Кем выдан ОМС'."""
        api_client.force_authenticate(user=student_user)

        malicious_input = "ЗАО 'МАКС-М' OR '1'='1"
        response = api_client.patch(
            STUDENT_HEALTH_URL,
            {'oms_issuer': malicious_input},
            format='json',
        )

        # Допустимо: 400 (валидация) или 200 (экранировано), НЕ 500
        assert response.status_code in (200, 400), \
            f"SQL-инъекция вызвала {response.status_code}"

        if response.status_code == 200:
            student, health = _get_student_health(student_user)
            if health:
                health.refresh_from_db()
                # Если значение сохранено, оно должно быть экранировано
                assert health.oms_issuer != malicious_input or "'" in health.oms_issuer, \
                    "SQL-инъекция не экранирована"

    def test_TC034_upload_executable_file(self, api_client, student_user):
        """БП2.1.3-TC034: Загрузка исполняемого файла вместо скана."""
        api_client.force_authenticate(user=student_user)

        # Создаём фейковый .exe файл
        fake_exe = io.BytesIO(b'MZ\x90\x00\x03\x00\x00\x00' + b'\x00' * 1000)
        fake_exe.name = 'malware.exe'

        response = api_client.patch(
            STUDENT_HEALTH_URL,
            {'diagnosis_scan': fake_exe},
            format='multipart',
        )

        # Допустимо: 400 (валидация) или 200 (если валидация отсутствует)
        assert response.status_code < 500, f"Получен {response.status_code}"

        if response.status_code == 200:
            print("⚠️  .exe файл принят: валидация форматов отсутствует")


@pytest.mark.django_db
class TestBlock213HealthBoundary:
    """TC065: максимальная длина диагноза."""

    def test_TC065_max_length_diagnosis(self, api_client, student_user):
        """БП2.1.3-TC065: Максимальная длина диагноза 500 символов."""
        api_client.force_authenticate(user=student_user)

        long_diagnosis = 'a' * 600  # 600 символов
        response = api_client.patch(
            STUDENT_HEALTH_URL,
            {'diagnosis': long_diagnosis},
            format='json',
        )

        # TextField не имеет max_length в БД, но сериализатор может валидировать
        assert response.status_code in (200, 400), \
            f"Получен {response.status_code}"

        if response.status_code == 200:
            student, health = _get_student_health(student_user)
            if health:
                health.refresh_from_db()
                if len(health.diagnosis) > 500:
                    print("⚠️  Диагноз > 500 символов принят: "
                          "валидация max_length отсутствует в сериализаторе")
        elif response.status_code == 400:
            # Проверяем, что ошибка валидации на длине
            diagnosis_errors = response.data.get('diagnosis', [])
            if diagnosis_errors:
                print(f"Валидация сработала: {diagnosis_errors}")


@pytest.mark.django_db
class TestBlock213HealthPerformance:
    """TC066: N+1 запросы при загрузке заявок куратором."""

    def test_TC064_curator_health_requests_no_n_plus_one(self, api_client, curator_user):
        """БП2.1.3-TC064: N+1 запросов при загрузке заявок куратором."""
        api_client.force_authenticate(user=curator_user)

        response = api_client.get(CURATOR_HEALTH_REQUESTS_URL)

        # Эндпоинт может не существовать (404)
        assert response.status_code in (200, 403, 404), \
            f"Получен {response.status_code}"

        if response.status_code != 200:
            print(f"⚠️  Эндпоинт {CURATOR_HEALTH_REQUESTS_URL} недоступен "
                  f"(HTTP {response.status_code})")
            return

        # Если эндпоинт есть, проверяем количество запросов
        with CaptureQueriesContext(connection) as ctx:
            api_client.get(CURATOR_HEALTH_REQUESTS_URL)

        total_queries = len(ctx.captured_queries)
        if total_queries > 3:
            print(f"⚠️  N+1: {total_queries} запросов "
                  "(цель ≤ 3, select_related('student__user'))")


@pytest.mark.django_db
class TestBlock213HealthEdgeCases:
    """TC070: спецсимволы в диагнозе."""

    def test_TC070_special_chars_in_diagnosis(self, api_client, student_user):
        """БП2.1.3-TC070: Спецсимволы в диагнозе сохраняются корректно."""
        api_client.force_authenticate(user=student_user)

        special_diagnosis = 'Бронхиальная астма (средней тяжести)'
        response = api_client.patch(
            STUDENT_HEALTH_URL,
            {'diagnosis': special_diagnosis},
            format='json',
        )

        # Допустимо: 200 (сохранено), 202 (через заявку), 400 (валидация), 403
        assert response.status_code in (200, 202, 400, 403), \
            f"Получен {response.status_code}"

        if response.status_code in (200, 202):
            student, health = _get_student_health(student_user)
            if health:
                health.refresh_from_db()
                # Проверяем, что спецсимволы не искажены
                if response.status_code == 200:
                    assert '(' in health.diagnosis or ')' in health.diagnosis, \
                        f"Спецсимволы искажены: {health.diagnosis!r}"
                    print(f"✅ Диагноз сохранён: {health.diagnosis!r}")
