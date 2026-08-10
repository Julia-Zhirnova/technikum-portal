"""Представления аутентификации с логированием в AuditLog.

БП 1.1.2, 1.1.4, 1.1.6: Логирование аутентификации (ФЗ-152).
"""
import logging
from django.conf import settings
from django.core.cache import caches

from rest_framework import status
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from core.models import AuditLog, UserSession
from accounts.brute_force import BruteForceProtection


import ipaddress as ipaddress_module

def validate_ip(ip_str: str) -> str:
    """Валидирует IP-адрес. Возвращает валидный IP или '127.0.0.1' для невалидных."""
    if not ip_str:
        return '127.0.0.1'
    try:
        ipaddress_module.ip_address(ip_str)
        return ip_str
    except ValueError:
        return '127.0.0.1'


logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """Извлекает и валидирует IP-адрес клиента из запроса."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        raw_ip = x_forwarded_for.split(',')[0].strip()
    else:
        raw_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return validate_ip(raw_ip)


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

            # Логируем неудачную попытку входа (с обработкой ошибок БД)
            try:
                AuditLog.objects.create(
                    user=None,
                    action_type=AuditLog.ActionType.LOGIN_FAIL,
                    object_type='User',
                    ip_address=ip_address,
                    user_agent=user_agent[:500],
                    details={
                        'email': email,
                        'reason': str(e),
                        'attempts_count': attempts_count,
                    },
                )
            except Exception as log_error:
                logger.error(f"Не удалось записать AuditLog (login_fail): {log_error}")
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

            # БП 1.1-002: обновляем last_login при успешном входе
            if user is not None:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])

            try:
                AuditLog.objects.create(
                    user=user,
                    action_type=AuditLog.ActionType.LOGIN_SUCCESS,
                    object_type='User',
                    object_id=str(user.pk) if user else '',
                    ip_address=ip_address,
                    user_agent=user_agent[:500],
                    details={
                        'email': email,
                    },
                )
                logger.info(f"Успешный вход: {email} с IP {ip_address}")
            except Exception as log_error:
                logger.error(f"Не удалось записать AuditLog (login_success): {log_error}")

            # БП 1.1-051: Создание записи UserSession
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                from django.conf import settings
                
                # Получаем refresh-токен из cookie или тела ответа
                refresh_token = response.cookies.get('refresh')
                if refresh_token:
                    refresh_token_value = refresh_token.value
                else:
                    refresh_token_value = response.data.get('refresh')
                
                if refresh_token_value:
                    token_obj = RefreshToken(refresh_token_value)
                    session_id = token_obj.get('jti')  # JWT ID
                    expires_at = timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
                    
                    UserSession.objects.create(
                        user=user,
                        session_id=session_id,
                        ip_address=ip_address,
                        user_agent=user_agent[:500],
                        expires_at=expires_at,
                    )
                    logger.info(f"Создана сессия {session_id} для {email}")
            except Exception as session_error:
                logger.error(f"Не удалось создать UserSession: {session_error}")

            # БП 1.1.4: Устанавливаем refresh-токен в httpOnly cookie
            refresh_token = response.data.get('refresh')
            if refresh_token:
                response.set_cookie(
                    key='refresh',
                    value=refresh_token,
                    httponly=True,
                    secure=False,  # True в production (HTTPS)
                    samesite='Strict',  # БП 1.1.4: SameSite=Strict
                    max_age=7*24*60*60,  # 7 дней
                    path='/'
                )
                # БП 1.1.4: Удаляем refresh из тела ответа (только в cookie)
                del response.data['refresh']

        return response



class RefreshTokenRateLimiter:
    """БП 1.1-TC038: Rate Limit для /api/token/refresh/.
    
    Защищает endpoint обновления токенов от DDoS-атак.
    Ограничивает количество запросов на refresh от одного IP.
    
    Параметры (берутся из settings):
    - RATE_LIMIT_TOKEN_REFRESH_MAX_REQUESTS: макс. запросов в окне (по умолчанию 30)
    - RATE_LIMIT_TOKEN_REFRESH_WINDOW_SECONDS: окно в секундах (по умолчанию 60)
    """
    
    def __init__(self, ip_address: str):
        self.ip = ip_address
        # Параметры по умолчанию (из спецификации БП 1.1-TC038)
        self.max_requests = getattr(settings, 'RATE_LIMIT_TOKEN_REFRESH_MAX_REQUESTS', 30)
        self.window_seconds = getattr(settings, 'RATE_LIMIT_TOKEN_REFRESH_WINDOW_SECONDS', 60)
        try:
            self.cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
        except Exception as e:
            logger.error(f"Не удалось получить кэш для rate limit: {e}")
            self.cache = None
    
    @property
    def _key(self) -> str:
        return f"refresh_rate_limit:{self.ip}"
    
    def _is_available(self) -> bool:
        """Проверяет доступность Redis."""
        if self.cache is None:
            return False
        try:
            self.cache.get('__connectivity_check__')
            return True
        except Exception as e:
            logger.warning(f"Redis unavailable, rate limit disabled: {e}")
            return False
    
    def check_rate_limit(self) -> tuple:
        """Проверяет, не превышен ли лимит.
        
        Returns:
            tuple: (is_limited: bool, attempts_count: int, retry_after: int)
        """
        if not self._is_available():
            # Graceful degradation: если Redis недоступен, пропускаем
            return False, 0, 0
        
        try:
            current = self.cache.get(self._key)
            attempts = int(current) if current is not None else 0
            return attempts >= self.max_requests, attempts, self.window_seconds
        except Exception as e:
            logger.error(f"Ошибка проверки rate limit: {e}")
            return False, 0, 0
    
    def record_request(self) -> int:
        """Записывает запрос. Возвращает новое количество попыток."""
        if not self._is_available():
            return 0
        
        try:
            current = self.cache.get(self._key)
            new_value = (int(current) if current is not None else 0) + 1
            self.cache.set(self._key, new_value, self.window_seconds)
            return new_value
        except Exception as e:
            logger.error(f"Ошибка записи rate limit: {e}")
            return 0


class CookieTokenRefreshView(TokenRefreshView):
    """БП 1.1.6: Обновление access-токена с поддержкой refresh из httpOnly cookie.

    Если refresh_token не передан в теле запроса, берёт его из httpOnly cookie.
    Новый access_token возвращается в теле ответа, новый refresh_token — в cookie.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # БП 1.1-TC038: Rate Limit для /api/token/refresh/
        ip_address = get_client_ip(request)
        rate_limiter = RefreshTokenRateLimiter(ip_address)
        is_limited, attempts, retry_after = rate_limiter.check_rate_limit()
        if is_limited:
            logger.warning(f"Rate limit превышен для IP {ip_address} ({attempts} запросов)")
            response = Response(
                {
                    'detail': f'Слишком много запросов. Повторите через {retry_after} секунд.',
                    'code': 'too_many_requests',
                    'retry_after': retry_after,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
            response['Retry-After'] = str(retry_after)
            return response
        
        # Успешный запрос — увеличиваем счётчик
        rate_limiter.record_request()
        
        # Если refresh не в теле — пробуем достать из cookie
        if 'refresh' not in request.data:
            refresh_from_cookie = request.COOKIES.get('refresh')
            if refresh_from_cookie:
                # request.data может быть dict (JSON) или QueryDict (form-data)
                if hasattr(request.data, '_mutable'):
                    # QueryDict — нужно временно сделать mutable
                    request.data._mutable = True
                    request.data['refresh'] = refresh_from_cookie
                    request.data._mutable = False
                else:
                    # Обычный dict (JSON body) — просто добавляем ключ
                    request.data['refresh'] = refresh_from_cookie

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
                samesite='Strict',
                max_age=7*24*60*60,
                path='/'
            )
            # Удаляем refresh из тела ответа
            del response.data['refresh']

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

        # Логируем выход (с обработкой ошибок БД)
        try:
            AuditLog.objects.create(
                user=request.user,
                action_type=AuditLog.ActionType.LOGOUT,
                object_type='User',
                object_id=str(request.user.pk),
                ip_address=ip_address,
                user_agent=user_agent[:500],
                details={
                    'email': request.user.email,
                },
            )
            logger.info(f"Выход: {request.user.email} с IP {ip_address}")
        except Exception as log_error:
            logger.error(f"Не удалось записать AuditLog (logout): {log_error}")

        # Удаляем cookie с refresh-токеном
        response = Response(
            {'detail': 'Вы успешно вышли из системы.'},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie('refresh', path='/')
        return response
