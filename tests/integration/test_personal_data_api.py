import pytest
import io
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import (
    User, Student, Passport, Health, Military, Family, 
    FamilyMember, EducationInstitution, Campus, Specialty, 
    Qualification, Order, Group
)
from datetime import date


def create_test_student(user, snils='182-530-946 72', birth_date=None):
    """Вспомогательная функция для создания студента с обязательными связями"""
    if birth_date is None:
        birth_date = date(2007, 7, 7)
    
    campus, _ = Campus.objects.get_or_create(id_campus='main', defaults={'address': 'Test Address'})
    specialty, _ = Specialty.objects.get_or_create(id_specialty='09.02.07', defaults={'name': 'Информационные системы'})
    qualification, _ = Qualification.objects.get_or_create(specialty=specialty, defaults={'name': 'Программист'})
    group, _ = Group.objects.get_or_create(
        id_group='ИС-24',
        defaults={
            'qualification': qualification,
            'campus': campus,
            'year_start': 2024,
            'year_end': 2028,
            'duration': '3 года 10 месяцев',
            'form': 'очная',
            'financing': 'бюджет'
        }
    )
    order, _ = Order.objects.get_or_create(
        id_order='1-2024',
        defaults={
            'number': '1',
            'date': '2024-09-01',
            'name': 'О зачислении',
            'type': 'зачисление'
        }
    )
    
    student = Student.objects.create(
        user=user,
        snils=snils,
        group=group,
        order=order,
        birth_date=birth_date,
        birth_place='Москва',
        gender='м',
        phone='89997776655'
    )
    return student


