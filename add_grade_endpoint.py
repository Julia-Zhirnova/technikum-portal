#!/usr/bin/env python
"""Скрипт для добавления API endpoint изменения оценки преподавателем"""

import os
import sys

# Правильный путь к settings вашего проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Читаем текущий файл api_views.py
with open('core/api_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Проверяем, есть ли уже UpdateGradeView
if 'class UpdateGradeView' in content:
    print("⚠️ UpdateGradeView уже существует")
else:
    # Добавляем новый класс view
    new_view = '''

class UpdateGradeView(APIView):
    """
    PATCH /api/teacher/grades/<int:grade_id>/ — изменение оценки преподавателем
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, grade_id):
        from .models import StatementGrade, Statement, StatementGradeSerializer
        
        try:
            grade = StatementGrade.objects.get(id_grade=grade_id)
            statement = grade.statement
            
            # Проверяем, что пользователь - преподаватель этой ведомости
            if statement.teacher != request.user:
                return Response(
                    {'error': 'Вы не являетесь преподавателем этой ведомости'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверяем статус ведомости
            if statement.status != 'в_работе':
                return Response(
                    {'error': 'Ведомость закрыта или сдана в архив'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем новую оценку из запроса
            new_grade = request.data.get('оценка')
            if new_grade is None:
                return Response(
                    {'error': 'Поле "оценка" обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Валидация оценки
            valid_grades = ['5', '4', '3', '2', 'н/а', 'зачтено', 'не_зачтено']
            if new_grade not in valid_grades:
                return Response(
                    {'error': f'Недопустимая оценка. Допустимые: {", ".join(valid_grades)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Обновляем оценку
            grade.оценка = new_grade
            grade.save()
            
            return Response({
                'success': True,
                'message': f'Оценка изменена на {new_grade}',
                'grade_id': grade.id_grade
            })
            
        except StatementGrade.DoesNotExist:
            return Response(
                {'error': 'Оценка не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
'''
    
    # Добавляем view в конец файла
    content += new_view
    
    with open('core/api_views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ UpdateGradeView добавлен в api_views.py")

# Теперь добавляем URL
with open('config/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

if 'update-grade' not in urls_content:
    # Добавляем URL перед последним ]
    new_url = "    path('api/teacher/grades/<int:grade_id>/', api_views.UpdateGradeView.as_view(), name='update-grade'),\n"
    
    # Находим последнюю строку с path и добавляем после неё
    lines = urls_content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if 'path(' in lines[i]:
            lines.insert(i + 1, new_url.strip())
            break
    
    urls_content = '\n'.join(lines)
    
    with open('config/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)
    
    print("✅ URL для update-grade добавлен в urls.py")
else:
    print("️ URL для update-grade уже существует")

print("\n✅ Готово! Endpoint добавлен.")
print("URL: PATCH /api/teacher/grades/<int:grade_id>/")
