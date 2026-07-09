#!/usr/bin/env python
"""
Скрипт для установки пароля по умолчанию для всех пользователей.
Устанавливает пароль 'student2026' для пользователей, у которых:
- пароль ещё не задан (пустой или placeholder)
- или пароль требует изменения (requires_password_change=True)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

DEFAULT_PASSWORD = 'student2026'

def set_default_passwords():
    print("=" * 80)
    print("🔐 УСТАНОВКА ПАРОЛЕЙ ПО УМОЛЧАНИЮ")
    print("=" * 80)
    print(f"Пароль по умолчанию: {DEFAULT_PASSWORD}")
    print()
    
    users = User.objects.all()
    updated_count = 0
    skipped_count = 0
    
    for user in users:
        # Пропускаем, если пароль уже задан и не требует изменения
        if user.password and not user.requires_password_change:
            # Проверяем, не является ли это placeholder
            if 'placeholder' not in user.password:
                skipped_count += 1
                continue
        
        # Устанавливаем пароль
        user.set_password(DEFAULT_PASSWORD)
        user.requires_password_change = False  # Сбрасываем флаг требования смены пароля
        user.save()
        updated_count += 1
        
        print(f"✅ {user.email} ({user.get_full_name()})")
    
    print()
    print("=" * 80)
    print(f"📊 ИТОГИ:")
    print(f"   Обновлено: {updated_count}")
    print(f"   Пропущено: {skipped_count}")
    print(f"   Всего: {users.count()}")
    print("=" * 80)
    print()
    print("💡 Теперь все пользователи могут войти с паролем: student2026")
    print("=" * 80)

if __name__ == '__main__':
    set_default_passwords()
