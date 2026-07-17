import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Card, CardContent, Typography, TextField, Button, Alert, CircularProgress } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import { authAPI } from '../services/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setEmailError(''); setPasswordError(''); setLoading(true);
    let hasError = false;
    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) { setEmailError('Введите корректный email'); hasError = true; }
    if (!password.trim()) { setPasswordError('Введите пароль'); hasError = true; }
    if (hasError) { setLoading(false); return; }

    try {
      const response = await authAPI.login(email, password);
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      if (response.data.requires_password_change) navigate('/change-password');
      else navigate('/');
    } catch (err: any) {
      if (err.response?.status === 401) setError(err.response?.data?.detail || 'Неверный email или пароль');
      else if (err.code === 'ERR_NETWORK') setError('Ошибка сети: не удается соединиться с сервером.');
      else setError('Произошла ошибка при входе.');
    } finally { setLoading(false); }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Card sx={{ width: '100%', boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <img src="/logo.png" alt="Логотип техникума" style={{ height: 80, marginBottom: 16 }} />
            <Typography variant="h5" fontWeight="bold" sx={{ lineHeight: 1.3 }}>ГБПОУ МО Люберецкий техникум<br/>имени Героя Советского Союза,<br/>лётчика-космонавта Ю. А. Гагарина</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Вход в личный кабинет</Typography>
          </Box>
          <form onSubmit={handleSubmit} noValidate>
            <TextField fullWidth label="Электронная почта" type="email" value={email} onChange={(e) => { setEmail(e.target.value); setEmailError(''); }} error={!!emailError} helperText={emailError} required margin="normal" autoFocus />
            <TextField fullWidth label="Пароль" type="password" value={password} onChange={(e) => { setPassword(e.target.value); setPasswordError(''); }} error={!!passwordError} helperText={passwordError} required margin="normal" />
            {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            <Button type="submit" fullWidth variant="contained" size="large" disabled={loading} sx={{ mt: 3, py: 1.5 }}>{loading ? <CircularProgress size={24} /> : 'Войти'}</Button>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>Забыли пароль? Обратитесь к администратору учебного заведения</Typography>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
