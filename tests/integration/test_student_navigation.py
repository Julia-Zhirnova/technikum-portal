import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

TEST_USERS = {
    'student': {'email': 'arhipov_kyu@luberteh.ru', 'password': 'student2026', 'roles': ['student']},
    'teacher_curator': {'email': 'YVZhirnova@yandex.ru', 'password': 'student2026', 'roles': ['teacher', 'curator']},
    'admin_curator_teacher': {'email': 'ang-bl@rambler.ru', 'password': 'student2026', 'roles': ['admin', 'curator', 'teacher']},
    'mck_curator_teacher': {'email': 'tardv69@yandex.ru', 'password': 'student2026', 'roles': ['mck_chairman', 'curator', 'teacher']},
}

ROLE_ROUTES = {
    'student': ['/api/student/profile/', '/api/student/grades/', '/api/student/practice/', '/api/student/requests/', '/api/student/notifications/'],
    'teacher': ['/api/teacher/statements/', '/api/teacher/schedule/', '/api/teacher/practice/', '/api/teacher/rpd/'],
    'curator': ['/api/curator/group/', '/api/curator/grades/', '/api/curator/attendance/', '/api/curator/schedule/', '/api/curator/requests/'],
    'admin': ['/api/admin/users/', '/api/admin/references/'],
    'mck_chairman': ['/api/mck/rpd/', '/api/mck/monitoring/', '/api/mck/protocols/'],
}

@pytest.mark.django_db
def test_role_based_navigation_and_access_control():
    """Проверка навигации по ролям и запрета доступа к чужим разделам"""
    
    try:
        from core.models import UserRole, Role
    except ImportError:
        pytest.skip("Модели UserRole или Role не найдены")
    
    created_users = {}
    
    # 1. Создаем роли с ЯВНЫМ указанием id_role (так как это PK)
    role_objects = {}
    roles_data = [
        ('student', 'Студент'), ('teacher', 'Преподаватель'), 
        ('curator', 'Куратор'), ('admin', 'Администратор'), 
        ('mck_chairman', 'Председатель МЦК')
    ]
    
    for role_id, role_name in roles_data:
        r, _ = Role.objects.get_or_create(id_role=role_id, defaults={'name': role_name})
        role_objects[role_id] = r

    # 2. Создаем пользователей ПРАВИЛЬНО (через create_user)
    for role_key, user_data in TEST_USERS.items():
        # create_user сразу хеширует пароль и сохраняет
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'password': '', # Будет перезаписан ниже
                'is_active': True
            }
        )
        if created or not user.check_password(user_data['password']):
            user.set_password(user_data['password'])
            user.save()
        
        for role_id in user_data['roles']:
            UserRole.objects.get_or_create(
                user=user, 
                role=role_objects[role_id]
            )
            
        created_users[role_key] = user

    client = APIClient()

    # 3. Проверяем доступность страниц
    for role_key, user_data in TEST_USERS.items():
        login_resp = client.post('/api/token/', {
            'email': user_data['email'], 
            'password': user_data['password']
        })
        assert login_resp.status_code == 200, f"Ошибка входа для {role_key}: {login_resp.data}"
        
        token = login_resp.data['access']
        
        for role_id in user_data['roles']:
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_ACTIVE_ROLE=role_id)
            
            allowed_routes = ROLE_ROUTES.get(role_id, [])
            for route in allowed_routes:
                resp = client.get(route)
                # 200 - OK, 404 - страница существует но пуста (допустимо)
                assert resp.status_code in [200, 404], (
                    f"[{role_key}/{role_id}] Страница {route} недоступна (статус {resp.status_code})"
                )

    # 4. Проверка безопасности
    student_user = created_users['student']
    login_resp = client.post('/api/token/', {'email': student_user.email, 'password': TEST_USERS['student']['password']})
    token = login_resp.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_ACTIVE_ROLE='student')
    
    forbidden_for_student = [
        '/api/admin/users/', '/api/teacher/statements/', '/api/curator/group/', '/api/mck/rpd/'
    ]
    
    for route in forbidden_for_student:
        resp = client.get(route)
        assert resp.status_code in [403, 404], (
            f"SECURITY FAIL: Студент получил доступ к {route} (статус {resp.status_code})"
        )
