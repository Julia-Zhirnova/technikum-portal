import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestSidebarRoleHeader:
    """Тесты заголовка X-Active-Role"""
    
    def setup_method(self):
        """Создаём роли"""
        self.role_student, _ = Role.objects.get_or_create(id_role='student', name='Студент')
        self.role_teacher, _ = Role.objects.get_or_create(id_role='teacher', name='Преподаватель')
        self.role_curator, _ = Role.objects.get_or_create(id_role='curator', name='Куратор')
        self.role_admin, _ = Role.objects.get_or_create(id_role='admin', name='Администратор')
    
    def test_request_without_role_header_is_rejected(self):
        """Запрос без заголовка X-Active-Role отклоняется"""
        user = User.objects.create_user(email='student_no_header@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        # НЕ устанавливаем заголовок X-Active-Role
        
        response = client.get('/api/student/profile/')
        # Должен вернуть 403 Forbidden
        assert response.status_code == 403, f"Запрос без заголовка X-Active-Role должен быть отклонён, получен {response.status_code}"
    
    def test_request_with_wrong_role_header_is_rejected(self):
        """Запрос с неправильным заголовком X-Active-Role отклоняется"""
        user = User.objects.create_user(email='student_wrong_role@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        # Устанавливаем неправильный заголовок (студент пытается притвориться преподавателем)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'teacher'
        
        # Пытаемся получить доступ к преподавательскому эндпоинту
        response = client.get('/api/teacher/statements/')
        # Должен вернуть 403 Forbidden
        assert response.status_code == 403, f"Запрос с неправильной ролью должен быть отклонён, получен {response.status_code}"
    
    def test_student_with_correct_role_header_can_access_notifications(self):
        """Студент с правильным заголовком X-Active-Role может получить доступ к уведомлениям"""
        user = User.objects.create_user(email='student_correct@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        # Используем /api/student/notifications/, который не требует связанного объекта Student
        response = client.get('/api/student/notifications/')
        # Должен вернуть 200 или 404, но не 403 (permission прошёл)
        assert response.status_code in [200, 404], f"Студент должен иметь доступ к уведомлениям, получен {response.status_code}"
    
    def test_curator_with_correct_role_header_can_access_group(self):
        """Куратор с правильным заголовком X-Active-Role может получить доступ к группе"""
        user = User.objects.create_user(email='curator_correct@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_curator)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'curator'
        
        response = client.get('/api/curator/group/')
        # Должен вернуть 200 или 404 (если группа не назначена), но не 403
        assert response.status_code in [200, 404], f"Куратор должен иметь доступ к группе, получен {response.status_code}"
    
    def test_teacher_with_correct_role_header_can_access_statements(self):
        """Преподаватель с правильным заголовком X-Active-Role может получить доступ к ведомостям"""
        user = User.objects.create_user(email='teacher_correct@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_teacher)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'teacher'
        
        response = client.get('/api/teacher/statements/')
        # Должен вернуть 200 или 404 (если ведомостей нет), но не 403
        assert response.status_code in [200, 404], f"Преподаватель должен иметь доступ к ведомостям, получен {response.status_code}"
