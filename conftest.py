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
def unique_client_ip(worker_id, request):
    """Генерирует гарантированно уникальный IP для каждого теста.
    
    Формат: 10.{worker_num}.{hash_octet_2}.{hash_octet_3}
    - worker_num явно кодирует xdist-воркер (gw0, gw1, ...) — исключает меж-воркерные коллизии
    - hash из nodeid — исключает внутри-воркерные коллизии
    """
    import hashlib
    # Извлекаем номер воркера (0, 1, 2, ...) — для master будет 'master' → 0
    try:
        worker_num = int(worker_id.replace('gw', ''))
    except (ValueError, AttributeError):
        worker_num = 0
    
    # Хэш test_id для 2-х оставшихся октетов
    test_hash = hashlib.md5(request.node.nodeid.encode()).hexdigest()
    octet_2 = (int(test_hash[:8], 16) % 254) + 1
    octet_3 = (int(test_hash[8:16], 16) % 254) + 1
    
    return f"10.{worker_num}.{octet_2}.{octet_3}"


@pytest.fixture
def mock_client_ip(unique_client_ip, monkeypatch):
    """Мокает get_client_ip для возврата уникального IP."""
    from accounts import audit_views
    
    def mock_get_client_ip(request):
        return unique_client_ip
    
    monkeypatch.setattr(audit_views, 'get_client_ip', mock_get_client_ip)
    return unique_client_ip


@pytest.fixture
def authenticated_client(api_client, student_user):
    """API-клиент, аутентифицированный как student_user.
    
    Используется в тестах, требующих уже аутентифицированного пользователя
    (например, тесты выхода из системы, аудита).
    """
    api_client.force_authenticate(user=student_user)
    return api_client



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
    # ВАЖНО: ВСЕГДА устанавливаем пароль для стабильности при --reuse-db
    user.set_password('student2026')
    user.requires_password_change = False
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
def password_change_user(db, student_group, student_role, enrollment_order):
    """Специальный пользователь для тестов БП 1.2 (смена пароля).
    
    Тестовые данные по спецификации CSV:
    - Email: test_password_change@luberteh.ru
    - Пароль: OldPassword123!
    - requires_password_change: True (принудительно перед каждым тестом)
    
    ВАЖНО: не используем get_or_create, чтобы гарантировать корректное
    состояние даже при --reuse-db.
    """
    # Удаляем старого, если остался от предыдущего прогона
    User.objects.filter(email='test_password_change@luberteh.ru').delete()
    
    user = User.objects.create(
        email='test_password_change@luberteh.ru',
        first_name='Тест',
        last_name='СменаПароля',
        requires_password_change=True,
        is_active=True,
        password_version=1,
    )
    user.set_password('OldPassword123!')
    user.save()
    
    UserRole.objects.create(user=user, role=student_role)
    
    Student.objects.get_or_create(
        snils='999-999-999 99',  # Уникальный тестовый СНИЛС
        defaults={
            'user': user,
            'group': student_group,
            'order': enrollment_order,
            'birth_date': date(2005, 1, 1),
            'gender': 'мужской',
            'birth_place': 'г. Люберцы',
            'phone': '+79990000000',
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



# ============================================
# CELERY: тестовая конфигурация (eager mode)
# ============================================
@pytest.fixture(autouse=True)
def celery_eager_mode(settings):
    """Включает eager mode для Celery в тестах.
    
    Все задачи выполняются синхронно в том же процессе,
    без необходимости запускать отдельный worker.
    """
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


# ============================================
# EMAIL: тестовая конфигурация (locmem backend)
# ============================================
@pytest.fixture(autouse=True)
def use_locmem_email_backend(settings):
    """В тестах email отправляются в django.core.mail.outbox (не реально)."""
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