@pytest.mark.django_db
class TestStudentProfileAPI:
    """Тесты API профиля студента"""
    def setup_method(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(
            email='student_profile@test.ru',
            password='student2026',
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович'
        )
        self.student = create_test_student(self.student_user)
        self.client.force_authenticate(user=self.student_user)
        self.client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'

    def test_get_student_profile(self):
        """Получение профиля студента"""
        url = reverse('student-profile')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data['snils'] == '182-530-946 72'

    def test_update_student_profile_valid(self):
        """Обновление профиля с валидными данными"""
        url = reverse('student-profile')
        payload = {'phone': '89998887766'}
        response = self.client.patch(url, payload, format='json')
        assert response.status_code == 200
        self.student.refresh_from_db()
        assert self.student.phone == '89998887766'

    def test_update_student_profile_invalid_snils(self):
        """Обновление профиля с невалидным СНИЛС"""
        url = reverse('student-profile')
        payload = {'snils': '182-530-946 99'}
        response = self.client.patch(url, payload, format='json')
        assert response.status_code == 400
        assert 'снилс' in str(response.data).lower()

    def test_duplicate_snils_rejected(self):
        """Дубликат СНИЛС отклоняется"""
        user2 = User.objects.create_user(email='student2@test.ru', password='pwd')
        create_test_student(user2, snils='222-333-444 16')
        url = reverse('student-profile')
        payload = {'snils': '222-333-444 16'}
        response = self.client.patch(url, payload, format='json')
        assert response.status_code == 400
        assert 'существует' in str(response.data).lower() or 'зарегистрирован' in str(response.data).lower()


@pytest.mark.django_db
class TestPassportAPI:
    """Тесты API паспорта"""
    def setup_method(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(email='passport@test.ru', password='pwd')
        self.student = create_test_student(self.student_user)
        self.client.force_authenticate(user=self.student_user)
        self.client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'

    def test_create_passport_rf(self):
        url = reverse('student-passport')
        payload = {
            'series_number': '4619686868', 'issue_date': '2023-07-07',
            'issuer': 'ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ', 'unit_code': '500-066',
            'region_city': 'обл. Московская, г. Люберцы'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]

    def test_create_passport_issue_before_14(self):
        url = reverse('student-passport')
        payload = {
            'series_number': '4619686868', 'issue_date': '2020-01-01',
            'issuer': 'ГУ МВД', 'unit_code': '500-066',
            'region_city': 'Москва'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code == 400
        assert '14' in str(response.data)

    def test_create_foreign_passport(self):
        url = reverse('student-passport')
        payload = {
            'is_foreigner': True, 'series_number': 'AB12345XY67890',
            'issue_date': '2023-01-01', 'issuer': 'Foreign Authority',
            'region_city': 'Москва'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]


@pytest.mark.django_db
class TestHealthAPI:
    """Тесты API здоровья"""
    def setup_method(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(email='health@test.ru', password='pwd')
        self.student = create_test_student(self.student_user)
        self.client.force_authenticate(user=self.student_user)
        self.client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'

    def test_create_health_healthy(self):
        url = reverse('student-health')
        payload = {
            'status': 'практически_здоров', 'oms_number': '5091199794001932',
            'oms_date': '2020-01-01', 'oms_issuer': 'ЗАО "МАКС-М"'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]

    def test_create_health_chronic_without_diagnosis(self):
        url = reverse('student-health')
        payload = {'status': 'хронические_заболевания', 'diagnosis': ''}
        response = self.client.post(url, payload, format='json')
        assert response.status_code == 400
        assert 'диагноз' in str(response.data).lower()

    def test_create_health_invalid_oms(self):
        url = reverse('student-health')
        payload = {'status': 'практически_здоров', 'oms_number': '12345'}
        response = self.client.post(url, payload, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestFamilyAPI:
    """Тесты API семьи"""
    def setup_method(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(email='family@test.ru', password='pwd')
        self.student = create_test_student(self.student_user)
        self.client.force_authenticate(user=self.student_user)
        self.client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'

    def test_create_family(self):
        url = reverse('student-family')
        payload = {
            'minors_count': 2, 'adults_count': 2, 'status': 'полная',
            'housing_type': 'в_собственном_жилье_с_родителями'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]

    def test_create_family_negative_count(self):
        url = reverse('student-family')
        payload = {
            'minors_count': -1, 'adults_count': 2, 'status': 'полная',
            'housing_type': 'в_собственном_жилье_с_родителями'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_add_family_member(self):
        # Сначала создаём семью
        family_url = reverse('student-family')
        self.client.post(family_url, {
            'minors_count': 2, 'adults_count': 2, 'status': 'полная',
            'housing_type': 'в_собственном_жилье_с_родителями'
        }, format='json')
        
        url = reverse('student-family-members')
        payload = {
            'relation': 'мать', 'full_name': 'Иванова Анна Ивановна',
            'birth_date': '1977-07-07', 'education': 'Высшее',
            'workplace': 'ООО "Транском"', 'phone': '89997776655'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]

    def test_add_two_priority_contacts(self):
        # Сначала создаём семью
        family_url = reverse('student-family')
        self.client.post(family_url, {
            'minors_count': 2, 'adults_count': 2, 'status': 'полная',
            'housing_type': 'в_собственном_жилье_с_родителями'
        }, format='json')
        
        url = reverse('student-family-members')
        payload1 = {'relation': 'мать', 'full_name': 'Иванова Анна', 'is_priority_contact': True}
        self.client.post(url, payload1, format='json')
        
        payload2 = {'relation': 'отец', 'full_name': 'Иванов Иван', 'is_priority_contact': True}
        response = self.client.post(url, payload2, format='json')
        assert response.status_code == 400
        assert 'приоритетный' in str(response.data).lower()


@pytest.mark.django_db
class TestEducationAPI:
    """Тесты API учебного заведения"""
    def setup_method(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(email='education@test.ru', password='pwd')
        self.student = create_test_student(self.student_user)
        self.client.force_authenticate(user=self.student_user)
        self.client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'

    def test_create_education_institution(self):
        url = reverse('student-education')
        payload = {
            'name': 'МБОУ "Гимназия № 5"', 'type': 'гимназия',
            'profile': 'Физико-математический', 'graduation_date': '2020-07-07'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code in [200, 201]

    def test_create_education_graduation_before_birth(self):
        url = reverse('student-education')
        payload = {
            'name': 'МБОУ "Гимназия № 5"', 'type': 'гимназия',
            'graduation_date': '2000-07-07'
        }
        response = self.client.post(url, payload, format='json')
        assert response.status_code == 400
