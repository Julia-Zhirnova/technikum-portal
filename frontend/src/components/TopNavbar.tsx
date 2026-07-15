import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Box, IconButton, Avatar, Tooltip
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import NotificationBell from './NotificationBell';
import RoleSwitcher from './RoleSwitcher';
import { authAPI } from '../services/api';

export default function TopNavbar() {
  const [user, setUser] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('TopNavbar: токен', token ? 'найден' : 'не найден');
      
      const response = await authAPI.whoami();
      console.log('TopNavbar: данные пользователя', response.data);
      setUser(response.data);
    } catch (err: any) {
      console.error('TopNavbar: ошибка загрузки пользователя:', err);
      console.error('Status:', err.response?.status);
      console.error('Data:', err.response?.data);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (!user) return null;

  // API возвращает full_name, либо собираем из отдельных полей
  const fullName = user.full_name || `${user.last_name || ''} ${user.first_name || ''}`.trim() || 'Пользователь';
  
  // Роли могут быть массивом строк ['curator', 'admin'] или массивом объектов [{name: 'curator'}]
  const roles = Array.isArray(user.roles) 
    ? user.roles.map((r: any) => typeof r === 'string' ? r : (r.name || r)).join(', ') 
    : 'Пользователь';

  return (
    <AppBar position="static" color="primary" elevation={2}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h6" component="div" fontWeight="bold" sx={{ display: { xs: 'none', sm: 'block' } }}>
            🎓 Люберецкий техникум
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
          <NotificationBell />
          <RoleSwitcher />
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main', fontSize: '0.9rem' }}>
              {user.first_name?.[0]}{user.last_name?.[0]}
            </Avatar>
            <Box sx={{ display: { xs: 'none', md: 'block' } }}>
              <Typography variant="body2" fontWeight="bold" sx={{ lineHeight: 1.2 }}>
                {fullName || 'Пользователь'}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8, lineHeight: 1 }}>
                {roles}
              </Typography>
            </Box>
          </Box>

          <Tooltip title="Выйти из системы">
            <IconButton color="inherit" onClick={handleLogout} sx={{ ml: 1 }}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
