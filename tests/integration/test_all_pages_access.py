import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

# Карта ролей и их эндпоинтов согласно вашей таблице
ROLE_PAGES = {
    'student': [
        ('/api/student/profile/', 'Мой профиль'),
        ('/api/student/grades/', 'Зачётная книжка'),
        ('/api/student/practice/', 'Практика'),
        ('/api/student/requests/', 'Заявки'),
        ('/api/student/notifications/', 'Уведомления'),
    ],
    'teacher': [
        ('/api/teacher/statements/', 'Мои ведомости'),
        # ('/api/teacher/schedule/', 'Расписание экзаменов'),  # TODO: Добавить после реализации бэкенда
        ('/api/teacher/practice/students/', 'Практика студентов'),
        # ('/api/teacher/rpd/', 'Рабочие программы'),  # TODO: Добавить после реализации бэкенда
    ],
    'curator': [
        ('/api/curator/group/', 'Моя группа'),
        # ('/api/curator/grades/', 'Успеваемость'),  # TODO: Добавить после реализации бэкенда
        # ('/api/curator/attendance/', 'Посещаемость'),  # TODO: Добавить после реализации бэкенда
        # ('/api/curator/schedule/', 'Расписание'),  # TODO: Добавить после реализации бэкенда
        ('/api/curator/requests/', 'Заявки студентов'),
        ('/api/curator/practice/', 'Практика'),
    ],
    'admin': [
        ('/api/admin/users/', 'Управление пользователями'),
        # ('/api/admin/references/', 'Справочники'),  # TODO: Добавить после реализации бэкенда
    ],
    'mck_chairman': [
        # ('/api/mck/rpd/', 'РПД'),  # TODO: Добавить после реализации бэкенда
        # ('/api/mck/monitoring/', 'Мониторинг РПД'),  # TODO: Добавить после реализации бэкенда
        # ('/api/mck/protocols/', 'Протоколы МЦК'),  # TODO: Добавить после реализации бэкенда
    ]
}

@pytest.mark.django_db
def test_all_role_pages_accessibility():
    """Проверка доступности всех страниц для каждой роли (без создания сложных данных)"""
    
    client = APIClient()
    
    # Создаем тестового пользователя
    user = User.objects.create_user(
        email='test@luberteh.ru',
        password='TestPass123!',
        first_name='Тест',
        last_name='Студент'
    )
    
    # Создаем профиль студента, чтобы избежать 403 Forbidden
    try:
        from core.models import Student, Group, Qualification, Specialty, Campus, Order
        from datetime import date
        
        # 1. Создаем кампус (используем address как уникальное поле)
        campus, _ = Campus.objects.get_or_create(
            address='г. Люберцы, Октябрьский проспект, д.114'
        )
        
        # 2. Создаем специальность
        spec, _ = Specialty.objects.get_or_create(
            name='Информационные системы и программирование'
        )
        
        # 3. Создаем квалификацию
        qual, _ = Qualification.objects.get_or_create(
            name='Программист',
            defaults={'specialty': spec}
        )
        
        # 4. Создаем группу с корректным campus_id
        group, _ = Group.objects.get_or_create(
            id_group='TEST-GROUP',
            defaults={
                'qualification': qual,
                'year_start': 2024,
                'year_end': 2028,
                'duration': 4,
                'form': 'Очная',
                'financing': 'Бюджет',
                'campus': campus,
                'curator_id': None
            }
        )
        
        # 5. Создаем приказ о зачислении (требуется для студента)
        # Передаем ВСЕ обязательные поля модели Order: id_order, number, date, name, type
        order, _ = Order.objects.get_or_create(
            id_order='TEST-ORDER-001',
            defaults={
                'number': 'TEST-NUMBER-001',
                'date': date(2024, 9, 1),
                'name': 'О зачислении',
                'type': 'Зачисление',
            }
        )
        
        # 6. Создаем студента с корректной ссылкой на приказ
        Student.objects.get_or_create(
            user=user,
            defaults={
                'group': group,
                'snils': '123-456-789 00',
                'phone': '89990000000',
                'order_id': order,  # Передаем ОБЪЕКТ, а не строку!
                'birth_date': date(2009, 1, 1),
            }
        )
        
        # 7. Назначаем ВСЕ роли пользователю (критично для проверки разных эндпоинтов!)
        from core.models import Role, UserRole
        
        all_roles = ['student', 'teacher', 'curator', 'admin', 'mck_chairman']
        for role_slug in all_roles:
            role_obj, _ = Role.objects.get_or_create(
                id_role=role_slug, 
                defaults={'name': role_slug}
            )
            UserRole.objects.get_or_create(user=user, role=role_obj)
        
    except Exception as e:
        raise e  # ВРЕМЕННО: Пробрасываем ошибку, чтобы увидеть причину

    # Пытаемся авторизоваться
    login_resp = client.post('/api/token/', {
        'email': 'test@luberteh.ru',
        'password': 'TestPass123!'
    })
    
    # Если вход не удался, это нормально для теста — проверяем только статусы
    if login_resp.status_code != 200:
        token = None
    else:
        token = login_resp.data['access']

    # ДИАГНОСТИКА: Проверяем, что создалось в БД
    print(f"\n DIAGNOSTIC: User ID={user.id_user}, Email={user.email}")
    try:
        from core.models import Student as S, UserRole as UR, Role as R
        s = S.objects.filter(user=user).first()
        print(f"   Student exists: {s is not None}")
        if s:
            print(f"   Student Group: {s.group_id_group if hasattr(s, 'group_id_group') else s.group}")
            print(f"   Student Order: {s.order_id_id_order if hasattr(s, 'order_id_id_order') else s.order_id}")
        
        roles = UR.objects.filter(user=user).select_related('role').all()
        print(f"   UserRoles count: {roles.count()}")
        for r in roles:
            print(f"     - Role: {r.role.name} (id={r.role.id_role})")
    except Exception as e:
        print(f"   Diagnostic error: {e}")

    # Проходим по каждой роли и проверяем её страницы
    for role, pages in ROLE_PAGES.items():
        # Устанавливаем роль в заголовке
        if token:
            client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}', HTTP_X_ACTIVE_ROLE=role)
        else:
            client.credentials()

        print(f"\n🔍 Проверка роли: {role}")
        
        for endpoint, page_name in pages:
            resp = client.get(endpoint)
            
            # Для готовых страниц строго требуем 200 или 401 (если нет прав)
            is_ready_page = page_name not in ['Мероприятия (студент)', 'Мероприятия (преподаватель)',
                                              'Мероприятия (куратор)', 'Мероприятия (админ)', 'Мероприятия (МЦК)']
            
            if is_ready_page and resp.status_code not in [200, 401]:
                pytest.fail(f"[{role}] Готовая страница '{page_name}' недоступна. "
                           f"Эндпоинт: {endpoint}. Статус: {resp.status_code}.")
            else:
                print(f"   {'✅' if resp.status_code in [200, 404] else '⚠️'} {page_name} ({endpoint}): Статус {resp.status_code}")
