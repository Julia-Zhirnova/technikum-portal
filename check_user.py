#!/usr/bin/env python
"""
Скрипт для проверки и исправления пользователя.
Использование: python check_user.py <email> <password>
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Student, UserRole, Role

if len(sys.argv) < 3:
    print("Использование: python check_user.py <email> <password>")
    print("Пример: python check_user.py shpak_va@luberteh.ru 12345")
    sys.exit(1)

email = sys.argv[1]
password = sys.argv[2]

print(f"🔍 Проверка пользователя: {email}")

try:
    user = User.objects.get(email=email)
    print(f"✅ Найден: {user.get_full_name()}")
    
    # Устанавливаем пароль
    user.set_password(password)
    user.save()
    print(f"✅ Пароль установлен")
    
    # Добавляем роль student
    student_role = Role.objects.get(id_role='student')
    UserRole.objects.get_or_create(user=user, role=student_role)
    print(f"✅ Роль 'student' добавлена")
    
    # Проверяем студента
    try:
        student = Student.objects.get(user=user)
        print(f"✅ Студент: {student.snils}, группа {student.group.id_group}")
    except Student.DoesNotExist:
        print(f"⚠️  Студент не найден")
    
    print(f"\n🎉 Готово! Вход: {email} / {password}")
    
except User.DoesNotExist:
    print(f"❌ Пользователь {email} не найден")
    sys.exit(1)
