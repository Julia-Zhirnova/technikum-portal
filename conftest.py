import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Стандартный API клиент DRF для тестов."""
    return APIClient()


@pytest.fixture
def student_user(db):
    """Фикстура для создания тестового студента."""
    user = User.objects.create_user(
        email="student@test.ru",
        password="TestPass123!",
        first_name="Иван",
        last_name="Иванов",
        requires_password_change=False,
        is_active=True
    )
    return user


@pytest.fixture
def admin_user(db):
    """Фикстура для создания тестового администратора."""
    user = User.objects.create_superuser(
        email="admin@test.ru",
        password="AdminPass123!",
        first_name="Админ",
        last_name="Тестов"
    )
    return user


@pytest.fixture
def authenticated_client(api_client, student_user):
    """Клиент с уже выполненным входом."""
    api_client.force_authenticate(user=student_user)
    return api_client
