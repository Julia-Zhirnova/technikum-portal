"""Представления аутентификации с логированием в AuditLog.

БП 1.1.2: Логирование аутентификации (ФЗ-152).
"""
import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import AuditLog

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """Извлекает IP-адрес клиента из запроса."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


class AuditTokenObtainPairView(TokenObtainPairView):
    """Расширение TokenObtainPairView с логированием в AuditLog."""

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос с логированием аудита."""
        ip_address = get_client_ip(request)
        email = request.data.get('email', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        try:
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            # Логируем неудачную попытку входа
            AuditLog.objects.create(
                user=None,
                action_type=AuditLog.ActionType.LOGIN_FAIL,
                object_type='User',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'email': email,
                    'reason': str(e),
                },
            )
            logger.warning(f"Неудачная попытка входа: {email} с IP {ip_address}")
            raise

        if response.status_code == status.HTTP_200_OK:
            # Успешный вход — логируем
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

            AuditLog.objects.create(
                user=user,
                action_type=AuditLog.ActionType.LOGIN_SUCCESS,
                object_type='User',
                object_id=str(user.pk) if user else '',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'email': email,
                },
            )
            logger.info(f"Успешный вход: {email} с IP {ip_address}")

        return response


class LogoutView(APIView):
    """Представление выхода из системы с логированием."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Обрабатывает выход: инвалидирует refresh-токен, логирует в AuditLog."""
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Пытаемся занести refresh-токен в blacklist
        refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Токен уже невалиден или blacklist не настроен

        # Логируем выход
        AuditLog.objects.create(
            user=request.user,
            action_type=AuditLog.ActionType.LOGOUT,
            object_type='User',
            object_id=str(request.user.pk),
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                'email': request.user.email,
            },
        )
        logger.info(f"Выход: {request.user.email} с IP {ip_address}")

        return Response(
            {'detail': 'Вы успешно вышли из системы.'},
            status=status.HTTP_200_OK,
        )
