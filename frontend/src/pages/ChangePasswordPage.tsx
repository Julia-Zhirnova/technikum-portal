import { useState } from 'react';
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
      await api.post('/auth/force-change-password/', {
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      setSuccess(true);
      setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        navigate('/'); // SmartRedirect перенаправит на нужный дашборд
      }, 2000);
    } catch (err: any) {
      const d = err.response?.data;
      if (d?.new_password) {
        setError(Array.isArray(d.new_password) ? d.new_password[0] : d.new_password);
      } else if (d?.confirm_password) {
        setError(d.confirm_password);
      } else if (d?.detail) {
        setError(d.detail);
      } else {
        setError('Произошла ошибка при смене пароля.');
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
          <Typography variant="h5" fontWeight="bold" color="success.main">Пароль успешно изменен!</Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>Выполняется перенаправление...</Typography>
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
              fullWidth label="Новый пароль" type="password" value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)} required margin="normal"
            />
            {newPassword.length > 0 && (
              <Box sx={{ mb: 2, mt: 1 }}>
                <Typography variant="caption" color="text.secondary">Сложность пароля</Typography>
                <LinearProgress variant="determinate" value={strength} sx={{ height: 8, borderRadius: 4, backgroundColor: '#e0e0e0', '& .MuiLinearProgress-bar': { backgroundColor: strengthColor } }} />
              </Box>
            )}

            <TextField
              fullWidth label="Подтвердите новый пароль" type="password" value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)} required margin="normal"
            />

            <Button type="submit" fullWidth variant="contained" size="large" disabled={loading} sx={{ mt: 3, py: 1.5 }}>
              {loading ? <CircularProgress size={24} /> : 'Сменить пароль'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
