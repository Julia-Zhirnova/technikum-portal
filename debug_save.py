#!/usr/bin/env python
"""Скрипт для диагностики ошибок сохранения"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Student, User
from core.serializers import StudentProfileUpdateSerializer

# Получаем тестового студента
try:
    student = Student.objects.get(snils='987-654-321 02')
    print(f"✅ Найден студент: {student.user.get_full_name()}")
    
    # Тестируем сериализатор с примерными данными
    test_data = {
        'phone': '+79161234567',
        'inn': '502712345678',
        'passport': {
            'series_number': '4619 123456',
            'issue_date': '2023-03-15',
            'issuer': 'ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ',
        },
        'health': {
            'status': 'здоров',
            'oms_number': '5999000999000999',
        }
    }
    
    print("\n📝 Тестируем сериализатор с данными:")
    print(test_data)
    
    serializer = StudentProfileUpdateSerializer(student, data=test_data, partial=True)
    
    if serializer.is_valid():
        print("\n✅ Данные валидны!")
        serializer.save()
        print("✅ Данные сохранены!")
    else:
        print("\n❌ Ошибки валидации:")
        print(serializer.errors)
        
except Student.DoesNotExist:
    print("❌ Студент не найден")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
