#!/usr/bin/env python
"""
Скрипт для назначения кураторов группам и исправления ролей.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, UserRole, Role, Group

print("=" * 80)
print("🔧 НАЗНАЧЕНИЕ КУРАТОРОВ ГРУППАМ И ИСПРАВЛЕНИЕ РОЛЕЙ")
print("=" * 80)

# 1. Удаляем роль admin у Жирновой и Тарджиманян
print("\n🗑️  УДАЛЕНИЕ ЛИШНИХ РОЛЕЙ ADMIN:")
for email in ['YVZhirnova@yandex.ru', 'tardv69@yandex.ru']:
    try:
        user = User.objects.get(email=email)
        deleted, _ = UserRole.objects.filter(user=user, role__id_role='admin').delete()
        if deleted:
            print(f"  ✅ У {user.get_full_name()} удалена роль admin")
        else:
            print(f"  ⚠️  У {user.get_full_name()} роли admin не было")
    except User.DoesNotExist:
        print(f"  ❌ Пользователь {email} не найден")

# 2. Удаляем роль curator у Архипова
print("\n🗑️  УДАЛЕНИЕ РОЛИ CURATOR У АРХИПОВА:")
try:
    arhipov = User.objects.get(email='arhipov_kyu@luberteh.ru')
    deleted, _ = UserRole.objects.filter(user=arhipov, role__id_role='curator').delete()
    if deleted:
        print(f"  ✅ У {arhipov.get_full_name()} удалена роль curator")
    else:
        print(f"  ⚠️  У {arhipov.get_full_name()} роли curator не было")
except User.DoesNotExist:
    print(f"  ❌ Архипов не найден")

# 3. Маппинг кураторов: (фамилия для поиска, email если известен, [(группа, корпус), ...])
curators_data = [
    # Угреша
    ('Капранова', 'ang-bl@rambler.ru', [('ИС1-25', 'Угреша')]),
    ('Жирнова', 'YVZhirnova@yandex.ru', [('ИС-24', 'Угреша')]),
    ('Тарджиманян', 'tardv69@yandex.ru', [('ОИБ-24', 'Угреша')]),
    ('Лозбинева', None, [('TM-25', 'Угреша')]),
    ('Дидаева', None, [('ИС2-25', 'Угреша')]),
    ('Ромашова', None, [('ТАКХС-25', 'Угреша')]),
    ('Меринова', None, [('ОДЛу-25', 'Угреша')]),
    ('Кушакова', None, [('ЖКХ-25', 'Угреша'), ('ПКп-24', 'Угреша')]),
    ('Кондакова', None, [('ЛК-25', 'Угреша')]),
    ('Каменев', None, [('СПм-25', 'Угреша')]),
    ('Чурилина', None, [('ГД-25', 'Угреша')]),
    ('Кагарманов', None, [('MCP-25', 'Угреша'), ('ЖКХп-24', 'Угреша')]),
    ('Гребенюк', None, [('ТМ-24', 'Угреша'), ('ПСОп-23', 'Угреша')]),
    ('Ахмылина', None, [('ЛК-24', 'Угреша')]),
    ('Борисов', None, [('МСР-24', 'Угреша')]),
    ('Назаренко', None, [('ТАКХС-24', 'Угреша'), ('КП -23', 'Угреша')]),
    ('Бахаева', None, [('ОДЛУ-24', 'Угреша')]),
    ('Жиркина', None, [('ГДп-24', 'Угреша')]),
    ('Кузьмина', None, [('ГД-24', 'Угреша')]),
    ('Истратова', None, [('РЗХ-24', 'Угреша')]),
    ('Гришакова', None, [('ИСП-23', 'Угреша')]),
    ('Есикова', None, [('ИСВ-23', 'Угреша')]),
    ('Шалагина', None, [('ГД-23', 'Угреша'), ('ГДп-23', 'Угреша')]),
    ('Гагарин', None, [('СП-23', 'Угреша')]),
    ('Вахаб', None, [('ПК-23', 'Угреша'), ('ГДп-22', 'Угреша')]),
    ('Рязанова', None, [('ОДЛу-23', 'Угреша')]),
    ('Шубина', None, [('ПКп-23', 'Угреша'), ('ПД-22', 'Угреша')]),
    ('Чадаева', None, [('ГД-22', 'Угреша')]),
    # Центральный
    ('Старченко', None, [('ПОАТ1-25', 'Центральный'), ('ПОАТ-24', 'Центральный')]),
    ('Гапоненко', None, [('ТО-25', 'Центральный')]),
    ('Акиньшина', None, [('ЭБАС1-25', 'Центральный'), ('Ю1п-24', 'Центральный')]),
    ('Кашеварова', None, [('Юп-25', 'Центральный')]),
    ('Чиркунова', None, [('НКп-25', 'Центральный')]),
    ('Акулина', None, [('ПОАТ2-25', 'Центральный')]),
    ('Щекочихина', None, [('ТО-24', 'Центральный')]),
    ('Лукина', None, [('Ю2п-24', 'Центральный')]),
    ('Соловьёва', None, [('ДОУп-24', 'Центральный')]),
    ('Потапова', None, [('ПОАТ -23', 'Центральный')]),
    ('Носова', None, [('ПБ-23', 'Центральный'), ('ПБ -22', 'Центральный')]),
    ('Алексеева', None, [('ДОУ -23', 'Центральный')]),
    ('Двухименная', None, [('ТОп-23', 'Центральный')]),
    ('Петухова', None, [('ПОАТ -22', 'Центральный')]),
    ('Ефимище', None, [('ТО -22', 'Центральный')]),
    # Гагаринский
    ('Миронова', None, [('ОС-25', 'Гагаринский'), ('ЭК-23', 'Гагаринский')]),
    ('Бундина', None, [('ЭК-25', 'Гагаринский')]),
    ('Хохлова', None, [('ЗУ-25', 'Гагаринский')]),
    ('Перепечко', None, [('ЭМД-25', 'Гагаринский')]),
    ('Меликян', None, [('ПДп-25', 'Гагаринский'), ('ОС-24', 'Гагаринский')]),
    ('Неретина', None, [('ПДп-24', 'Гагаринский')]),
    ('Куртукова', None, [('ЭКп-24', 'Гагаринский')]),
    ('Евсюкова', None, [('ПД-23', 'Гагаринский')]),
    ('Лавриненко', None, [('ПК-22', 'Гагаринский'), ('ПКп-22', 'Гагаринский')]),
    # Красково
    ('Терешина', None, [('СА-25', 'Красково')]),
    ('Иванова', None, [('АП-25', 'Красково'), ('ОДЛк-25', 'Красково')]),
    ('Татаринцева', None, [('МОП1-25', 'Красково'), ('МР-25', 'Красково')]),
    ('Стасюк', None, [('МОП2-25', 'Красково')]),
    ('Барсукова', None, [('СА-24', 'Красково'), ('АП-24', 'Красково')]),
    ('Бусыгина', None, [('ЭБАС-24', 'Красково'), ('ЭБАС-22', 'Красково')]),
    ('Шамхалян', None, [('МОП-24', 'Красково'), ('ОДЛк-23', 'Красково')]),
    ('Зеляева', None, [('СА-23', 'Красково')]),
    ('Тюкова', None, [('ТИК-23', 'Красково'), ('МРп-24', 'Красково')]),
    ('Щербакова', None, [('ЭБАС-23', 'Красково')]),
    ('Сальковская', None, [('СА-22', 'Красково'), ('ТПИ -22', 'Красково')]),
]

# 4. Назначаем кураторов
print("\n👨‍🏫 НАЗНАЧЕНИЕ КУРАТОРОВ:")
assigned_count = 0
not_found_count = 0

for surname, known_email, groups in curators_data:
    # Находим пользователя
    user = None
    if known_email:
        try:
            user = User.objects.get(email=known_email)
        except User.DoesNotExist:
            pass
    
    if not user:
        # Ищем по фамилии
        users = User.objects.filter(last_name__icontains=surname)
        if users.count() == 1:
            user = users.first()
        elif users.count() > 1:
            # Берём первого активного
            user = users.filter(is_active=True).first()
    
    if not user:
        print(f"  ❌ {surname}: пользователь не найден")
        not_found_count += 1
        continue
    
    # Добавляем роли teacher и curator
    teacher_role, _ = Role.objects.get_or_create(id_role='teacher', defaults={'name': 'Преподаватель'})
    curator_role, _ = Role.objects.get_or_create(id_role='curator', defaults={'name': 'Куратор'})
    
    UserRole.objects.get_or_create(user=user, role=teacher_role)
    UserRole.objects.get_or_create(user=user, role=curator_role)
    
    # Назначаем куратора для групп
    for group_id, campus in groups:
        try:
            group = Group.objects.get(id_group=group_id)
            group.curator = user
            group.save()
            print(f"  ✅ {group_id} → {user.get_full_name()} ({user.email})")
            assigned_count += 1
        except Group.DoesNotExist:
            print(f"  ⚠️  Группа {group_id} не найдена в БД")

print("\n" + "=" * 80)
print(f"📊 ИТОГИ:")
print(f"   Назначено кураторов: {assigned_count}")
print(f"   Не найдено пользователей: {not_found_count}")
print("=" * 80)
