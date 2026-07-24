import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()

@pytest.mark.django_db
class TestUIThemeAndHeader:
    def setup_method(self):
        self.role_admin, _ = Role.objects.get_or_create(id_role='admin', name='Администратор')
        self.user = User.objects.create_user(
            email='ui_test@test.ru', 
            password='Pass123!',
            first_name='Иван',
            last_name='Петров',
            middle_name='Сергеевич'
        )
        UserRole.objects.create(user=self.user, role=self.role_admin)

    def test_full_name_in_profile_response(self):
        """Проверяем, что API возвращает полное ФИО для шапки"""
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.get('/api/user/profile/')
        assert response.status_code == 200
        data = response.json()
        assert data['first_name'] == 'Иван'
        assert data['last_name'] == 'Петров'
        assert data['middle_name'] == 'Сергеевич'

    def test_campus_data_available_for_footer(self):
        """Проверяем, что данные корпусов доступны для подвала"""
        from core.models import Campus
        # Создаем тестовый корпус, если нет
        campus, created = Campus.objects.get_or_create(
            id_campus='TEST-CAMPUS',
            defaults={'address': 'г. Люберцы, Тестовая ул., д. 1'}
        )
        
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.get('/api/campuses/')
        assert response.status_code == 200
        campuses = response.json()['data']
        assert any(c['id'] == 'TEST-CAMPUS' for c in campuses)
