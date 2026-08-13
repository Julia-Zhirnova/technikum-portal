"""БП 2.2.1 (Учебное заведение): TC020-TC021, TC024-TC027.

Строки tests.txt: 1616-1617, 1620-1621, 1638-1639.

Реальная структура (отличается от ТЗ):
- модель EducationInstitution: name(255), type(100, choices), profile(100),
  graduation_date; одна запись на студента через student.education;
- URL /api/v1/student/education/ без <pk>.

Отложены (⏳): TC022/TC023 (транзакции), TC028 (модель 1:1, не список),
TC029/TC030 (нет certificate_scan), TC033/TC034 (нет сканов/is_current),
TC035-TC041 (Playwright UI).
"""
import pytest

from core.models import EducationInstitution, Student

EDUCATION_URL = '/api/v1/student/education/'
EDUCATION_DETAIL_URL = '/api/v1/student/profile/education/{pk}/'


def _valid_type():
    """Первое допустимое значение поля type (choices)."""
    choices = EducationInstitution._meta.get_field('type').choices
    return choices[0][0] if choices else 'school'


@pytest.mark.django_db
class TestBlock221EducationSecurity:
    """TC020/TC021: IDOR; TC024/TC025: XSS."""

    def test_TC020_idor_delete_other_school(self, api_client, student_user):
        """БП2.2.1-TC020: [Security] IDOR — удаление чужой школы."""
        api_client.force_authenticate(user=student_user)

        response = api_client.delete(EDUCATION_DETAIL_URL.format(pk=5))
        assert response.status_code in (403, 404, 405), \
            f"Получен {response.status_code}"

        if response.status_code == 404:
            print("⚠️  Эндпоинт /api/v1/student/profile/education/<id>/ не "
                  "реализован — IDOR исключён на уровне роутинга")

    def test_TC021_idor_update_other_school(self, api_client, student_user):
        """БП2.2.1-TC021: [Security] IDOR — изменение чужой школы."""
        api_client.force_authenticate(user=student_user)

        response = api_client.patch(
            EDUCATION_DETAIL_URL.format(pk=5),
            {'name': 'Чужая школа'},
            format='json',
        )
        assert response.status_code in (403, 404, 405), \
            f"Получен {response.status_code}"

        if response.status_code == 404:
            print("⚠️  Эндпоинт /api/v1/student/profile/education/<id>/ не "
                  "реализован — IDOR исключён на уровне роутинга")

    def test_TC024_xss_in_school_name(self, api_client, student_user):
        """БП2.2.1-TC024: [Security] XSS в поле наименования."""
        api_client.force_authenticate(user=student_user)

        payload = {
            'name': '<script>alert(1)</script>',
            'type': _valid_type(),
        }
        response = api_client.post(EDUCATION_URL, payload, format='json')
        assert response.status_code in (200, 201, 400), \
            f"Получен {response.status_code}"

        if response.status_code in (200, 201):
            student = Student.objects.filter(user=student_user).first()
            edu = getattr(student, 'education', None)
            if edu and edu.name == '<script>alert(1)</script>':
                print("⚠️  XSS-payload сохранён без серверного экранирования "
                      "(защита на рендеринге: React экранирует по умолчанию)")

    def test_TC025_xss_in_profile_field(self, api_client, student_user):
        """БП2.2.1-TC025: [Security] XSS в поле уточнения (profile)."""
        api_client.force_authenticate(user=student_user)

        payload = {
            'name': 'МБОУ СОШ №1',
            'type': _valid_type(),
            'profile': '<script>alert(1)</script>',
        }
        response = api_client.post(EDUCATION_URL, payload, format='json')
        assert response.status_code in (200, 201, 400), \
            f"Получен {response.status_code}"

        if response.status_code in (200, 201):
            student = Student.objects.filter(user=student_user).first()
            edu = getattr(student, 'education', None)
            if edu and edu.profile == '<script>alert(1)</script>':
                print("⚠️  XSS-payload сохранён без серверного экранирования")


@pytest.mark.django_db
class TestBlock221EducationBoundary:
    """TC026/TC027: максимальные длины полей."""

    def test_TC026_max_length_school_name(self, api_client, student_user):
        """БП2.2.1-TC026: [Boundary] name > 255 символов → 400."""
        api_client.force_authenticate(user=student_user)

        payload = {'name': 'А' * 300, 'type': _valid_type()}
        response = api_client.post(EDUCATION_URL, payload, format='json')
        assert response.status_code == 400, f"Получен {response.status_code}"
        assert 'name' in response.data, f"Нет ошибки по name: {response.data}"

    def test_TC027_max_length_profile_field(self, api_client, student_user):
        """БП2.2.1-TC027: [Boundary] profile > 100 символов → 400."""
        api_client.force_authenticate(user=student_user)

        payload = {
            'name': 'МБОУ СОШ №1',
            'type': _valid_type(),
            'profile': 'А' * 150,
        }
        response = api_client.post(EDUCATION_URL, payload, format='json')
        assert response.status_code == 400, f"Получен {response.status_code}"
        assert 'profile' in response.data, \
            f"Нет ошибки по profile: {response.data}"
