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
        token['roles'] = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        token['requires_password_change'] = user.requires_password_change
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(_("Неверный email или пароль"))
        if not user.is_active:
            raise AuthenticationFailed(_("Ваша учетная запись заблокирована. Обратитесь к администратору."))
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed(_("Неверный email или пароль"))
        from core.models import UserRole
        data['roles'] = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        data['requires_password_change'] = user.requires_password_change
        return data

class ForceChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError({"new_password": "Новый пароль не должен совпадать с текущим."})
        try:
            validate_password(attrs['new_password'], user=user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        return attrs
