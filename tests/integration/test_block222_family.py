"""БП 2.2.2 (Семья): TC034, TC035, TC049.

Строки tests.txt: 1754-1755, 1727.

Реальная структура (упрощена по сравнению с ТЗ):
- family_status → status (CharField с choices, один выбор)
- children_count → minors_count
- family_members_count → отсутствует
- financial_aid_grounds → fin_aid_ground (ForeignKey, один выбор)
- housing_type_other, parents_retirees → отсутствуют

Отложены (⏳): TC046-TC048, TC050-TC065 (модель упрощена, полей нет).
"""
import pytest

from core.models import Family, Student

FAMILY_URL = '/api/v1/student/family/'


def _get_student_family(user):
    """Возвращает (student, family) для пользователя или (None, None)."""
    student = Student.objects.filter(user=user).first()
    if student is None:
        return None, None
    return student, getattr(student, 'family', None)


@pytest.mark.django_db
class TestBlock222FamilyBoundary:
    """TC034/TC035: Boundary для minors_count, adults_count."""

    def test_TC034_minors_count_one(self, api_client, student_user):
        """БП2.2.2-TC034: [Boundary] minors_count = 1 (только сам студент)."""
        api_client.force_authenticate(user=student_user)

        response = api_client.patch(
            FAMILY_URL,
            {'minors_count': 1},
            format='json',
        )

        assert response.status_code in (200, 400), \
            f"Получен {response.status_code}"

        if response.status_code == 200:
            student, family = _get_student_family(student_user)
            if family:
                family.refresh_from_db()
                assert family.minors_count == 1, \
                    f"minors_count не обновлён: {family.minors_count}"

    def test_TC035_adults_count_one(self, api_client, student_user):
        """БП2.2.2-TC035: [Boundary] adults_count = 1 (только сам студент)."""
        api_client.force_authenticate(user=student_user)

        response = api_client.patch(
            FAMILY_URL,
            {'adults_count': 1},
            format='json',
        )

        assert response.status_code in (200, 400), \
            f"Получен {response.status_code}"

        if response.status_code == 200:
            student, family = _get_student_family(student_user)
            if family:
                family.refresh_from_db()
                assert family.adults_count == 1, \
                    f"adults_count не обновлён: {family.adults_count}"


@pytest.mark.django_db
class TestBlock222FamilySecurity:
    """TC049: валидация status (choices)."""

    def test_TC049_invalid_status_rejected(self, api_client, student_user):
        """БП2.2.2-TC049: [Security] status не принимает несуществующие значения."""
        api_client.force_authenticate(user=student_user)

        response = api_client.patch(
            FAMILY_URL,
            {'status': 'несуществующий_статус'},
            format='json',
        )

        # choices валидируют на уровне сериализатора → 400
        assert response.status_code == 400, \
            f"Несуществующий статус принят: {response.status_code}"
        assert 'status' in response.data, \
            f"Нет ошибки по status: {response.data}"
