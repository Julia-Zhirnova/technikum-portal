"""Глобальные фикстуры pytest для БП 1.1 / 1.2."""
import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Group, Student, Role, UserRole, Campus, Specialty, Qualification, Order

User = get_user_model()


@pytest.fixture
def api_client():
    """Стандартный DRF API-клиент."""
    return APIClient()


@pytest.fixture
def student_role(db):
    """Фикстура роли 'student'."""
    role, _ = Role.objects.get_or_create(id_role='student', name='Студент')
    return role


@pytest.fixture
def campus(db):
    """Фикстура корпуса."""
    campus, _ = Campus.objects.get_or_create(
        id_campus='main',
        defaults={'address': 'г. Люберцы, ул. Кирова, д. 1'},
    )
    return campus


@pytest.fixture
def specialty(db):
    """Фикстура специальности."""
    specialty, _ = Specialty.objects.get_or_create(
        id_specialty='09.02.07',
        defaults={'name': 'Информационные системы'},
    )
    return specialty


@pytest.fixture
def qualification(db, specialty):
    """Фикстура квалификации."""
    qual, _ = Qualification.objects.get_or_create(
        specialty=specialty,
        name='Техник-программист',
    )
    return qual


@pytest.fixture
def enrollment_order(db):
    """Фикстура приказа о зачислении."""
    order, _ = Order.objects.get_or_create(
        id_order='100-2025',
        defaults={
            'number': '100',
            'date': date(2025, 9, 1),
            'name': 'О зачислении студентов 1 курса',
            'type': 'зачисление',
        },
    )
    return order


@pytest.fixture
def student_group(db, qualification, campus):
    """Фикстура группы ИС1-25."""
    group, _ = Group.objects.get_or_create(
        id_group='ИС1-25',
        defaults={
            'qualification': qualification,
            'year_start': 2025,
            'year_end': 2027,
            'duration': '2 года 10 месяцев',
            'form': 'очная',
            'financing': 'бюджет',
            'campus': campus,
        },
    )
    return group


@pytest.fixture
def student_user(db, student_group, student_role, enrollment_order):
    """Тестовый студент arhipov_kyu@luberteh.ru."""
    user, created = User.objects.get_or_create(
        email='arhipov_kyu@luberteh.ru',
        defaults={
            'first_name': 'Кирилл',
            'last_name': 'Архипов',
            'requires_password_change': False,
            'is_active': True,
        },
    )
    if created:
        user.set_password('student2026')
        user.save()
    
    UserRole.objects.get_or_create(user=user, role=student_role)
    
    Student.objects.get_or_create(
        snils='182-530-946 72',
        defaults={
            'user': user,
            'group': student_group,
            'order': enrollment_order,
            'birth_date': date(2005, 1, 1),
            'gender': 'мужской',
            'birth_place': 'г. Люберцы',
            'phone': '+79000000000',
        },
    )
    return user


@pytest.fixture
def blocked_user(db, student_role):
    """Заблокированный пользователь (is_active=False)."""
    user, created = User.objects.get_or_create(
        email='blocked_user@luberteh.ru',
        defaults={
            'is_active': False,
        },
    )
    if created:
        user.set_password('Password123!')
        user.save()
    
    UserRole.objects.get_or_create(user=user, role=student_role)
    return user


@pytest.fixture
def curator_user(db):
    """Куратор YVZhirnova@yandex.ru."""
    role, _ = Role.objects.get_or_create(id_role='curator', name='Куратор')
    user, created = User.objects.get_or_create(
        email='YVZhirnova@yandex.ru',
        defaults={
            'first_name': 'Юлия',
            'last_name': 'Жирнова',
            'requires_password_change': False,
            'is_active': True,
        },
    )
    if created:
        user.set_password('student2026')
        user.save()
    
    UserRole.objects.get_or_create(user=user, role=role)
    return user


@pytest.fixture(autouse=True)
def clear_brute_force_cache():
    """Очищает brute-force кэш до и после каждого теста."""
    from django.conf import settings
    from django.core.cache import caches
    try:
        cache = caches[settings.BRUTE_FORCE_PROTECTION["CACHE_ALIAS"]]
        cache.clear()
    except Exception:
        pass
    yield
    try:
        cache = caches[settings.BRUTE_FORCE_PROTECTION["CACHE_ALIAS"]]
        cache.clear()
    except Exception:
        pass
