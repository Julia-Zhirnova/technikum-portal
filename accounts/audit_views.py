"""Представления аутентификации с логированием в AuditLog.

БП 1.1.2: Логирование аутентификации (ФЗ-152).
"""
import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

from core.models import AuditLog
from accounts.brute_force import BruteForceProtection

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
        """Обрабатывает POST-запрос с логированием аудита и защитой от брутфорса."""
        ip_address = get_client_ip(request)
        email = request.data.get('email', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # БП 1.1.5: Brute Force Protection — проверяем блокировку IP
        brute_force = BruteForceProtection(ip_address)
        if brute_force.is_blocked():
            logger.warning(f"Заблокированный IP {ip_address} пытается войти как {email}")
            return Response(
                {
                    'detail': 'Слишком много попыток. Повторите через 15 минут.',
                    'code': 'ip_blocked',
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed as e:
            # БП 1.1.5: Записываем неудачную попытку
            attempts_count = brute_force.record_failed_attempt()

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
                    'attempts_count': attempts_count,
                },
            )
            logger.warning(f"Неудачная попытка входа: {email} с IP {ip_address} (попытка #{attempts_count})")

            # Если IP только что заблокирован — возвращаем 429
            if brute_force.is_blocked():
                return Response(
                    {
                        'detail': 'Слишком много попыток. Повторите через 15 минут.',
                        'code': 'ip_blocked',
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Если нужна капча — добавляем require_captcha в ответ
            error_data = {'detail': str(e)}
            if brute_force.require_captcha():
                error_data['require_captcha'] = True
                error_data['attempts_count'] = attempts_count

            return Response(error_data, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == status.HTTP_200_OK:
            # БП 1.1.5: Успешный вход — сбрасываем счётчик попыток
            brute_force.record_successful_login()

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

            # БП 1.1.4: Устанавливаем refresh-токен в httpOnly cookie
            refresh_token = response.data.get('refresh')
            if refresh_token:
                response.set_cookie(
                    key='refresh',
                    value=refresh_token,
                    httponly=True,
                    secure=False,  # True в production (HTTPS)
                    samesite='Lax',
                    max_age=7*24*60*60,  # 7 дней
                    path='/'
                )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """БП 1.1.6: Обновление access-токена с поддержкой refresh из httpOnly cookie.

    Если refresh_token не передан в теле запроса, берёт его из httpOnly cookie.
    Новый access_token возвращается в теле ответа, новый refresh_token — в cookie.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # Если refresh не в теле — пробуем достать из cookie
        if 'refresh' not in request.data:
            refresh_from_cookie = request.COOKIES.get('refresh')
            if refresh_from_cookie:
                # Копируем data и добавляем refresh
                request.data._mutable = True
                request.data['refresh'] = refresh_from_cookie
                request.data._mutable = False

        # Вызываем стандартную логику TokenRefreshView
        response = super().post(request, *args, **kwargs)

        # Если получен новый refresh_token (ROTATE_REFRESH_TOKENS=True),
        # обновляем cookie
        new_refresh = response.data.get('refresh')
        if new_refresh:
            response.set_cookie(
                key='refresh',
                value=new_refresh,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=7*24*60*60,
                path='/'
            )

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
