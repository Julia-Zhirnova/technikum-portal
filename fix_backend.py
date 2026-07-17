import os

# 1. Обновляем config/settings.py
settings_path = 'config/settings.py'
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'TOKEN_OBTAIN_SERIALIZER' not in content:
    content = content.replace(
        'SIMPLE_JWT = {',
        'SIMPLE_JWT = {\n    "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.CustomTokenObtainPairSerializer",'
    )
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ config/settings.py обновлен (добавлен CustomTokenObtainPairSerializer)")
else:
    print("ℹ️ config/settings.py уже содержит настройку сериализатора")

# 2. Перезаписываем accounts/serializers.py целиком
serializer_code = """from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

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
        try:
            data = super().validate(attrs)
            data['requires_password_change'] = self.user.requires_password_change
            return data
        except AuthenticationFailed as e:
            error_msg = str(e).lower()
            if "active" in error_msg or "no active account" in error_msg:
                raise AuthenticationFailed(_("Ваша учетная запись заблокирована. Обратитесь к администратору."))
            raise e
"""
with open('accounts/serializers.py', 'w', encoding='utf-8') as f:
    f.write(serializer_code)
print("✅ accounts/serializers.py успешно перезаписан")
