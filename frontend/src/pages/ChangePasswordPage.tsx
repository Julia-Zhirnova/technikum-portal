import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Box, Card, CardContent, Typography,
  TextField, Button, Alert, CircularProgress
} from '@mui/material';
import LockResetIcon from '@mui/icons-material/LockReset';
import api from '../services/api'; // Ваш настроенный экземпляр axios

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (newPassword.length < 8) {
      setError('Пароль должен содержать минимум 8 символов.');
      setLoading(false);
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Пароли не совпадают.');
      setLoading(false);
      return;
    }

    try {
      // Точно такой же URL, который мы проверили через curl
      const response = await api.post('/auth/change-password/', {
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      console.log('✅ Пароль успешно изменен:', response.data);
      setSuccess(true);
      
      // Через 2 секунды очищаем токены и отправляем на страницу входа для чистого логина
      setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      console.error('❌ Ошибка смены пароля:', err.response?.data);
      const errData = err.response?.data;
      
      // Красивый вывод ошибок от Django DRF
      if (errData?.new_password) {
        setError(Array.isArray(errData.new_password) ? errData.new_password[0] : errData.new_password);
      } else if (errData?.confirm_password) {
        setError(errData.confirm_password);
      } else if (errData?.detail) {
        setError(errData.detail);
      } else {
        setError('Произошла ошибка при смене пароля. Попробуйте еще раз.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
        <Card sx={{ width: '100%', boxShadow: 3, textAlign: 'center', p: 4 }}>
          <LockResetIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" fontWeight="bold" color="success.main">
            Пароль успешно изменен!
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Выполняется перенаправление на страницу входа...
          </Typography>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Card sx={{ width: '100%', boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <LockResetIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
            <Typography variant="h5" fontWeight="bold">Смена пароля</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Требуется задать новый надежный пароль перед продолжением работы.
            </Typography>
          </Box>

          <form onSubmit={handleSubmit}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            
            <TextField
              fullWidth
              label="Новый пароль"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              margin="normal"
              helperText="Минимум 8 символов"
            />
            <TextField
              fullWidth
              label="Подтвердите новый пароль"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              margin="normal"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, py: 1.5 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Сменить пароль'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
