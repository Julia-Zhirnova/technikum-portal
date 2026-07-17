import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
from core.models import Role, UserRole

code = "from rest_framework_simplejwt.serializers import TokenObtainPairSerializer\nfrom rest_framework_simplejwt.exceptions import AuthenticationFailed\nfrom django.utils.translation import gettext_lazy as _\nclass CustomTokenObtainPairSerializer(TokenObtainPairSerializer):\n    @classmethod\n    def get_token(cls, user):\n        token = super().get_token(user)\n        from core.models import UserRole\n        token['roles'] = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))\n        token['requires_password_change'] = user.requires_password_change\n        return token\n    def validate(self, attrs):\n        try:\n            data = super().validate(attrs)\n            data['requires_password_change'] = self.user.requires_password_change\n            return data\n        except AuthenticationFailed as e:\n            if 'active' in str(e).lower() or 'no active account' in str(e).lower():\n                raise AuthenticationFailed(_('Ваша учетная запись заблокирована. Обратитесь к администратору.'))\n            raise e"
with open('accounts/serializers.py', 'w') as f: f.write(code)

with open('config/settings.py', 'r') as f: c = f.read()
if 'TOKEN_OBTAIN_SERIALIZER' not in c:
    c = c.replace('SIMPLE_JWT = {', 'SIMPLE_JWT = {\n    "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.CustomTokenObtainPairSerializer",')
    with open('config/settings.py', 'w') as f: f.write(c)

User = get_user_model()
u1, _ = User.objects.get_or_create(email='test_password_change@luberteh.ru')
u1.set_password('OldPassword123!'); u1.requires_password_change = True; u1.is_active = True; u1.save()
r1, _ = Role.objects.get_or_create(id_role='student', defaults={'name': 'Студент'})
UserRole.objects.get_or_create(user=u1, role=r1)

u2, _ = User.objects.get_or_create(email='blocked_user@luberteh.ru')
u2.set_password('Password123!'); u2.is_active = False; u2.save()
UserRole.objects.get_or_create(user=u2, role=r1)
print("✅ Бэкенд и тестовые пользователи исправлены!")
