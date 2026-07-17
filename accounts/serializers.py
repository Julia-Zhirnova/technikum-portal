from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        from core.models import UserRole
        roles = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        token['roles'] = roles
        token['requires_password_change'] = user.requires_password_change
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        
        # 1. Проверяем, существует ли пользователь
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Пользователь не найден — общая ошибка (защита от перебора)
            raise AuthenticationFailed(_("Неверный email или пароль"))
        
        # 2. Проверяем, активен ли пользователь
        if not user.is_active:
            raise AuthenticationFailed(_("Ваша учетная запись заблокирована. Обратитесь к администратору."))
        
        # 3. Проверяем пароль через стандартный механизм
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            # Пароль неверный — общая ошибка
            raise AuthenticationFailed(_("Неверный email или пароль"))
        
        # 4. Добавляем roles и requires_password_change в ответ
        from core.models import UserRole
        data['roles'] = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        data['requires_password_change'] = user.requires_password_change
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
            
        return attrs
