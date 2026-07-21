import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { 
  AppBar, Toolbar, Typography, Button, Box, IconButton, Drawer,
  useMediaQuery, useTheme as useMuiTheme, MenuItem, Select, FormControl
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { userAPI } from '../services/api';
import { useTheme as useAppTheme } from '../ThemeContext';

// Маппинг названий ролей
const ROLE_LABELS: Record<string, string> = {
  student: 'Студент',
  teacher: 'Преподаватель',
  curator: 'Куратор',
  admin: 'Администратор',
  mck_chairman: 'Председатель МЦК'
};

// Названия страниц для заголовка
const ROUTE_TITLES: Record<string, string> = {
  '/student/profile': 'Мой профиль',
  '/student/grades': 'Зачётная книжка',
  '/student/practice': 'Практика',
  '/student/requests': 'Заявки',
  '/student/notifications': 'Уведомления',
  '/teacher/statements': 'Мои ведомости',
  '/teacher/schedule': 'Расписание экзаменов',
  '/teacher/practice': 'Практика студентов',
  '/teacher/rpd': 'Рабочие программы',
  '/curator/group': 'Моя группа',
  '/curator/grades': 'Успеваемость',
  '/curator/attendance': 'Посещаемость',
  '/curator/schedule': 'Расписание',
  '/curator/requests': 'Заявки студентов',
  '/admin/users': 'Управление пользователями',
  '/admin/references': 'Справочники',
  '/mck/rpd': 'Рабочие программы (РПД)',
  '/mck/monitoring': 'Мониторинг РПД',
  '/mck/protocols': 'Протоколы МЦК'
};

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Состояния
  const [activeRole, setActiveRole] = useState<string>('student');
  const [userRoles, setUserRoles] = useState<string[]>([]); // <-- НОВЫЙ STATE ДЛЯ РЕАЛЬНЫХ РОЛЕЙ
  const [userName, setUserName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  
  // Хуки темы
  const { mode, toggleTheme } = useAppTheme();
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  // 1. Загрузка данных профиля при монтировании
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await userAPI.getProfile();
        const data = response.data;
        
        // Формируем ФИО
        const fullName = [data.last_name, data.first_name, data.middle_name]
          .filter(Boolean)
          .join(' ');
        setUserName(fullName || data.email || 'Пользователь');
        
        // Сохраняем ВСЕ роли пользователя из ответа API
        if (data.roles && Array.isArray(data.roles)) {
          setUserRoles(data.roles);
          
          // Определяем активную роль
          const storedRole = localStorage.getItem('activeRole');
          // Если сохраненная роль есть в списке реальных ролей - используем её
          if (storedRole && data.roles.includes(storedRole)) {
            setActiveRole(storedRole);
          } else {
            // Иначе берем первую роль из списка или дефолтную
            const firstRole = data.roles[0] || 'student';
            setActiveRole(firstRole);
            localStorage.setItem('activeRole', firstRole);
          }
        }
      } catch (error) {
        console.error('Не удалось загрузить профиль:', error);
        setUserName('Пользователь');
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserProfile();
  }, []);

  // Обработчики UI
  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  
  const handleRoleChange = (role: string) => {
    setActiveRole(role);
    localStorage.setItem('activeRole', role);
    
    // Перенаправляем на главную страницу выбранной роли
    const roleRoutes: Record<string, string> = {
      student: '/student/profile',
      teacher: '/teacher/statements',
      curator: '/curator/group',
      admin: '/admin/users',
      mck_chairman: '/mck/rpd'
    };
    navigate(roleRoutes[role] || '/student/profile');
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  // Определение заголовка текущей страницы
  const getPageTitle = () => {
    return ROUTE_TITLES[location.pathname] || 'Главная';
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Верхняя шапка */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          {/* Логотип и название */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1 }}>
            <img 
              src="/logo.png" 
              alt="Логотип" 
              style={{ height: '40px', width: 'auto' }} 
            />
            <Typography variant="h6" noWrap component="div">
              ТехноПортал
            </Typography>
          </Box>

          {/* Переключатель ролей (ТОЛЬКО РЕАЛЬНЫЕ РОЛИ ПОЛЬЗОВАТЕЛЯ) */}
          {userRoles.length > 0 && (
            <FormControl size="small" sx={{ mx: 2, minWidth: 140, '& .MuiInputBase-root': { color: '#fff' } }}>
              <Select
                value={activeRole}
                onChange={(e) => handleRoleChange(e.target.value)}
                renderValue={(selected) => ROLE_LABELS[selected] || selected}
                sx={{ 
                  color: '#fff', 
                  '.MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.3)' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.5)' }
                }}
              >
                {userRoles.map((role) => (
                  <MenuItem key={role} value={role}>
                    {ROLE_LABELS[role] || role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          {/* Отображение ФИО пользователя */}
          <Typography variant="body2" sx={{ mr: 2, opacity: 0.9, display: { xs: 'none', sm: 'block' } }}>
            {userName}
          </Typography>

          {/* Кнопка смены темы */}
          <Button 
            size="small" 
            onClick={toggleTheme} 
            sx={{ color: '#fff', ml: 1, border: '1px solid rgba(255,255,255,0.3)', textTransform: 'none' }}
          >
            {mode === 'dark-gagarin' ? '☀️ Светлая' : '🌙 Тёмная'}
          </Button>

          {/* Кнопка выхода */}
          <Button 
            size="small" 
            onClick={handleLogout} 
            sx={{ color: '#fff', ml: 1, fontWeight: 'bold' }}
          >
            ВЫХОД
          </Button>
        </Toolbar>
      </AppBar>

      {/* Основной контент с сайдбаром */}
      <Box sx={{ display: 'flex', flexGrow: 1, mt: '64px' }}>
        {/* Сайдбар для десктопа */}
        <Drawer
          variant="permanent"
          sx={{
            width: 240,
            flexShrink: 0,
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Sidebar role={activeRole} />
        </Drawer>

        {/* Сайдбар для мобильных */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' },
          }}
        >
          <Toolbar />
          <Sidebar role={activeRole} onClose={handleDrawerToggle} />
        </Drawer>

        {/* Основная область контента */}
        <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - 240px)` } }}>
          <Toolbar /> {/* Отступ под шапку */}
          
          {/* Заголовок страницы */}
          <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
            {getPageTitle()}
          </Typography>

          {/* Рендеринг дочерних маршрутов */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
              <Typography>Загрузка данных...</Typography>
            </Box>
          ) : (
            <Outlet context={{ activeRole, userName }} />
          )}
        </Box>
      </Box>

      {/* Подвал */}
      <Footer />
    </Box>
  );
}
