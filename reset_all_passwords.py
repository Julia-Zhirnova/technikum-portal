#!/usr/bin/env python
"""
Скрипт для установки пароля 'student2026' для ВСЕХ пользователей.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User

DEFAULT_PASSWORD = 'student2026'

def reset_all_passwords():
    print("=" * 80)
    print("🔐 СБРОС ПАРОЛЕЙ ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)
    print(f"Новый пароль: {DEFAULT_PASSWORD}")
    print()
    
    users = User.objects.all()
    updated_count = 0
    
    for user in users:
        user.set_password(DEFAULT_PASSWORD)
        user.requires_password_change = False
        user.save()
        updated_count += 1
        
        if updated_count % 100 == 0:
            print(f"✅ Обновлено: {updated_count} из {users.count()}")
    
    print()
    print("=" * 80)
    print(f"📊 ИТОГИ:")
    print(f"   Обновлено: {updated_count}")
    print(f"   Всего: {users.count()}")
    print("=" * 80)
    print()
    print(f"💡 Теперь ВСЕ пользователи могут войти с паролем: {DEFAULT_PASSWORD}")
    print("=" * 80)

if __name__ == '__main__':
    reset_all_passwords()
