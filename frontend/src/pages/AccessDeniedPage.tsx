import { Container, Box, Typography, Button, Paper } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import { useNavigate } from 'react-router-dom';

export default function AccessDeniedPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <Container maxWidth="sm" sx={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center', width: '100%' }}>
        <BlockIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom fontWeight="bold" color="error">
          Нет доступа
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          У вас нет назначенных ролей в системе. Обратитесь к администратору учебного заведения для назначения роли.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button variant="outlined" onClick={() => navigate('/login')}>
            На страницу входа
          </Button>
          <Button variant="contained" color="error" onClick={handleLogout}>
            Выйти из системы
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}
