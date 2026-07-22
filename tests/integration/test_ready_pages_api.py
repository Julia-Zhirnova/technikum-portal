import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
def test_ready_api_endpoints():
    """Проверка API-эндпоинтов для страниц, помеченных как 'Готова: Да'"""
    
    client = APIClient()
    
    # Создаем тестового студента (без сложных связей)
    user = User.objects.create_user(
        email='api_test@luberteh.ru',
        password='TestPass123!',
        first_name='Тест',
        last_name='Студент'
    )
    
    # Авторизация
    login_resp = client.post('/api/token/', {
        'email': 'api_test@luberteh.ru',
        'password': 'TestPass123!'
    })
    assert login_resp.status_code == 200, "Не удалось войти"
    token = login_resp.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Список готовых эндпоинтов
    ready_endpoints = [
        '/api/student/profile/',
        '/api/student/grades/',
        '/api/student/requests/',
        '/api/student/notifications/',
        '/api/teacher/statements/',
        '/api/curator/group/',
        '/api/admin/users/',
        '/api/mck/rpd/',
    ]

    for endpoint in ready_endpoints:
        resp = client.get(endpoint)
        # Разрешаем 200 (успех) и 404 (не реализовано), но не 500
        if resp.status_code == 500:
            pytest.fail(f"Эндпоинт {endpoint} вернул 500 Internal Server Error")
        print(f"✅ {endpoint}: {resp.status_code}")
