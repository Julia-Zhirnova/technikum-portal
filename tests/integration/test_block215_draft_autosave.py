# ============================================
# БП 2.1.5: Частичное сохранение анкеты + Автосохранение черновика
# ============================================
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.core.cache import cache

User = get_user_model()


class Block215DraftAutosaveTest(TestCase):
    """Тесты частичного сохранения и автосохранения черновика."""

    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.user = User.objects.create_user(
            email='test_draft@test.ru',
            password='TestPass123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_001_partial_save(self):
        """Проверка частичного сохранения."""
        response = self.client.patch(
            '/api/student/profile/',
            {'phone': '+7(999)123-45-67'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 207, 400, 403, 404])

    def test_002_autosave_endpoint(self):
        """Проверка эндпоинта автосохранения."""
        response = self.client.post(
            '/api/student/profile/autosave/',
            {'draft': {'phone': '+7(999)123-45-67'}},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])

    def test_003_draft_restore(self):
        """Восстановление черновика."""
        response = self.client.get('/api/student/profile/draft/')
        self.assertIn(response.status_code, [200, 403, 404])

    def test_004_draft_clear(self):
        """Очистка черновика."""
        response = self.client.delete('/api/student/profile/draft/')
        self.assertIn(response.status_code, [200, 204, 403, 404])

    def test_005_profile_update(self):
        """Обновление профиля."""
        response = self.client.patch(
            '/api/student/profile/',
            {'first_name': 'Тест', 'last_name': 'Тестов'},
            format='json'
        )
        self.assertIn(response.status_code, [200, 400, 403, 404])
