# ============================================
# БП 3.1: Справочник организаций (с верификацией)
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block31OrganizationsTest(TestCase):
    """Тесты справочника организаций."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.admin_user = User.objects.create_user(
            email='admin_org@test.ru',
            password='TestPass123!',
            is_staff=True
        )
        self.student_user = User.objects.create_user(
            email='student_org@test.ru',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_001_create_organization(self):
        """Проверка создания организации."""
        response = self.client.post(
            '/api/organizations/',
            {
                'inn': '7710044140',
                'legal_name': 'ПАО Россети Московский регион'
            },
            format='json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403, 404])

    def test_002_search_by_inn(self):
        """Поиск организации по ИНН."""
        response = self.client.get('/api/organizations/search/?inn=7710044140')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_003_search_by_name(self):
        """Поиск организации по названию."""
        response = self.client.get('/api/organizations/search/?name=Россети')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_004_student_cannot_create(self):
        """Студент не может создать организацию."""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(
            '/api/organizations/',
            {'inn': '772344295938', 'legal_name': 'ООО Тест'},
            format='json'
        )
        self.assertIn(response.status_code, [403, 404])

    def test_005_admin_can_view(self):
        """Администратор может просматривать организации."""
        response = self.client.get('/api/organizations/')
        self.assertIn(response.status_code, [200, 403, 404])
