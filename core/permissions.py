"""Кастомные permissions для ролевого доступа (Блок 1.3).

Паттерн проверки ролей через UserRole (таблица core_userrole).
Идентичен паттерну из core/api_views.py (IsCurator, IsTeacher).
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        from core.models import UserRole
        return UserRole.objects.filter(user=request.user, role__id_role='admin').exists()


class IsCurator(permissions.BasePermission):
    """Разрешение для кураторов и администраторов."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        from core.models import UserRole
        return UserRole.objects.filter(user=request.user, role__id_role='curator').exists()


class IsTeacher(permissions.BasePermission):
    """Разрешение для преподавателей."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        from core.models import UserRole
        return UserRole.objects.filter(user=request.user, role__id_role='teacher').exists()
