import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Box, IconButton, Avatar, Tooltip, Badge } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import NotificationsIcon from '@mui/icons-material/Notifications';
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
      const response = await authAPI.whoami();
      setUser(response.data);
    } catch (err: any) {
      console.error('TopNavbar: ошибка загрузки пользователя:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('activeRole');
    navigate('/login');
  };

  if (!user) return null;

  const fullName = user.full_name || `${user.last_name || ''} ${user.first_name || ''} ${user.middle_name || ''}`.trim() || 'Пользователь';
  const roles = Array.isArray(user.roles) ? user.roles : [];
  const activeRole = localStorage.getItem('activeRole') || roles[0] || 'student';

  return (
    <AppBar position="static" color="primary" elevation={2} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 1, sm: 3 } }}>
        
        {/* 1.3.1 и 1.3.2: Логотип и "ТехноПортал" слева/по центру */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box component="img" src="/logo.png" alt="Логотип" sx={{ height: 40, width: 'auto', display: { xs: 'none', sm: 'block' } }} />
          <Typography variant="h6" component="div" fontWeight="bold" sx={{ display: { xs: 'none', md: 'block' } }}>
            ТехноПортал
          </Typography>
        </Box>

        {/* Правая часть: Уведомления, Переключатель ролей, ФИО, Выход */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
          
          {/* 1.3.6: Колокольчик уведомлений */}
          <Tooltip title="Уведомления">
            <IconButton color="inherit">
              <Badge badgeContent={0} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* 1.3.8: Переключатель ролей (используем наш кастомный компонент) */}
          {roles.length > 1 && <RoleSwitcher roles={roles} currentRole={activeRole} />}
          
          {/* 1.3.3 и 1.3.4: ФИО полностью и активная роль (без обрезки) */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 1, flexShrink: 0 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main', fontSize: '0.9rem' }}>
              {user.first_name?.[0]}{user.last_name?.[0]}
            </Avatar>
            <Box sx={{ display: { xs: 'none', md: 'block' }, textAlign: 'right' }}>
              <Typography variant="body2" fontWeight="bold" sx={{ lineHeight: 1.2, whiteSpace: 'nowrap' }}>
                {fullName}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8, lineHeight: 1, textTransform: 'capitalize' }}>
                {activeRole === 'mck_chairman' ? 'МЦК' : activeRole}
              </Typography>
            </Box>
          </Box>

          {/* 1.3.10: Выход */}
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
