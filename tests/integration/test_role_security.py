import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import User, Role, UserRole

@pytest.mark.django_db
class TestRoleSecurity:
    
    def setup_method(self):
        self.student_client = APIClient()
        self.curator_client = APIClient()
        self.admin_client = APIClient()
        
        # Создаем роли
        self.role_student = Role.objects.create(id_role='student', name='Студент')
        self.role_curator = Role.objects.create(id_role='curator', name='Куратор')
        self.role_admin = Role.objects.create(id_role='admin', name='Администратор')
        
        # Создаем пользователей
        self.student_user = User.objects.create_user(
            email='secure_student@luberteh.ru', password='student2026'
        )
        UserRole.objects.create(user=self.student_user, role=self.role_student)
        
        self.curator_user = User.objects.create_user(
            email='secure_curator@luberteh.ru', password='student2026'
        )
        UserRole.objects.create(user=self.curator_user, role=self.role_curator)
        
        self.admin_user = User.objects.create_user(
            email='secure_admin@luberteh.ru', password='student2026'
        )
        UserRole.objects.create(user=self.admin_user, role=self.role_admin)
        
        # Аутентифицируем клиентов
        self.student_client.force_authenticate(user=self.student_user)
        self.curator_client.force_authenticate(user=self.curator_user)
        self.admin_client.force_authenticate(user=self.admin_user)

    def test_1_6_3_student_cannot_access_admin(self):
        """1.6.3: Студент не может получить доступ к /api/admin/users/"""
        self.student_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        response = self.student_client.get(reverse('admin_users'))
        assert response.status_code == 403

    def test_1_6_4_student_cannot_access_teacher_statements(self):
        """1.6.4: Студент не может получить доступ к /api/teacher/statements/"""
        self.student_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        response = self.student_client.get(reverse('teacher_statements'))
        assert response.status_code == 403

    def test_1_6_5_student_cannot_access_curator_group(self):
        """1.6.5: Студент не может получить доступ к /api/curator/group/"""
        self.student_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        response = self.student_client.get(reverse('curator_group'))
        assert response.status_code == 403

    def test_1_6_11_request_without_active_role_header(self):
        """1.6.11: Запрос без заголовка X-Active-Role к защищенному эндпоинту"""
        # Не устанавливаем HTTP_X_ACTIVE_ROLE
        response = self.student_client.get(reverse('admin_users'))
        # Должен быть 403, так как нет прав админа
        assert response.status_code == 403

    def test_1_6_12_curator_access_to_own_group(self):
        """1.6.12: Куратор может получить доступ к своему эндпоинту (проверка базового доступа)"""
        self.curator_client.defaults['HTTP_X_ACTIVE_ROLE'] = 'curator'
        response = self.curator_client.get(reverse('curator_group'))
        # Если групп нет, вернет 200 с пустым списком или 404, но не 403 (если роль верная)
        assert response.status_code in [200, 404]
