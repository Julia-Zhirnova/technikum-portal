"""БП 1.4: API endpoints для email-восстановления пароля."""
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PasswordRecoveryToken
from .serializers import RecoveryRequestSerializer, RecoveryConfirmSerializer
from .tasks import send_password_recovery_email

logger = logging.getLogger(__name__)
User = get_user_model()


class RecoveryRequestView(APIView):
    """POST /api/auth/recovery/request/ — запрос восстановления пароля.
    
    Спецификация БП 1.4:
    - Создаёт PasswordRecoveryToken с TTL 15 минут
    - Отправляет email через Celery task
    - Rate limit: 3 запроса в час на email
    - Несуществующий email → 200 (без утечки информации)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RecoveryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        # Rate limiting: 3 запроса в час на email
        rate_limit_key = f'recovery_requests:{email}'
        try:
            current_requests = cache.get(rate_limit_key, 0)
            if current_requests >= 3:
                return Response(
                    {'detail': 'Слишком много запросов. Повторите через час.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            cache.set(rate_limit_key, current_requests + 1, 3600)  # 1 час TTL
        except Exception as e:
            logger.warning(f"Redis unavailable for rate limiting: {e}")
        
        # Ищем пользователя
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Возвращаем 200 даже для несуществующего email (без утечки)
            return Response({'detail': 'Если пользователь существует, ему отправлено письмо.'}, status=status.HTTP_200_OK)
        
        # Создаём токен
        token_obj = PasswordRecoveryToken.objects.create_for_user(user)
        
        # Отправляем email через Celery (eager mode в тестах)
        try:
            send_password_recovery_email.delay(user.pk, token_obj.token)
        except Exception as e:
            logger.error(f"Failed to queue recovery email task: {e}")
        
        return Response({'detail': 'Если пользователь существует, ему отправлено письмо.'}, status=status.HTTP_200_OK)


class RecoveryConfirmView(APIView):
    """POST /api/auth/recovery/confirm/ — подтверждение восстановления пароля.
    
    Спецификация БП 1.4:
    - Проверяет валидность токена (не истёк, не использован)
    - Меняет пароль
    - Помечает токен использованным (одноразовость)
    - Инвалидирует все refresh-токены (blacklist)
    - Сбрасывает requires_password_change
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RecoveryConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token_value = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Ищем токен
        try:
            token_obj = PasswordRecoveryToken.objects.get(token=token_value)
        except PasswordRecoveryToken.DoesNotExist:
            return Response(
                {'detail': 'Недействительный токен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Проверяем валидность
        if not token_obj.is_valid:
            return Response(
                {'detail': 'Токен истёк или уже использован.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user = token_obj.user
        
        # Меняем пароль
        user.set_password(new_password)
        user.requires_password_change = False
        user.save()
        
        # Помечаем токен использованным
        token_obj.mark_used()
        
        # Инвалидируем все refresh-токены (blacklist)
        try:
            from rest_framework_simplejwt.token_blacklist.models import (
                OutstandingToken, BlacklistedToken,
            )
            for token in OutstandingToken.objects.filter(user=user):
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception as e:
            logger.warning(f"Failed to blacklist tokens: {e}")
        
        # Логируем в auditlog
        try:
            from core.models import AuditLog
            AuditLog.objects.create(
                user=user,
                action_type='password_recovery',
                object_type='User',
                object_id=str(user.pk),
                details={'email': user.email},
            )
        except Exception as e:
            logger.warning(f"Failed to create audit log: {e}")
        
        return Response({'detail': 'Пароль успешно изменён.'}, status=status.HTTP_200_OK)
