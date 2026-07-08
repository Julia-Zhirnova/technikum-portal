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
      navigate('/profile');
    } catch (err: any) {
      setError(
        err.response?.status === 401
          ? 'Неверный email или пароль'
          : 'Ошибка соединения с сервером'
      );
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

          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              <strong>Тестовый вход:</strong><br />
              Email: <code>ivanov.ii@test.ru</code><br />
              Пароль: <code>student123</code>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}
