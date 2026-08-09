import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { Box, Container, Typography, TextField, Button, Alert, CircularProgress, Paper, LinearProgress } from '@mui/material';
import { authAPI } from '../services/api';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // ========== БП 1.2-TC040: Синхронная проверка флага ==========
  const storedToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (storedToken) {
    try {
      const payload = JSON.parse(atob(storedToken.split('.')[1]));
      if (payload.requires_password_change !== true) {
        const roles: string[] = payload.roles || [];
        let target = '/student/profile';
        if (roles.includes('admin')) target = '/admin/users';
        else if (roles.includes('teacher') || roles.includes('curator')) target = '/teacher/statements';
        else if (roles.includes('mck_head')) target = '/mck/rpd';
        return <Navigate to={target} replace />;
      }
    } catch {
      // невалидный токен — продолжаем рендер формы
    }
  }

  // ========== Ссылка «Вернуться на главную» ==========
  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch {
      // игнорируем ошибки logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('activeRole');
      navigate('/login', { replace: true });
    }
  };

  // ========== Расчёт сложности пароля ==========
  const getPasswordStrength = (pwd: string) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;
    return strength;
  };

  const strength = getPasswordStrength(newPassword);
  const strengthColor = strength <= 1 ? 'error' : strength <= 2 ? 'warning' : strength <= 3 ? 'info' : 'success';
  const strengthText = ['Очень слабый', 'Слабый', 'Средний', 'Хороший', 'Отличный'][strength];

  // ========== Обработка отправки формы ==========
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (newPassword !== confirmPassword) {
      setError('Пароли не совпадают');
      setLoading(false);
      return;
    }

    try {
      await authAPI.forceChangePassword(newPassword, confirmPassword);
      setSuccess(true);
      setLoading(false);
      // БП 1.2-TC002: через 2 сек редирект на /login
      setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('activeRole');
        navigate('/login', { replace: true });
      }, 2000);
      return;
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const passwordErrors = err.response?.data?.new_password;
      if (Array.isArray(passwordErrors)) {
        setError(passwordErrors.join('. '));
      } else {
        setError(detail || 'Ошибка при смене пароля');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.default', p: 2 }}>
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom align="center">
            Смена пароля
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Для продолжения работы необходимо установить новый пароль.
          </Typography>

          <form onSubmit={handleSubmit}>
            <TextField 
              fullWidth 
              label="Новый пароль" 
              type="password" 
              value={newPassword} 
              onChange={(e) => setNewPassword(e.target.value)} 
              margin="normal" 
              required 
              autoFocus
              inputProps={{ 'data-testid': 'new-password-input' }}
            />
            
            {newPassword.length > 0 && (
              <Box sx={{ mb: 2, mt: 1 }} data-testid="password-strength-indicator">
                <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block' }}>
                  Сложность пароля: {strengthText}
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={(strength / 4) * 100} 
                  color={strengthColor as any} 
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  Минимум 8 символов, заглавная буква, цифра и спецсимвол.
                </Typography>
              </Box>
            )}

            <TextField 
              fullWidth 
              label="Подтвердите новый пароль" 
              type="password" 
              value={confirmPassword} 
              onChange={(e) => setConfirmPassword(e.target.value)} 
              margin="normal" 
              required 
              inputProps={{ 'data-testid': 'confirm-password-input' }}
            />

            {error && (
              <Alert severity="error" sx={{ mt: 2 }} data-testid="error-message">
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mt: 2 }} data-testid="success-message">
                Пароль успешно изменён! Перенаправление на страницу входа...
              </Alert>
            )}

            <Button 
              type="submit" 
              fullWidth 
              variant="contained" 
              size="large" 
              disabled={loading || success}
              sx={{ mt: 3, py: 1.5, fontSize: '1.1rem', fontWeight: 'bold', borderRadius: 2 }}
              data-testid="submit-button"
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : success ? 'Готово' : 'Сменить пароль'}
            </Button>

            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Button 
                variant="text" 
                color="inherit" 
                onClick={handleLogout}
                data-testid="back-to-home-link"
              >
                Вернуться на главную
              </Button>
            </Box>
          </form>
        </Paper>
      </Container>
    </Box>
  );
}
