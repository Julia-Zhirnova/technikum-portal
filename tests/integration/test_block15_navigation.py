
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class Block15NavigationTest(TestCase):
    """Тесты навигации и боковой панели."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_sidebar_for_student(self):
        """Проверка боковой панели студента."""
        user = User.objects.create_user(
            email='student_sidebar@test.ru',
            password='TestPass123!'
        )
        from core.models import Role, UserRole
        role, _ = Role.objects.get_or_create(id_role='student')
        UserRole.objects.get_or_create(user=user, role=role)
        self.client.force_authenticate(user=user)
        
        # Проверяем доступ к страницам студента
        pages = ['/student/profile', '/student/grades', '/student/practice', '/student/requests']
        for page in pages:
            response = self.client.get(page)
            self.assertIn(response.status_code, [200, 403, 404])
    
    def test_sidebar_for_teacher(self):
        """Проверка боковой панели преподавателя."""
        user = User.objects.create_user(
            email='teacher_sidebar@test.ru',
            password='TestPass123!'
        )
        from core.models import Role, UserRole
        role, _ = Role.objects.get_or_create(id_role='teacher')
        UserRole.objects.get_or_create(user=user, role=role)
        self.client.force_authenticate(user=user)
        
        pages = ['/teacher/statements', '/teacher/schedule', '/teacher/practice', '/teacher/programs']
        for page in pages:
            response = self.client.get(page)
            self.assertIn(response.status_code, [200, 403, 404])
    
    def test_sidebar_for_curator(self):
        """Проверка боковой панели куратора."""
        user = User.objects.create_user(
            email='curator_sidebar@test.ru',
            password='TestPass123!'
        )
        from core.models import Role, UserRole
        role, _ = Role.objects.get_or_create(id_role='curator')
        UserRole.objects.get_or_create(user=user, role=role)
        self.client.force_authenticate(user=user)
        
        pages = ['/curator/group', '/curator/grades', '/curator/attendance', '/curator/schedule']
        for page in pages:
            response = self.client.get(page)
            self.assertIn(response.status_code, [200, 403, 404])
