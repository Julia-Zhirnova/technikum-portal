import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()

@pytest.mark.django_db
class TestForcePasswordChange:
    
    def test_force_change_password_success(self):
        user = User.objects.create_user(email='force@test.ru', password='OldPass123!', requires_password_change=True)
        Role.objects.create(id_role='student', name='Студент')
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'NewSuperPass123!'
        })
        
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.requires_password_change is False
        assert user.check_password('NewSuperPass123!') is True

    def test_force_change_password_weak_password(self):
        user = User.objects.create_user(email='weak@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': '12345678',
            'confirm_password': '12345678'
        })
        
        assert response.status_code == 400
        assert 'new_password' in response.data

    def test_force_change_password_same_as_current(self):
        user = User.objects.create_user(email='same@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'OldPass123!',
            'confirm_password': 'OldPass123!'
        })
        
        assert response.status_code == 400
        assert 'Новый пароль не должен совпадать с текущим' in str(response.data)

    def test_force_change_password_mismatch(self):
        user = User.objects.create_user(email='mismatch@test.ru', password='OldPass123!', requires_password_change=True)
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/auth/force-change-password/', {
            'new_password': 'NewSuperPass123!',
            'confirm_password': 'DifferentPass123!'
        })
        
        assert response.status_code == 400
        assert 'Пароли не совпадают' in str(response.data)
