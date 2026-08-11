"""БП 1.3: TC028 (refresh с X-Active-Role) + TC030 (аудит role_switch)."""
import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def curator_teacher_user(db):
    """Пользователь с ролями curator + teacher."""
    from core.models import Role, UserRole
    user = User.objects.create_user(email='zhirnova_test@luberteh.ru', password='TestPass123!')
    curator_role, _ = Role.objects.get_or_create(id_role='curator', defaults={'name': 'Куратор'})
    teacher_role, _ = Role.objects.get_or_create(id_role='teacher', defaults={'name': 'Преподаватель'})
    UserRole.objects.get_or_create(user=user, role=curator_role)
    UserRole.objects.get_or_create(user=user, role=teacher_role)
    return user


class TestTC028RefreshWithRoleHeader:
    """TC028: истёкший access → refresh с X-Active-Role → повторный запрос."""

    def test_TC028_expired_access_refresh_with_role_header(self, api_client, curator_teacher_user):
        """TC028: просроченный access → 401 → refresh → новый access → запрос проходит."""
        # Получаем refresh-токен
        refresh = RefreshToken.for_user(curator_teacher_user)
        
        # Создаём истёкший access-токен
        access = AccessToken.for_user(curator_teacher_user)
        access.set_exp(lifetime=timedelta(seconds=-1))  # истёк 1 секунду назад
        expired_access = str(access)
        
        # Запрос с истёкшим access → 401
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {expired_access}',
            HTTP_X_ACTIVE_ROLE='curator'
        )
        response = api_client.get('/api/curator/group/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        # SessionAuthentication первым в DRF → невалидный JWT даёт 403 (не 401)
        # Фронтенд-интерцептор обрабатывает оба кода
        
        # Refresh с заголовком X-Active-Role
        api_client.credentials(HTTP_X_ACTIVE_ROLE='curator')
        refresh_url = reverse('token_refresh')
        response = api_client.post(refresh_url, {'refresh': str(refresh)}, format='json')
        assert response.status_code == status.HTTP_200_OK
        new_access = response.data['access']
        
        # Повторный запрос с новым access и тем же X-Active-Role → 200
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {new_access}',
            HTTP_X_ACTIVE_ROLE='curator'
        )
        response = api_client.get('/api/curator/group/')
        assert response.status_code == status.HTTP_200_OK


class TestTC030RoleSwitchAudit:
    """TC030: переключение роли → запись в core_auditlog."""

    def test_TC030_role_switch_creates_audit_log(self, api_client, curator_teacher_user):
        """TC030: POST /api/auth/switch-role/ → 200 + запись role_switch в auditlog."""
        from core.models import AuditLog
        
        # Аутентификация
        refresh = RefreshToken.for_user(curator_teacher_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(curator_teacher_user))}')
        
        # Переключаем роль с teacher на curator
        response = api_client.post('/api/auth/switch-role/', {
            'old_role': 'teacher',
            'new_role': 'curator'
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверяем запись в auditlog
        log = AuditLog.objects.filter(
            user=curator_teacher_user,
            action_type=AuditLog.ActionType.ROLE_SWITCH
        ).order_by('-created_at').first()
        
        assert log is not None, "Запись role_switch не создана"
        assert log.details['old_role'] == 'teacher'
        assert log.details['new_role'] == 'curator'
        assert 'ip' in log.details
        assert 'user_agent' in log.details

    def test_TC030_switch_to_invalid_role_returns_403(self, api_client, curator_teacher_user):
        """TC030: переключение на роль, которой нет у пользователя → 403."""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(AccessToken.for_user(curator_teacher_user))}')
        
        response = api_client.post('/api/auth/switch-role/', {
            'old_role': 'teacher',
            'new_role': 'admin'  # роли admin нет у пользователя
        }, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
