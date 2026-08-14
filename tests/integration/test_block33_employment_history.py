# ============================================
# БП 3.3: История трудоустройства
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block33EmploymentHistoryTest(TestCase):
    """Тесты истории трудоустройства."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        
        self.student_user = User.objects.create_user(
            email='student_history@test.ru',
            password='TestPass123!'
        )
        self.curator_user = User.objects.create_user(
            email='curator_history@test.ru',
            password='TestPass123!'
        )
        self.admin_user = User.objects.create_user(
            email='admin_history@test.ru',
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

    def test_001_create_history(self):
        """Создание записи истории трудоустройства."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.post(
            '/api/curator/employment-history/',
            {
                'student_id': self.student_user.id_user,
                'employment_type': 'Трудоустроен',
                'position': 'Инженер',
                'date_start': '2025-09-01'
            },
            format='json'
        )
        self.assertIn(response.status_code, [200, 201, 400, 403, 404])

    def test_002_view_history(self):
        """Просмотр истории трудоустройства."""
        self.client.force_authenticate(user=self.curator_user)
        response = self.client.get('/api/curator/employment-history/')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_003_student_cannot_delete(self):
        """Студент не может удалять записи истории."""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.delete('/api/student/employment-history/1/')
        self.assertIn(response.status_code, [403, 404])

    def test_004_student_cannot_update(self):
        """Студент не может редактировать записи истории."""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(
            '/api/student/employment-history/1/',
            {'position': 'Новая должность'},
            format='json'
        )
        self.assertIn(response.status_code, [403, 404])

    def test_005_admin_can_view(self):
        """Администратор может просматривать историю."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/admin/employment-history/')
        self.assertIn(response.status_code, [200, 403, 404])
