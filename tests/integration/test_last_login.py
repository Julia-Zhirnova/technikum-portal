"""1.1-002: после успешного входа поле last_login обновлено (SQL-проверка из спецификации)."""
import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


def test_1_1_002_last_login_updated(api_client, student_user):
    """POST /api/token/ → 200 и core_user.last_login обновлено до текущего времени."""
    student_user.set_password('student2026')
    student_user.last_login = None
    student_user.save()

    response = api_client.post(
        '/api/token/',
        {'email': student_user.email, 'password': 'student2026'},
        format='json',
    )

    assert response.status_code == 200
    student_user.refresh_from_db()
    assert student_user.last_login is not None, "last_login должен обновиться после входа"
    assert (timezone.now() - student_user.last_login).total_seconds() < 60
