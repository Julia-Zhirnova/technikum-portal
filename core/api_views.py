from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Student, Group, Statement
from .serializers import (
    StudentProfileSerializer, GroupWithStudentsSerializer, StatementSerializer
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
# API ENDPOINTS ДЛЯ СТУДЕНТА
# ==============================================================================

class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/student/profile/ — получить профиль студента
    PUT/PATCH /api/student/profile/ — обновить профиль студента
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_object(self):
        return Student.objects.get(user=self.request.user)

# ==============================================================================
# API ENDPOINTS ДЛЯ КУРАТОРА
# ==============================================================================

class CuratorGroupView(generics.RetrieveAPIView):
    """
    GET /api/curator/group/ — группа куратора со списком студентов
    """
    serializer_class = GroupWithStudentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCurator]
    
    def get_object(self):
        return Group.objects.get(curator=self.request.user)

class CuratorStudentDetailView(generics.RetrieveAPIView):
    """
    GET /api/curator/students/<snils>/ — анкета конкретного студента
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsCurator]
    lookup_field = 'snils'
    
    def get_queryset(self):
        # Куратор видит только студентов своей группы
        curator_group = Group.objects.filter(curator=self.request.user).first()
        if curator_group:
            return Student.objects.filter(group=curator_group)
        return Student.objects.none()

# ==============================================================================
# API ENDPOINTS ДЛЯ ПРЕПОДАВАТЕЛЯ
# ==============================================================================

class TeacherStatementsView(generics.ListAPIView):
    """
    GET /api/teacher/statements/ — список ведомостей преподавателя
    """
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    
    def get_queryset(self):
        return Statement.objects.filter(teacher=self.request.user)

# ==============================================================================
# УНИВЕРСАЛЬНЫЕ ENDPOINTS
# ==============================================================================

class WhoAmIView(APIView):
    """
    GET /api/whoami/ — роль текущего пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        roles = []
        
        if hasattr(user, 'student'):
            roles.append('student')
        
        if Group.objects.filter(curator=user).exists():
            roles.append('curator')
        
        if Statement.objects.filter(teacher=user).exists():
            roles.append('teacher')
        
        if user.is_staff:
            roles.append('admin')
        
        return Response({
            'user_id': user.id_user,
            'email': user.email,
            'full_name': user.get_full_name(),
            'roles': roles,
        })
