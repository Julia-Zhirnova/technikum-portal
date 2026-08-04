"""Тесты модели журнала аудита AuditLog.

БП 1.1.1: Логирование и аудит действий пользователей.
Требование ФЗ-152: все операции с персональными данными должны
логироваться, журнал аудита защищён от модификации и удаления.
"""
import pytest
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestAuditLogModel:
    """Тесты базовой функциональности модели AuditLog."""

    def test_create_audit_log_entry(self, student_user):
        """Запись аудита создаётся с корректными полями."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS,
            object_type="User",
            object_id=str(student_user.pk),
            ip_address="192.168.1.100",
            details={"email": student_user.email},
        )

        assert entry.pk is not None
        assert entry.action_type == "login_success"
        assert entry.details["email"] == student_user.email
        assert entry.created_at is not None

    def test_audit_log_str_representation(self, student_user):
        """Строковое представление записи содержит тип действия."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS,
        )

        assert "login_success" in str(entry)

    def test_audit_log_update_forbidden(self, student_user):
        """Изменение существующей записи аудита запрещено (ФЗ-152)."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS,
        )
        entry.action_type = AuditLog.ActionType.DELETE

        with pytest.raises(ValidationError):
            entry.save()

    def test_audit_log_delete_forbidden(self, student_user):
        """Удаление записи аудита запрещено (ФЗ-152)."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS,
        )

        with pytest.raises(ValidationError):
            entry.delete()

    def test_audit_log_default_details(self, student_user):
        """Поле details по умолчанию — пустой словарь."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGOUT,
        )

        assert entry.details == {}

    def test_audit_log_ordering_by_created_desc(self, student_user):
        """Записи упорядочены по убыванию created_at (новые сверху)."""
        from core.models import AuditLog

        entry1 = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGIN_SUCCESS,
        )
        entry2 = AuditLog.objects.create(
            user=student_user,
            action_type=AuditLog.ActionType.LOGOUT,
        )

        entries = list(AuditLog.objects.all())
        assert entries[0].pk == entry2.pk
        assert entries[1].pk == entry1.pk

    def test_audit_log_allows_null_user(self):
        """Запись аудита создаётся без пользователя (например, анонимный вход)."""
        from core.models import AuditLog

        entry = AuditLog.objects.create(
            user=None,
            action_type=AuditLog.ActionType.LOGIN_FAIL,
            ip_address="10.0.0.1",
            details={"reason": "invalid_credentials"},
        )

        assert entry.pk is not None
        assert entry.user is None
