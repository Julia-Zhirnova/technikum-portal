from django.http import JsonResponse, HttpResponse
from core.models import Campus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ForceChangePasswordSerializer


def hello(request):
    """Главная страница портала."""
    campuses = Campus.objects.all()
    sp = ''.join([
        f'<li><b>🏢 {k.id_campus}</b><br><small>📍 {k.address}</small></li>'
        for k in campuses
    ])
    return HttpResponse(f"""
<html>
<head>
<meta charset="utf-8">
<title>ТехноПортал — Люберецкий техникум</title>
</head>
<body style="font-family: Arial; max-width: 900px; margin: 40px auto; padding: 20px;">
<h1>🚀 ТехноПортал работает!</h1>
<p><b>ГБПОУ МО «Люберецкий техникум имени Ю. А. Гагарина»</b></p>
<h2>🏢 Корпуса техникума ({campuses.count()} шт.):</h2>
<ul>{sp}</ul>
</body>
</html>
""")


def api_campuses(request):
    """API эндпоинт со списком корпусов."""
    campuses = Campus.objects.values('id_campus', 'address')
    return JsonResponse({
        'success': True,
        'count': len(campuses),
        'data': list(campuses)
    }, json_dumps_params={'ensure_ascii': False})


class ForceChangePasswordView(APIView):
    """Принудительная смена пароля (Функция 1.2)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Принудительная смена пароля. БП 1.2: TC004-TC009, TC031, TC041, TC048."""
        from django.core.cache import caches
        from django.conf import settings
        from django.utils import timezone

        user = request.user

        # БП 1.2-TC031/TC032: извлечение IP и User-Agent для аудита
        from accounts.audit_views import get_client_ip
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        # БП 1.2-TC009: запрет смены, если флаг уже сброшен
        if not getattr(user, 'requires_password_change', False):
            return Response(
                {'detail': 'Смена пароля не требуется'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # БП 1.2-TC007/TC008: Rate limiting по user_id (не по IP)
        cache = None
        blocked_key = None
        attempts_key = None
        try:
            cache = caches[settings.BRUTE_FORCE_PROTECTION['CACHE_ALIAS']]
            blocked_key = f'pwd_change_blocked:{user.pk}'
            attempts_key = f'pwd_change_attempts:{user.pk}'

            if cache.get(blocked_key):
                return Response(
                    {'detail': 'Слишком много попыток. Повторите через 5 минут'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
        except Exception:
            # БП 1.2-TC041: Graceful degradation — Redis недоступен
            cache = None

        # БП 1.2-TC007: Проверяем блокировку ДО валидации
        if cache is not None and blocked_key:
            try:
                if cache.get(blocked_key):
                    return Response(
                        {'detail': 'Слишком много попыток. Повторите через 5 минут'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
            except Exception:
                pass

        serializer = ForceChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            # Успешная смена пароля
            user.set_password(serializer.validated_data['new_password'])
            user.requires_password_change = False
            # БП 1.2-TC004: инкремент password_version для инвалидации токенов
            user.password_version = getattr(user, 'password_version', 1) + 1
            if hasattr(user, 'password_changed_at'):
                user.password_changed_at = timezone.now()
            user.save()

            # БП 1.2-TC005/TC047: blacklist всех refresh-токенов пользователя
            try:
                from rest_framework_simplejwt.token_blacklist.models import (
                    OutstandingToken, BlacklistedToken,
                )
                for token in OutstandingToken.objects.filter(user=user):
                    BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                pass  # Приложение token_blacklist может быть не установлено

            # БП 1.2-TC048: сброс счётчика и блокировки при успехе
            if cache is not None:
                try:
                    cache.delete(attempts_key)
                    cache.delete(blocked_key)
                except Exception:
                    pass

            # БП 1.2-TC031: логирование успешной смены в auditlog
            try:
                from core.models import AuditLog
                AuditLog.objects.create(
                    user=user,
                    action_type=AuditLog.ActionType.PASSWORD_CHANGE,
                    object_type='User',
                    object_id=str(user.pk),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'email': user.email},
                )
            except Exception:
                pass

            return Response(
                {"detail": "Пароль успешно изменен."},
                status=status.HTTP_200_OK
            )

        # Неудачная валидация → инкремент счётчика попыток
        # БП 1.2-TC007: инкремент при ЛЮБОЙ ошибке (не только после валидации)
        if cache is not None and attempts_key:
            try:
                current = cache.get(attempts_key)
                attempts = (int(current) if current is not None else 0) + 1
                cache.set(attempts_key, attempts, timeout=300)
            except Exception:
                attempts = 0

            # БП 1.2-TC007: После 3 неудачных попыток → блокировка на 5 минут (TTL 300)
            if attempts >= 3:
                try:
                    cache.set(blocked_key, 1, timeout=300)
                except Exception:
                    pass

        # БП 1.2-TC032: логирование неудачной попытки
        try:
            from core.models import AuditLog
            AuditLog.objects.create(
                user=user,
                action_type='password_change_failed',
                object_type='User',
                object_id=str(user.pk),
                ip_address=ip_address,
                user_agent=user_agent,
                details={'email': user.email, 'errors': serializer.errors},
            )
        except Exception:
            pass

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
