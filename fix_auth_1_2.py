import os

# 1. Полностью перезаписываем accounts/serializers.py (гарантируем правильные импорты)
serializers_code = """from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
"""
with open('accounts/serializers.py', 'w', encoding='utf-8') as f:
    f.write(serializers_code)
print("✅ accounts/serializers.py обновлен")

# 2. Безопасно обновляем accounts/views.py
with open('accounts/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

if 'from .serializers import ForceChangePasswordSerializer' not in views_content:
    views_content = "from .serializers import ForceChangePasswordSerializer\n" + views_content

if 'class ForceChangePasswordView' not in views_content:
    view_code = """
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
    views_content += view_code

with open('accounts/views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)
print("✅ accounts/views.py обновлен")

# 3. Полностью перезаписываем ChangePasswordPage.tsx
tsx_code = """import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Card, CardContent, Typography, TextField, Button, Alert, CircularProgress, LinearProgress } from '@mui/material';
import LockResetIcon from '@mui/icons-material/LockReset';
import api from '../services/api';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const getStrength = (pass: string) => {
    let s = 0;
    if (pass.length >= 8) s += 25;
    if (/[A-Z]/.test(pass)) s += 25;
    if (/[0-9]/.test(pass)) s += 25;
    if (/[^A-Za-z0-9]/.test(pass)) s += 25;
    return s;
  };

  const strength = getStrength(newPassword);
  const strengthColor = strength < 50 ? '#f44336' : strength < 100 ? '#ff9800' : '#4caf50';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.post('/auth/force-change-password/', { new_password: newPassword, confirm_password: confirmPassword });
      setSuccess(true);
      setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      const d = err.response?.data;
      setError(d?.new_password?.[0] || d?.confirm_password?.[0] || d?.detail || 'Ошибка при смене пароля.');
    } finally {
      setLoading(false);
    }
  };

  if (success) return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Card sx={{ width: '100%', boxShadow: 3, textAlign: 'center', p: 4 }}>
        <LockResetIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
        <Typography variant="h5" fontWeight="bold" color="success.main">Пароль успешно изменен!</Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>Перенаправление на страницу входа...</Typography>
      </Card>
    </Container>
  );

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Card sx={{ width: '100%', boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <LockResetIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
            <Typography variant="h5" fontWeight="bold">Смена пароля</Typography>
            <Typography variant="body2" color="text.secondary">Требуется задать новый надежный пароль.</Typography>
          </Box>
          <form onSubmit={handleSubmit}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField fullWidth label="Новый пароль" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required margin="normal" />
            {newPassword.length > 0 && (
              <Box sx={{ mb: 2, mt: 1 }}>
                <Typography variant="caption" color="text.secondary">Сложность пароля</Typography>
                <LinearProgress variant="determinate" value={strength} sx={{ height: 8, borderRadius: 4, backgroundColor: '#e0e0e0', '& .MuiLinearProgress-bar': { backgroundColor: strengthColor } }} />
              </Box>
            )}
            <TextField fullWidth label="Подтвердите новый пароль" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required margin="normal" />
            <Button type="submit" fullWidth variant="contained" size="large" disabled={loading} sx={{ mt: 3, py: 1.5 }}>
              {loading ? <CircularProgress size={24} /> : 'Сменить пароль'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
"""
with open('frontend/src/pages/ChangePasswordPage.tsx', 'w', encoding='utf-8') as f:
    f.write(tsx_code)
print("✅ frontend/src/pages/ChangePasswordPage.tsx обновлен")

print("\n🎉 Все файлы успешно и безопасно обновлены!")
