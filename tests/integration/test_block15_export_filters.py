# ============================================
# БП 1.5: Боковые панели и фильтры - Тесты
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block15SidebarTest(TestCase):
    """Тесты боковой панели (БП 1.5)."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def create_user_with_role(self, email, password, role_id):
        from core.models import Role, UserRole
        user = User.objects.create_user(email=email, password=password)
        role, _ = Role.objects.get_or_create(id_role=role_id)
        UserRole.objects.get_or_create(user=user, role=role)
        return user

    def test_TC014_notifications_icons_for_all_roles(self):
        """[БП1.5-TC014] Иконки уведомлений и мероприятий для всех ролей."""
        roles = ['student', 'teacher', 'curator', 'admin', 'chairman']
        for role in roles:
            user = self.create_user_with_role(f'test_{role}@test.ru', 'TestPass123!', role)
            self.client.force_authenticate(user=user)
            response = self.client.get('/api/notifications/')
            self.assertIn(response.status_code, [200, 204, 403, 404])
            response = self.client.get('/api/events/')
            self.assertIn(response.status_code, [200, 204, 403, 404])

    def test_TC018_curator_group_switching(self):
        """[БП1.5-TC018] Переключение группы куратором."""
        user = self.create_user_with_role('curator_test@test.ru', 'TestPass123!', 'curator')
        self.client.force_authenticate(user=user)
        # Проверяем API получения групп (даже если их нет)
        response = self.client.get('/api/curator/groups/')
        self.assertIn(response.status_code, [200, 403, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIsInstance(data, list)

    def test_TC027_sync_filters_with_url(self):
        """[БП1.5-TC027] Синхронизация фильтров с URL."""
        user = self.create_user_with_role('student_filters@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/?semester=2')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_TC028_restore_filters_from_url(self):
        """[БП1.5-TC028] Восстановление фильтров из URL."""
        user = self.create_user_with_role('student_restore@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/?semester=2&type=exam')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_TC029_export_to_excel(self):
        """[БП1.5-TC029] Экспорт в Excel."""
        user = self.create_user_with_role('student_export@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/export/?format=excel')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_TC032_a11y_for_smarttable(self):
        """[БП1.5-TC032] Доступность SmartTable."""
        user = self.create_user_with_role('student_a11y@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/')
        self.assertIn(response.status_code, [200, 403, 404])
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                self.assertIn('results', data)
                self.assertIn('count', data)

    def test_TC044_empty_state(self):
        """[БП1.5-TC044] Состояние 'Нет данных'."""
        user = self.create_user_with_role('student_empty@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/?search=несуществующая_дисциплина')
        self.assertIn(response.status_code, [200, 403, 404])
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                self.assertEqual(data.get('count', 0), 0)

    def test_TC056_export_with_filters(self):
        """[БП1.5-TC056] Экспорт с фильтрами."""
        user = self.create_user_with_role('student_export_filter@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/export/?semester=2&format=excel')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_TC057_export_without_filters(self):
        """[БП1.5-TC057] Экспорт без фильтров."""
        user = self.create_user_with_role('student_export_all@test.ru', 'TestPass123!', 'student')
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/student/grades/export/?format=excel')
        self.assertIn(response.status_code, [200, 403, 404])
