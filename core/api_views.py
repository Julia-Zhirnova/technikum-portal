from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Student, Group, Statement
from .serializers_update import StudentProfileUpdateSerializer
from .serializers import (
    UserProfileSerializer,
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
    """Разрешение для кураторов и администраторов."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Админы всегда имеют доступ
        if request.user.is_staff:
            return True
        
        # Проверяем роль curator
        from .models import UserRole
        return UserRole.objects.filter(user=request.user, role__id_role='curator').exists()

class IsTeacher(permissions.BasePermission):
    """Разрешение для преподавателей."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Проверяем роль teacher через UserRole
        from .models import UserRole
        return UserRole.objects.filter(user=request.user, role__id_role='teacher').exists()

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

class CuratorGroupView(generics.ListAPIView):
    """
    GET /api/curator/group/ — список групп куратора со студентами
    """
    serializer_class = GroupWithStudentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCurator]
    pagination_class = None
    
    def get_queryset(self):
        user = self.request.user
        # Проверяем, что пользователь имеет роль куратора
        from .models import UserRole
        has_curator_role = UserRole.objects.filter(
            user=user, 
            role__id_role='curator'
        ).exists()
        
        if not has_curator_role:
            return Group.objects.none()
        
        # Возвращаем ТОЛЬКО группы, где пользователь назначен куратором
        return Group.objects.filter(curator=user).order_by('id_group')

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



class StudentProfileUpdateView(APIView):
    """
    PATCH /api/student/profile/update/ — обновление профиля студента
    """
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def patch(self, request, *args, **kwargs):
        try:
            student = Student.objects.get(user=request.user)
            print(f"🎯 Найден студент для обновления: {student.snils}")
            
            serializer = StudentProfileUpdateSerializer(student, data=request.data, partial=True)
            
            if serializer.is_valid():
                print(f"✅ Данные валидны, вызываем update()")
                updated_student = serializer.update(student, serializer.validated_data)
                print(f"✅ Обновление завершено")
                
                # Возвращаем обновленный профиль
                profile_serializer = StudentProfileSerializer(updated_student)
                return Response(profile_serializer.data)
            else:
                print(f"❌ Ошибки валидации: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Student.DoesNotExist:
            return Response({'error': 'Студент не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WhoAmIView(APIView):
    """
    GET /api/whoami/ — роли текущего пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from .models import UserRole
        user = request.user
        roles = []
        
        # Получаем все роли пользователя из таблицы UserRole
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        for ur in user_roles:
            roles.append(ur.role.id_role)
        
        # Добавляем админа, если is_staff
        if user.is_staff and 'admin' not in roles:
            roles.append('admin')
        
        return Response({
            'user_id': user.id_user,
            'email': user.email,
            'full_name': user.get_full_name(),
            'roles': roles,
        })


# ==============================================================================
# API ENDPOINTS ДЛЯ ПОЛЬЗОВАТЕЛЯ (КУРАТОР/ПРЕПОДАВАТЕЛЬ/АДМИН)
# ==============================================================================

class UserProfileView(generics.RetrieveAPIView):
    """
    GET /api/user/profile/ — профиль куратора/преподавателя/админа
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# ==============================================================================
# API ENDPOINTS ДЛЯ ПОЛУЧЕНИЯ СПРАВОЧНИКОВ (ВЫПАДАЮЩИЕ СПИСКИ)
# ==============================================================================

class ReferencesView(APIView):
    """
    GET /api/references/ — получение всех вариантов choices из моделей
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from .models import Health, Military, Family, FamilyMember, Passport
        
        references = {
            # Здоровье
            'health_status': [{'value': c[0], 'label': c[1]} for c in Health._meta.get_field('status').choices],
            
            # Воинский учет
            'fitness_category': [{'value': c[0], 'label': c[1]} for c in Military._meta.get_field('fitness_category').choices],
            
            # Семья
            'family_status': [{'value': c[0], 'label': c[1]} for c in Family._meta.get_field('status').choices],
            'housing_type': [{'value': c[0], 'label': c[1]} for c in Family._meta.get_field('housing_type').choices],
            
            # Члены семьи
            'relation': [{'value': c[0], 'label': c[1]} for c in FamilyMember._meta.get_field('relation').choices],
            
            # Паспорт
            'gender': [
                {'value': 'мужской', 'label': 'Мужской'},
                {'value': 'женский', 'label': 'Женский'},
            ],
        }
        
        return Response(references)
