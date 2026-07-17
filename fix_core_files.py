import os

# 1. Чистая перезапись accounts/serializers.py
serializers_code = """from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
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
        
        errors = []
        password = attrs['new_password']
        if len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов.")
        if not any(c.isupper() for c in password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву.")
        if not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать хотя бы одну цифру.")
        if not any(not c.isalnum() for c in password):
            errors.append("Пароль должен содержать хотя бы один спецсимвол.")
            
        if errors:
            raise serializers.ValidationError({"new_password": " ".join(errors)})
            
        return attrs

# Алиас на всякий случай, если где-то остался старый импорт
ChangePasswordSerializer = ForceChangePasswordSerializer
"""
with open('accounts/serializers.py', 'w', encoding='utf-8') as f:
    f.write(serializers_code)

# 2. Чистая перезапись accounts/views.py (убираем весь мусор)
views_code = """from django.http import JsonResponse, HttpResponse
from core.models import Campus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ForceChangePasswordSerializer

def hello(request):
    campuses = Campus.objects.all()
    sp = ''.join([f'<li><b>🏢 {k.id_campus}</b><br><small>📍 {k.address}</small></li>' for k in campuses])
    return HttpResponse(f"<html><body><h1>✅ Django работает!</h1><ul>{sp}</ul></body></html>")

def api_campuses(request):
    campuses = Campus.objects.values('id_campus', 'address')
    return JsonResponse({'success': True, 'count': len(campuses), 'data': list(campuses)}, json_dumps_params={'ensure_ascii': False})

class ForceChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ForceChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.requires_password_change = False
            user.save()
            return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
with open('accounts/views.py', 'w', encoding='utf-8') as f:
    f.write(views_code)

print("✅ Файлы accounts/serializers.py и accounts/views.py успешно и чисто перезаписаны!")
