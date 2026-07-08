#!/usr/bin/env python
"""
Скрипт управления пользователями и ролями.
Использование:
  python manage_users.py list              — показать всех пользователей
  python manage_users.py set_password <email> <password>  — установить пароль
  python manage_users.py add_role <email> <role>  — добавить роль (student/curator/teacher/admin)
  python manage_users.py remove_role <email> <role>  — удалить роль
  python manage_users.py make_all_students  — назначить всем пользователям роль student
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Student, UserRole, Role

def list_users():
    """Показать всех пользователей с их ролями."""
    print("=" * 100)
    print("📋 СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 100)
    
    users = User.objects.all().order_by('id_user')
    for user in users:
        roles = UserRole.objects.filter(user=user).select_related('role')
        role_names = [ur.role.name for ur in roles]
        
        # Проверяем, есть ли связанный Student
        try:
            student = Student.objects.get(user=user)
            student_info = f"🎓 {student.snils} ({student.group.id_group})"
        except Student.DoesNotExist:
            student_info = "❌ Нет записи Student"
        
        print(f"\n👤 ID: {user.id_user}")
        print(f"   Email: {user.email}")
        print(f"   ФИО: {user.get_full_name()}")
        print(f"   Роли: {', '.join(role_names) if role_names else '⚠️  Нет ролей'}")
        print(f"   Студент: {student_info}")
        print(f"   Активен: {'✅' if user.is_active else '❌'}")
    
    print("\n" + "=" * 100)
    print(f"📊 Всего пользователей: {users.count()}")
    print("=" * 100)


def set_password(email, password):
    """Установить пароль для пользователя."""
    try:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        print(f"✅ Пароль установлен для {email}")
        print(f"   Email: {email}")
        print(f"   Пароль: {password}")
    except User.DoesNotExist:
        print(f"❌ Пользователь {email} не найден")


def add_role(email, role_name):
    """Добавить роль пользователю."""
    try:
        user = User.objects.get(email=email)
        role = Role.objects.get(id_role=role_name)
        
        user_role, created = UserRole.objects.get_or_create(user=user, role=role)
        if created:
            print(f"✅ Роль '{role_name}' добавлена пользователю {email}")
        else:
            print(f"⚠️  Роль '{role_name}' уже есть у пользователя {email}")
    except User.DoesNotExist:
        print(f"❌ Пользователь {email} не найден")
    except Role.DoesNotExist:
        print(f"❌ Роль '{role_name}' не найдена")
        print("Доступные роли:")
        for r in Role.objects.all():
            print(f"  - {r.id_role} ({r.name})")


def remove_role(email, role_name):
    """Удалить роль у пользователя."""
    try:
        user = User.objects.get(email=email)
        role = Role.objects.get(id_role=role_name)
        
        deleted_count, _ = UserRole.objects.filter(user=user, role=role).delete()
        if deleted_count > 0:
            print(f"✅ Роль '{role_name}' удалена у пользователя {email}")
        else:
            print(f"⚠️  Роль '{role_name}' не найдена у пользователя {email}")
    except User.DoesNotExist:
        print(f"❌ Пользователь {email} не найден")
    except Role.DoesNotExist:
        print(f"❌ Роль '{role_name}' не найдена")


def make_all_students():
    """Назначить всем пользователям роль student."""
    print("=" * 100)
    print("🎓 НАЗНАЧЕНИЕ РОЛИ STUDENT ВСЕМ ПОЛЬЗОВАТЕЛЯМ")
    print("=" * 100)
    
    try:
        student_role = Role.objects.get(id_role='student')
    except Role.DoesNotExist:
        print("❌ Роль 'student' не найдена")
        return
    
    users = User.objects.all()
    count = 0
    
    for user in users:
        user_role, created = UserRole.objects.get_or_create(user=user, role=student_role)
        if created:
            count += 1
            print(f"✅ {user.email} — роль добавлена")
        else:
            print(f"⚠️  {user.email} — роль уже есть")
    
    print("\n" + "=" * 100)
    print(f"📊 Назначено ролей: {count} из {users.count()}")
    print("=" * 100)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'list':
        list_users()
    elif command == 'set_password' and len(sys.argv) == 4:
        set_password(sys.argv[2], sys.argv[3])
    elif command == 'add_role' and len(sys.argv) == 4:
        add_role(sys.argv[2], sys.argv[3])
    elif command == 'remove_role' and len(sys.argv) == 4:
        remove_role(sys.argv[2], sys.argv[3])
    elif command == 'make_all_students':
        make_all_students()
    else:
        print(__doc__)
        sys.exit(1)
