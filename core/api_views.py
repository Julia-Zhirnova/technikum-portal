from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Student, Group, Statement
from .serializers import (
    StudentSerializer, GroupWithStudentsSerializer, StatementSerializer
)

# ==============================================================================
# КАСТОМНЫЕ PERMISSIONS
# ==============================================================================

class IsStudent(permissions.BasePermission):
    """Разрешение только для студентов."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'student')

class IsCurator(permissions.BasePermission):
    """Разрешение только для кураторов."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and Group.objects.filter(curator=request.user).exists()

class IsTeacher(permissions.BasePermission):
    """Разрешение только для преподавателей."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and Statement.objects.filter(teacher=request.user).exists()

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

class StudentProfileView(generics.RetrieveAPIView):
    """
    GET /api/student/profile/
    Возвращает профиль текущего студента.
    """
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_object(self):
        # Получаем студента, связанного с текущим пользователем
        return Student.objects.get(user=self.request.user)

class CuratorGroupView(generics.RetrieveAPIView):
    """
    GET /api/curator/group/
    Возвращает группу куратора со списком студентов.
    """
    serializer_class = GroupWithStudentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCurator]
    
    def get_object(self):
        # Получаем группу, где текущий пользователь — куратор
        return Group.objects.get(curator=self.request.user)

class TeacherStatementsView(generics.ListAPIView):
    """
    GET /api/teacher/statements/
    Возвращает список ведомостей преподавателя.
    """
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        # Возвращаем только ведомости текущего преподавателя
        return Statement.objects.filter(teacher=self.request.user)

class WhoAmIView(APIView):
    """
    GET /api/whoami/
    Возвращает роль текущего пользователя (студент/куратор/преподаватель).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        roles = []
        
        # Проверяем, является ли пользователь студентом
        if hasattr(user, 'student'):
            roles.append('student')
        
        # Проверяем, является ли пользователь куратором
        if Group.objects.filter(curator=user).exists():
            roles.append('curator')
        
        # Проверяем, является ли пользователь преподавателем
        if Statement.objects.filter(teacher=user).exists():
            roles.append('teacher')
        
        # Если пользователь — администратор
        if user.is_staff:
            roles.append('admin')
        
        return Response({
            'user_id': user.id_user,
            'email': user.email,
            'full_name': user.get_full_name(),
            'roles': roles
        })
