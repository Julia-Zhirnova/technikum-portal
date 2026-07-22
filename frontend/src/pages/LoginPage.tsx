import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Container, Grid, Typography, TextField, Button, Alert, CircularProgress, Paper } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import GroupsIcon from '@mui/icons-material/Groups';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { authAPI } from '../services/api';
const roles = [
  { label: 'Студент', desc: 'Личный кабинет, оценки, практика', icon: <PersonIcon sx={{ fontSize: 32 }} /> },
  { label: 'Преподаватель', desc: 'Журналы, ведомости, расписание', icon: <SchoolIcon sx={{ fontSize: 32 }} /> },
  { label: 'Куратор', desc: 'Управление группой, посещаемость', icon: <GroupsIcon sx={{ fontSize: 32 }} /> },
  { label: 'Администратор', desc: 'Пользователи, справочники, импорт', icon: <AdminPanelSettingsIcon sx={{ fontSize: 32 }} /> },
];

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('>>> Кнопка ВОЙТИ нажата!');
    console.log('Email:', email, 'Password:', password ? '***' : 'ПУСТО');
    e.preventDefault();
    setError(''); setLoading(true);
    
    if (!email.trim() || !password.trim()) {
      setError('Введите email и пароль'); setLoading(false); return;
    }

    try {
      console.log('>>> Отправляем запрос на /api/token/...');
      const response = await authAPI.login(email, password);
      console.log('>>> Ответ от сервера:', response.data);
      
      if (!response.data.access) {
        console.error('>>> Токен доступа отсутствует в ответе!');
        setError('Ошибка сервера: токен не получен');
        setLoading(false);
        return;
      }
      
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      console.log('>>> Токены сохранены в LocalStorage');
      
      if (response.data.requires_password_change) {
        console.log('>>> Требуется смена пароля');
        navigate('/change-password');
      } else {
        console.log('>>> Переход на главную');
        navigate('/');
      }
    } catch (err: any) {
      console.error('>>> ОШИБКА ВХОДА:', err);
      console.error('>>> Статус ответа:', err.response?.status);
      console.error('>>> Данные ошибки:', err.response?.data);
      
      if (err.response?.status === 401) {
        setError(err.response?.data?.detail || 'Неверный email или пароль');
      } else if (err.code === 'ERR_NETWORK') {
        setError('Ошибка сети: не удается соединиться с сервером. Проверьте, запущен ли Django.');
      } else {
        setError(`Ошибка: ${err.message || 'Неизвестная ошибка'}`);
      }
    } finally { 
      setLoading(false); 
    }
  };

  const currentYear = new Date().getFullYear();
  const academicYear = `${currentYear - 1}–${currentYear}`;

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex' }}>
      
      {/* ЛЕВАЯ КОЛОНКА: Бренд и информация */}
      <Box 
        sx={{ 
          width: '45%', 
          bgcolor: 'primary.main', 
          color: 'white', 
          p: { xs: 4, md: 6 }, 
          display: { xs: 'none', md: 'flex' }, 
          flexDirection: 'column', 
          justifyContent: 'space-between',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Фоновое изображение fon.png с динамической прозрачностью */}
        <Box 
          sx={{ 
            position: 'absolute', 
            top: 0, left: 0, right: 0, bottom: 0, 
            backgroundImage: 'url(/fon.png)', 
            backgroundSize: 'cover', 
            backgroundPosition: 'center',
            opacity: 'light' === 'dark-gagarin' ? 0.15 : 0.1,
            zIndex: 0
          }} 
        />
        
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
            <Box component="img" src="/logo.png" alt="Логотип" sx={{ height: 70, width: 'auto' }} />
            <Typography variant="h6" fontWeight="bold" sx={{ lineHeight: 1.2, fontSize: '1rem' }}>
              ГБПОУ МО<br/>Люберецкий техникум<br/>имени Героя Советского Союза,<br/>лётчика-космонавта Ю. А. Гагарина
            </Typography>
          </Box>
          
          <Typography variant="h2" fontWeight="900" sx={{ mb: 3, lineHeight: 1.1, fontSize: { md: '3rem', lg: '3.5rem' } }}>
            ТехноПортал
          </Typography>
          
          <Typography variant="body1" sx={{ opacity: 0.95, maxWidth: '90%', mb: 2, fontWeight: 'medium', fontSize: '1.1rem' }}>
            ТехноПортал — цифровой фундамент техникума. Мы строим его вместе с вами.
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8, maxWidth: '90%', mb: 4, fontSize: '1rem' }}>
            Учёба, документы, практика, события — всё в одной экосистеме. Доступ 24/7.<br/>
            Вход свободный. Функционал полный. Заходите. Пробуйте. Оценивайте.
          </Typography>
        </Box>

        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mb: 1, letterSpacing: '1px', fontSize: '0.8rem' }}>СИСТЕМНАЯ ИНФОРМАЦИЯ</Typography>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">Версия</Typography>
            <Typography variant="body2" fontWeight="bold">2.4.1</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="body2">Учебный год</Typography>
            <Typography variant="body2" fontWeight="bold">{academicYear}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2">Семестр</Typography>
            <Typography variant="body2" fontWeight="bold">I (осенний)</Typography>
          </Box>
        </Box>
      </Box>

      {/* ПРАВАЯ КОЛОНКА: Роли и Форма входа */}
      <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 4, bgcolor: 'background.default' }}>
        <Container maxWidth="sm">
          <Paper elevation={0} sx={{ p: 4, borderRadius: 3, bgcolor: 'background.paper' }}>
            <Typography variant="h4" fontWeight="bold" gutterBottom>Вход в систему</Typography>
            
            {/* Сетка ролей 2x2 без заголовка "Выберите роль", без hover-эффектов */}
            <Box sx={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 2 }} sx={{ mb: 4, maxWidth: '500px', mx: 'auto' }}>
              {roles.map((role) => (
                <Box key={role.label}>
                  <Box 
                    sx={{ 
                      p: 2.5, 
                      border: 1, 
                      borderColor: 'divider', 
                      borderRadius: 2, 
                      cursor: 'pointer',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      textAlign: 'center',
                      transition: 'none', // Отключаем любые анимации
                      '&:hover': { 
                        borderColor: 'divider', 
                        bgcolor: 'background.paper', 
                        transform: 'none' 
                      }
                    }}
                  >
                    <Box sx={{ color: 'primary.main', mb: 1.5 }}>{role.icon}</Box>
                    <Typography variant="subtitle1" fontWeight="bold" fontSize="0.95rem">{role.label}</Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.2 }}>{role.desc}</Typography>
                  </Box>
                </Box>
              ))}
            </Box>

            <form onSubmit={handleSubmit}>
              <TextField 
                fullWidth 
                label="Логин" 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                margin="normal" 
                required 
                autoFocus
                sx={{ mb: 2 }}
              />
              <TextField 
                fullWidth 
                label="Пароль" 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                margin="normal" 
                required
                sx={{ mb: 3 }}
              />
              
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              
              <Button 
                type="submit" 
                fullWidth 
                variant="contained" 
                size="large" 
                disabled={loading}
                sx={{ py: 1.5, fontSize: '1.1rem', fontWeight: 'bold', borderRadius: 2 }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Войти в систему'}
              </Button>
            </form>

            {/* Текст про забытый пароль */}
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 3, fontSize: '0.85rem' }}>
              Забыли пароль? Обратитесь к администратору учебного заведения
            </Typography>
          </Paper>
        </Container>
      </Box>
    </Box>
  );
}
