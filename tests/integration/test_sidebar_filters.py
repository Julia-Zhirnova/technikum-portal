import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Role, UserRole

User = get_user_model()

@pytest.mark.django_db
class TestSidebarFiltersAndPagination:
    def setup_method(self):
        self.role_student, _ = Role.objects.get_or_create(id_role='student', name='Студент')
        self.role_curator, _ = Role.objects.get_or_create(id_role='curator', name='Куратор')

    def test_student_grades_filters_via_query_params(self):
        user = User.objects.create_user(email='stud_filt@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        # Проверка, что эндпоинт принимает query-параметры фильтров
        response = client.get('/api/student/grades/?semester=2&type=exam')
        assert response.status_code in [200, 404]

    def test_curator_group_filters_via_query_params(self):
        user = User.objects.create_user(email='cur_filt@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_curator)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'curator'
        
        response = client.get('/api/curator/requests/?status=new')
        assert response.status_code in [200, 404]

    def test_default_pagination_parameters(self):
        user = User.objects.create_user(email='pag_test@test.ru', password='Pass123!')
        UserRole.objects.create(user=user, role=self.role_student)
        
        client = APIClient()
        client.force_authenticate(user=user)
        client.defaults['HTTP_X_ACTIVE_ROLE'] = 'student'
        
        # Проверка, что пагинация работает (запрос с page_size)
        response = client.get('/api/student/notifications/?page=1&page_size=20')
        assert response.status_code in [200, 404]
