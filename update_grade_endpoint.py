# Скрипт для добавления API endpoint изменения оценки преподавателем

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, '/home/redoslek/projects/technikum-portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technikum_portal.settings')

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
    PATCH/POST /api/teacher/grade/<grade_id>/update/ — изменение оценки преподавателем
    
    Преподаватель может изменить оценку студента. После изменения:
    - Оценка обновляется в базе данных
    - Автоматически пересчитывается статистика в зачётке студента
    - Создаётся запись в журнале изменений
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, grade_id):
        return self.update_grade(request, grade_id)
    
    def post(self, request, grade_id):
        return self.update_grade(request, grade_id)
    
    def update_grade(self, request, grade_id):
        from core.models import StatementGrade, GradeChangeLog
        from core.serializers import StatementGradeSerializer
        
        try:
            # Получаем оценку
            grade = StatementGrade.objects.select_related(
                'statement', 
                'student',
                'statement__teacher'
            ).get(id=grade_id)
            
            # Проверяем права доступа
            if grade.statement.teacher != request.user:
                return Response(
                    {'error': 'Только преподаватель, ведущий дисциплину, может изменять оценку'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Получаем новую оценку
            new_grade_value = request.data.get('grade')
            if not new_grade_value:
                return Response(
                    {'error': 'Необходимо указать новую оценку в поле "grade"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Допустимые значения оценок
            valid_grades = ['5', '4', '3', '2', 'Зачтено', 'Не зачтено']
            if new_grade_value not in valid_grades:
                return Response(
                    {'error': f'Недопустимая оценка. Допустимые: {", ".join(valid_grades)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Сохраняем старую оценку
            old_grade_value = grade.grade
            
            # Обновляем оценку
            grade.grade = new_grade_value
            grade.is_retake = request.data.get('is_retake', False)
            grade.save()
            
            # Создаём запись в журнале изменений
            GradeChangeLog.objects.create(
                grade=grade,
                teacher=request.user,
                old_grade=old_grade_value,
                new_grade=new_grade_value,
                comment=request.data.get('comment', '')
            )
            
            # Сериализуем обновлённую оценку
            serializer = StatementGradeSerializer(grade)
            
            return Response({
                'success': True,
                'message': f'Оценка изменена с "{old_grade_value}" на "{new_grade_value}"',
                'grade': serializer.data
            })
            
        except StatementGrade.DoesNotExist:
            return Response(
                {'error': 'Оценка не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Ошибка сервера: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

'''
    
    # Добавляем в конец файла
    content = content.rstrip() + new_view
    
    with open('core/api_views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ UpdateGradeView добавлен в core/api_views.py")

# Теперь добавляем URL
with open('core/urls.py', 'r', encoding='utf-8') as f:
    urls_content = f.read()

# Проверяем, есть ли уже этот URL
if 'grade/<int:grade_id>/update' not in urls_content:
    # Импортируем UpdateGradeView
    if 'from .api_views import' in urls_content:
        # Добавляем в существующий импорт
        urls_content = urls_content.replace(
            'from .api_views import',
            'from .api_views import UpdateGradeView,'
        )
    else:
        # Добавляем новый импорт
        urls_content = 'from .api_views import UpdateGradeView\n' + urls_content
    
    # Добавляем URL pattern
    if 'urlpatterns = [' in urls_content:
        urls_content = urls_content.replace(
            'urlpatterns = [',
            '''urlpatterns = [
    path('teacher/grade/<int:grade_id>/update/', UpdateGradeView.as_view(), name='teacher-update-grade'),
'''
        )
    
    with open('core/urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content)
    
    print("✅ URL добавлен в core/urls.py")
else:
    print("⚠️ URL уже существует")

print("\n📋 Пример использования:")
print('''
# Изменение оценки
curl -X PATCH http://localhost:8000/api/teacher/grade/123/update/ \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{"grade": "5", "is_retake": false, "comment": "Исправлено по заявлению студента"}'

# Ответ:
{
  "success": true,
  "message": "Оценка изменена с \\"2\\" на \\"5\\"",
  "grade": {
    "id": 123,
    "grade": "5",
    "student": {...},
    "statement": {...},
    ...
  }
}

После изменения оценки:
✅ Оценка обновляется в базе
✅ Статистика в StudentGradesView пересчитывается автоматически
✅ Создаётся запись в журнале изменений
✅ Студент видит обновлённую оценку в зачётке
''')

