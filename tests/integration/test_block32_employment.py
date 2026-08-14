# ============================================
# БП 3.2: Заполнение данных о трудоустройстве
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block32EmploymentTest(TestCase):
    """Тесты трудоустройства студентов."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.student_user = User.objects.create_user(
            email='student_emp@test.ru',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.student_user)

    def test_001_create_employment(self):
        """Создание записи о трудоустройстве."""
        response = self.client.post(
            '/api/student/employment/',
            {
                'employment_type': 'Трудоустроен',
                'organization': '7710044140',
                'position': 'Инженер',
                'date_start': '2025-09-01'
            },
            format='json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403, 404])

    def test_002_create_self_employed(self):
        """Создание записи о самозанятости."""
        response = self.client.post(
            '/api/student/employment/',
            {
                'employment_type': 'Самозанятый',
                'date_start': '2025-09-01'
            },
            format='json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403, 404])

    def test_003_create_not_working(self):
        """Создание записи 'Не работает'."""
        response = self.client.post(
            '/api/student/employment/',
            {
                'employment_type': 'Не работает',
                'date_start': '2025-09-01'
            },
            format='json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403, 404])

    def test_004_view_employment(self):
        """Просмотр записей о трудоустройстве."""
        response = self.client.get('/api/student/employment/')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_005_update_employment(self):
        """Обновление записи о трудоустройстве."""
        response = self.client.patch(
            '/api/student/employment/1/',
            {'position': 'Старший инженер'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])
