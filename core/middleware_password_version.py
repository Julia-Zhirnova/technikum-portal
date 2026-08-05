"""Middleware для проверки password_version в JWT токенах.

БП 1.1.4: Инвалидация старых токенов после смены пароля.
"""
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordVersionMiddleware:
    """Проверяет, что password_version в JWT совпадает с текущим значением в БД."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):
        # Пропускаем запросы без Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return self.get_response(request)

        # Пропускаем endpoint'ы, которые не требуют проверки
        if request.path in ['/api/token/', '/api/token/refresh/', '/api/logout/']:
            return self.get_response(request)

        try:
            # Извлекаем токен
            token = auth_header.split(' ')[1]
            validated_token = self.jwt_auth.get_validated_token(token)
            
            # Получаем user_id и password_version из токена
            user_id = validated_token.get('user_id')
            token_password_version = validated_token.get('password_version', 1)

            if user_id:
                # Получаем текущего пользователя из БД
                try:
                    user = User.objects.get(id_user=user_id)
                    current_password_version = getattr(user, 'password_version', 1)

                    # Сравниваем версии
                    if token_password_version != current_password_version:
                        return JsonResponse(
                            {
                                'code': 'password_changed',
                                'detail': 'Ваш пароль был изменён. Войдите снова.'
                            },
                            status=401
                        )
                except User.DoesNotExist:
                    pass  # Пользователь не найден — пусть JWT auth обработает это

        except (InvalidToken, IndexError, ValueError):
            pass  # Токен невалиден — пусть DRF обработает это

        return self.get_response(request)
