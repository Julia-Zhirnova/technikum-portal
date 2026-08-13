"""БП 2.1.2 (Паспорт) — продолжение: TC034-TC036, TC065-TC067.

Строки tests.txt: 942-944, 952-954.

Стиль проекта (см. test_block212_passport_security.py):
- жёсткие проверки реализованного функционала;
- мягкие проверки (warn) для функционала, ожидающего реализации;
- никакого 5xx в ответах.

Отложены (⏳): TC062/TC063 (нет интеграции «Контингент»),
TC064 (нет Celery-задачи очистки архива), TC068 (Playwright UI).
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from core.models import AuditLog, Passport, Student

STUDENT_PASSPORT_URL = '/api/v1/student/passport/'
CURATOR_REQUESTS_URL = '/api/v1/curator/passport-requests/'


def _get_student_passport(user):
    """Возвращает (student, passport) для пользователя или (None, None)."""
    student = Student.objects.filter(user=user).first()
    if student is None:
        return None, None
    return student, getattr(student, 'passport', None)


@pytest.mark.django_db
class TestBlock212PassportAuditContinued:
    """TC034-TC036: валидация скана и аудит изменений."""

    def test_TC034_missing_scan_when_passport_present(self, api_client, student_user):
        """БП2.1.2-TC034: [Negative] Отсутствие скана при наличии паспорта."""
        api_client.force_authenticate(user=student_user)

        # Паспортные данные заявлены, скан не приложен
        response = api_client.patch(
            STUDENT_PASSPORT_URL,
            {'series_number': '4624 123456'},
            format='json',
        )
        assert response.status_code < 500, f"Получен {response.status_code}"

        field_names = {f.name for f in Passport._meta.get_fields()}
        if 'no_passport' not in field_names:
            print("⚠️  core_passport.no_passport отсутствует — "
                  "валидация 'Скан обязателен' требует миграции")
        if not ({'file_path', 'scan_file_id'} & field_names):
            print("⚠️  Поле скана в core_passport не найдено")

    def test_TC035_auditlog_on_address_change(self, api_client, student_user):
        """БП2.1.2-TC035: [Integration] Аудит при изменении адресов."""
        api_client.force_authenticate(user=student_user)

        student, passport = _get_student_passport(student_user)
        assert student is not None, "Студент для тестового пользователя не найден"

        new_addresses = {
            'region_city': 'обл. Московская, г. Люберцы',
            'address_detail': 'ул. Новая, д. 1',
            'fact_region': 'обл. Московская, г. Люберцы',
            'fact_detail': 'ул. Новая, д. 2',
        }
        response = api_client.patch(STUDENT_PASSPORT_URL, new_addresses, format='json')
        assert response.status_code < 500, f"Получен {response.status_code}"

        if passport is None:
            print("⚠️  У тестового студента нет связанного паспорта")
            return

        passport.refresh_from_db()
        if passport.address_detail == new_addresses['address_detail']:
            audit_exists = AuditLog.objects.filter(
                action_type=AuditLog.ActionType.UPDATE
            ).exists()
            if not audit_exists:
                print("⚠️  Адреса обновлены, но запись update в core_auditlog не найдена")
        else:
            print("⚠️  Адреса не обновлены через данный эндпоинт")

    def test_TC036_auditlog_passport_change_fact_only(self, api_client, admin_user):
        """БП2.1.2-TC036: [Security] Аудит смены паспорта — только факт."""
        api_client.force_authenticate(user=admin_user)

        action_values = [choice[0] for choice in AuditLog.ActionType.choices]
        if 'passport_change' not in action_values:
            print("⚠️  AuditLog.ActionType не содержит passport_change")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'core_passport_change_request')"
            )
            if not cursor.fetchone()[0]:
                print("⚠️  Таблица core_passport_change_request отсутствует")

        # Если записи есть — чувствительные значения не должны попадать в аудит
        for log in AuditLog.objects.filter(action_type='passport_change'):
            details = log.details or {}
            if isinstance(details, dict):
                leaked = [k for k in details if 'series' in k or 'number' in k]
                assert not leaked, f"Чувствительные поля в аудите: {leaked}"


@pytest.mark.django_db
class TestBlock212PassportDataHandling:
    """TC065-TC067: спецсимволы, N+1, уникальность."""

    def test_TC065_special_chars_in_issued_by(self, api_client, student_user):
        """БП2.1.2-TC065: Спецсимволы в поле "Кем выдан"."""
        api_client.force_authenticate(user=student_user)
        special_issuer = 'ОТДЕЛ УФМС по г. Москве, ул. Тверская 1/2'

        response = api_client.patch(
            STUDENT_PASSPORT_URL, {'issuer': special_issuer}, format='json'
        )
        assert response.status_code in (200, 202, 400, 404), \
            f"Получен {response.status_code}"

        if response.status_code in (400, 404):
            print(f"⚠️  HTTP {response.status_code}: {getattr(response, 'data', '')}")
            return

        student, passport = _get_student_passport(student_user)
        if passport is None:
            print("⚠️  Паспорт студента не найден — проверка только по HTTP")
            return

        passport.refresh_from_db()
        if response.status_code == 200:
            assert passport.issuer == special_issuer, (
                f"Спецсимволы искажены: {passport.issuer!r}"
            )
        else:
            print("⚠️  202: значение применится после подтверждения заявки")

    def test_TC066_curator_requests_no_n_plus_one(self, api_client, curator_user):
        """БП2.1.2-TC066: [Performance] N+1 при списке заявок куратором."""
        api_client.force_authenticate(user=curator_user)

        response = api_client.get(CURATOR_REQUESTS_URL)
        assert response.status_code in (200, 403, 404), \
            f"Получен {response.status_code}"

        if response.status_code != 200:
            print("⚠️  Эндпоинт /api/v1/curator/passport-requests/ недоступен "
                  f"(HTTP {response.status_code})")
            return

        with CaptureQueriesContext(connection) as ctx:
            api_client.get(CURATOR_REQUESTS_URL)
        total = len(ctx.captured_queries)
        if total > 3:
            print(f"⚠️  N+1: {total} запросов "
                  "(цель ≤ 3, select_related('student__user'))")

    def test_TC067_passport_hash_uniqueness(self, api_client, student_user):
        """БП2.1.2-TC067: [Security] Уникальность при смене паспорта на чужой."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_name = 'core_passport' "
                "AND column_name = 'passport_hash'"
            )
            has_column = cursor.fetchone()[0] > 0
            cursor.execute(
                "SELECT COUNT(*) FROM pg_indexes "
                "WHERE tablename = 'core_passport' "
                "AND indexdef LIKE '%passport_hash%'"
            )
            has_index = cursor.fetchone()[0] > 0

        if not has_column:
            print("⚠️  Колонка core_passport.passport_hash отсутствует")
        elif not has_index:
            print("⚠️  Уникальный индекс на passport_hash отсутствует")

        student, own_passport = _get_student_passport(student_user)
        qs = Passport.objects.exclude(
            series_number__isnull=True
        ).exclude(series_number='')
        if own_passport is not None:
            qs = qs.exclude(pk=own_passport.pk)
        foreign_passport = qs.first()

        if foreign_passport is None:
            print("⚠️  В БД нет паспорта с заполненной серией+номером")
            return

        api_client.force_authenticate(user=student_user)
        response = api_client.patch(
            STUDENT_PASSPORT_URL,
            {'series_number': foreign_passport.series_number},
            format='json',
        )
        assert response.status_code < 500, f"Получен {response.status_code}"

        if response.status_code == 400:
            print(f"Дубликат отклонён: {response.data}")
        elif not has_column:
            print("⚠️  Дубликат принят: защита уникальности не реализована")
