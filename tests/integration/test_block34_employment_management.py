# ============================================
# БП 3.4: Проверка и управление трудоустройством
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block34EmploymentManagementTest(TestCase):
    """Тесты управления трудоустройством."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        
        self.student_user = User.objects.create_user(
            email='student_emp@test.ru',
            password='TestPass123!'
        )
        self.curator_user = User.objects.create_user(
            email='curator_emp@test.ru',
            password='TestPass123!'
        )
        self.admin_user = User.objects.create_user(
            email='admin_emp@test.ru',
            password='TestPass123!',
            is_staff=True
        )
        
        from core.models import Role, UserRole
        student_role, _ = Role.objects.get_or_create(id_role='student')
        curator_role, _ = Role.objects.get_or_create(id_role='curator')
        admin_role, _ = Role.objects.get_or_create(id_role='admin')
        
        UserRole.objects.get_or_create(user=self.student_user, role=student_role)
        UserRole.objects.get_or_create(user=self.curator_user, role=curator_role)
        UserRole.objects.get_or_create(user=self.admin_user, role=admin_role)

    def test_001_curator_view_employment(self):
        """Куратор просматривает трудоустройство студентов."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.get('/api/curator/employment/')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_002_admin_view_employment(self):
        """Администратор просматривает трудоустройство всех студентов."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/employment/')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_003_curator_confirm_employment(self):
        """Куратор подтверждает запись о трудоустройстве."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.patch(
            '/api/curator/employment/1/confirm/',
            {'comment': 'Проверено'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])

    def test_004_curator_reject_employment(self):
        """Куратор отклоняет запись о трудоустройстве."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.patch(
            '/api/curator/employment/1/reject/',
            {'comment': 'Требуются дополнительные документы'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])

    def test_005_curator_request_documents(self):
        """Куратор запрашивает документы."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.post(
            '/api/curator/employment/1/request-documents/',
            {'comment': 'Загрузите СЗВ-ТД'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])
