import io
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from openpyxl import Workbook

from core.models import UserRole
from .services import reset_user_password, generate_temporary_password

User = get_user_model()


def _get_curator_group(user):
    """Возвращает группу, которую курирует пользователь, или None."""
    try:
        # Ищем группу, где этот пользователь — куратор
        from core.models import Group
        # Предполагаем, что в модели Group есть поле curator (ForeignKey к User)
        group = Group.objects.filter(curator=user).first()
        return group
    except Exception:
        return None


def _get_students_of_group(group):
    """Возвращает queryset студентов указанной группы."""
    if not group:
        return User.objects.none()
    return User.objects.filter(studentprofile__group=group, is_active=True)


class CuratorGroupStudentsView(APIView):
    """Список студентов группы куратора с их логинами."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Проверяем, что пользователь — куратор
        is_curator = UserRole.objects.filter(
            user=request.user, 
            role__id_role='curator'
        ).exists()
        
        if not is_curator:
            return Response(
                {"detail": "Доступ только для кураторов."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        group = _get_curator_group(request.user)
        if not group:
            return Response(
                {"detail": "За вами не закреплена ни одна группа."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        students = _get_students_of_group(group)
        
        data = []
        for student in students:
            full_name = f"{student.last_name} {student.first_name} {student.middle_name}".strip()
            data.append({
                "id": student.id,
                "full_name": full_name,
                "email": student.email,
                "requires_password_change": student.requires_password_change
            })
        
        return Response({
            "group": {
                "id": group.id,
                "name": group.name
            },
            "students": data
        }, status=status.HTTP_200_OK)


class CuratorResetStudentPasswordView(APIView):
    """Сброс пароля студента своей группы (только для куратора)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        # Проверяем, что пользователь — куратор
        is_curator = UserRole.objects.filter(
            user=request.user, 
            role__id_role='curator'
        ).exists()
        
        if not is_curator:
            return Response(
                {"detail": "Доступ только для кураторов."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        group = _get_curator_group(request.user)
        if not group:
            return Response(
                {"detail": "За вами не закреплена ни одна группа."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Проверяем, что студент принадлежит группе куратора
        try:
            student = User.objects.get(
                id=student_id, 
                studentprofile__group=group,
                is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Студент не найден или не принадлежит вашей группе."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        new_password = reset_user_password(student)
        
        return Response({
            "detail": "Пароль студента сброшен.",
            "email": student.email,
            "temporary_password": new_password
        }, status=status.HTTP_200_OK)


class CuratorExportGroupPasswordsView(APIView):
    """Экспорт Excel с логинами и паролями студентов своей группы."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Проверяем, что пользователь — куратор
        is_curator = UserRole.objects.filter(
            user=request.user, 
            role__id_role='curator'
        ).exists()
        
        if not is_curator:
            return HttpResponse("Доступ только для кураторов.", status=403)
        
        group = _get_curator_group(request.user)
        if not group:
            return HttpResponse("За вами не закреплена ни одна группа.", status=404)
        
        students = _get_students_of_group(group)
        
        # Создаём Excel
        wb = Workbook()
        ws = wb.active
        ws.title = group.name
        ws.append(["ФИО", "Email", "Логин", "Временный пароль", "Группа"])
        
        for student in students:
            full_name = f"{student.last_name} {student.first_name} {student.middle_name}".strip()
            new_password = reset_user_password(student, save=True)
            ws.append([
                full_name,
                student.email,
                student.email,
                new_password,
                group.name
            ])
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        safe_name = "".join(c for c in group.name if c.isalnum() or c in (' ', '-', '_')).strip()
        response['Content-Disposition'] = f'attachment; filename="{safe_name}.xlsx"'
        return response
