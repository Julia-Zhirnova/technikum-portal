import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Box, Card, CardContent, Typography,
  TextField, Button, Alert, CircularProgress,
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import { authAPI } from '../services/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(email, password);
      
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      // ГЛАВНОЕ ИСПРАВЛЕНИЕ: Проверяем флаг сразу после логина
      if (response.data.requires_password_change) {
        navigate('/change-password');
      } else {
        navigate('/');
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        // ЧИТАЕМ СООБЩЕНИЕ С БЭКЕНДА (там будет "Ваша учетная запись заблокирована...")
        const backendMessage = err.response?.data?.detail;
        setError(backendMessage || 'Неверный email или пароль');
      } else if (err.code === 'ERR_NETWORK') {
        setError('Ошибка сети: не удается соединиться с сервером.');
      } else {
        setError('Произошла ошибка при входе.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
      <Card sx={{ width: '100%', boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <SchoolIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
            <Typography variant="h5" fontWeight="bold">
              Люберецкий техникум
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Вход в личный кабинет
            </Typography>
          </Box>

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              margin="normal"
              autoFocus
            />
            <TextField
              fullWidth
              label="Пароль"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              margin="normal"
            />

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, py: 1.5 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Войти'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}

