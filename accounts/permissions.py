from rest_framework import permissions
from core.models import UserRole


class HasActiveRolePermission(permissions.BasePermission):
    """
    Проверяет, что пользователь аутентифицирован,
    и указанная в заголовке X-Active-Role роль действительно принадлежит этому пользователю.
    """
    message = "У вас нет доступа к этому разделу с выбранной ролью."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Получаем роль из заголовка (DRF преобразует X-Active-Role в HTTP_X_ACTIVE_ROLE)
        active_role = request.META.get('HTTP_X_ACTIVE_ROLE')
        
        if not active_role:
            # Если заголовок не передан — разрешаем (для совместимости)
            return True
        
        # Получаем все роли пользователя из БД
        user_roles = list(UserRole.objects.filter(user=request.user).values_list('role__id_role', flat=True))
        
        # Разрешаем доступ, только если запрошенная роль есть у пользователя
        return active_role in user_roles


class RequireRole(permissions.BasePermission):
    """
    Проверяет, что активная роль пользователя совпадает с требуемой для View.
    Использование: permission_classes = [RequireRole]
    required_role = 'admin'  # или 'curator', 'teacher', 'student'
    """
    message = "У вас нет доступа к этому разделу."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        active_role = request.META.get('HTTP_X_ACTIVE_ROLE')
        required_role = getattr(view, 'required_role', None)
        
        if not required_role:
            return True
        
        if not active_role:
            return False
        
        # Проверяем, что активная роль совпадает с требуемой И есть у пользователя
        if active_role != required_role:
            return False
        
        user_roles = list(UserRole.objects.filter(user=request.user).values_list('role__id_role', flat=True))
        return required_role in user_roles
