import React, { useState } from 'react';
import { Box, Container, Grid, Paper, Typography, TextField, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import GroupsIcon from '@mui/icons-material/Groups';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { authAPI } from '../services/api';

const roles = [
  { id: 'student', title: 'Студент', desc: 'Личный кабинет', icon: <PersonIcon sx={{ fontSize: 40 }} /> },
  { id: 'teacher', title: 'Преподаватель', desc: 'Журналы и ведомости', icon: <SchoolIcon sx={{ fontSize: 40 }} /> },
  { id: 'curator', title: 'Куратор', desc: 'Управление группой', icon: <GroupsIcon sx={{ fontSize: 40 }} /> },
  { id: 'admin', title: 'Администратор', desc: 'Полный доступ', icon: <AdminPanelSettingsIcon sx={{ fontSize: 40 }} /> },
];

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await authAPI.login(email, password);
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      if (res.data.requires_password_change) navigate('/change-password');
      else navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', overflowY: 'auto' }}>
      <Box sx={{ 
        width: { xs: '100%', md: '45%' }, 
        bgcolor: 'primary.main', 
        color: 'white', 
        p: 4, 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center', 
        position: 'relative' 
      }}>
        <Box sx={{ 
          position: 'absolute', inset: 0, 
          backgroundImage: 'url(/fon.png)', 
          backgroundSize: 'cover', 
          opacity: 0.9 
        }} />
        <Box sx={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <Typography variant="h2" fontWeight="900" sx={{ fontSize: { xs: '2rem', md: '3.5rem' }, mb: 2 }}>ТехноПортал</Typography>
          <Typography variant="h5">Единое цифровое пространство техникума</Typography>
        </Box>
      </Box>
      
      <Container maxWidth="md" sx={{ py: 6, flex: 1 }}>
        <Typography variant="h4" align="center" gutterBottom>Выберите вашу роль</Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {roles.map((role) => (
            <Grid item xs={12} sm={6} key={role.id}>
              <Paper elevation={3} sx={{ 
                p: 3, height: '100%', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', justifyContent: 'center', cursor: 'pointer', 
                '&:hover': { transform: 'translateY(-4px)' }, transition: '0.2s' 
              }}>
                {React.cloneElement(role.icon, { sx: { fontSize: 48, mb: 2, color: 'primary.main' } })}
                <Typography variant="h6" fontWeight="bold">{role.title}</Typography>
                <Typography variant="body2" color="text.secondary" align="center">{role.desc}</Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <form onSubmit={handleSubmit}>
          <TextField fullWidth label="Email" value={email} onChange={e => setEmail(e.target.value)} margin="normal" required />
          <TextField fullWidth label="Пароль" type="password" value={password} onChange={e => setPassword(e.target.value)} margin="normal" required />
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          <Button type="submit" variant="contained" fullWidth size="large" disabled={loading} sx={{ mt: 3 }}>
            {loading ? 'Вход...' : 'Войти в систему'}
          </Button>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 2 }}>
            Забыли пароль? Обратитесь к администратору
          </Typography>
        </form>
      </Container>
    </Box>
  );
}