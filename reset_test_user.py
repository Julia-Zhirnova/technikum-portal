#!/usr/bin/env python3
"""Сброс тестового пользователя БП 1.2 (E2E меняет реальную БД)."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='test_new_password@luberteh.ru')
user.set_password('OldPassword123!')
user.requires_password_change = True
user.save(update_fields=['password', 'requires_password_change'])
print('reset ok')
