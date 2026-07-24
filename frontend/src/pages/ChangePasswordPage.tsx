import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Typography, TextField, Button, Alert, CircularProgress, Paper, LinearProgress } from '@mui/material';
import { authAPI } from '../services/api';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Логика расчета сложности пароля (1.2.3)
  const getPasswordStrength = (pwd: string) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;
    return strength; // 0 to 4
  };

  const strength = getPasswordStrength(newPassword);
  const strengthColor = strength <= 1 ? 'error' : strength <= 2 ? 'warning' : strength <= 3 ? 'info' : 'success';
  const strengthText = ['Очень слабый', 'Слабый', 'Средний', 'Хороший', 'Отличный'][strength];

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
      // После успешной смены пароля флаг requires_password_change сброшен на бэкенде.
      // Перенаправляем на главную, где SmartRedirect пустит пользователя дальше.
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.response?.data?.new_password?.[0] || 'Ошибка при смене пароля');
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
            {/* 1.2.2: НЕТ поля "Текущий пароль" */}
            <TextField 
              fullWidth 
              label="Новый пароль" 
              type="password" 
              value={newPassword} 
              onChange={(e) => setNewPassword(e.target.value)} 
              margin="normal" 
              required 
              autoFocus
            />
            
            {/* Индикатор сложности (1.2.3) с тестовым классом */}
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
            />
            
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            
            <Button 
              type="submit" 
              fullWidth 
              variant="contained" 
              size="large" 
              disabled={loading}
              sx={{ mt: 3, py: 1.5, fontSize: '1.1rem', fontWeight: 'bold', borderRadius: 2 }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Сохранить и войти'}
            </Button>
          </form>
        </Paper>
      </Container>
    </Box>
  );
}
