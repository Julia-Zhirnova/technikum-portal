import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestRoleSwitching:
    def setup_method(self):
        self.role_admin, _ = Role.objects.get_or_create(id_role='admin', name='Администратор')
        self.role_teacher, _ = Role.objects.get_or_create(id_role='teacher', name='Преподаватель')
        self.role_curator, _ = Role.objects.get_or_create(id_role='curator', name='Куратор')
        self.role_student, _ = Role.objects.get_or_create(id_role='student', name='Студент')

    def test_multi_role_user_switches_to_valid_role(self):
        user = User.objects.create_user(email='multi@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_admin)
        UserRole.objects.create(user=user, role=self.role_curator)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'curator'
        
        response = client.get('/api/curator/group/')
        assert response.status_code in [200, 404]

    def test_user_denied_access_to_role_they_dont_have(self):
        user = User.objects.create_user(email='student_only@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'admin'
        
        response = client.get('/api/admin/users/')
        assert response.status_code == 403

    def test_request_without_active_role_header_is_denied(self):
        user = User.objects.create_user(email='no_header@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_admin)
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/admin/users/')
        assert response.status_code == 403

    def test_priority_role_selection_on_startup(self):
        user = User.objects.create_user(email='priority@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        UserRole.objects.create(user=user, role=self.role_teacher)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'teacher'
        
        response = client.get('/api/teacher/statements/')
        assert response.status_code in [200, 404]
