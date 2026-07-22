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

const ROLE_LABELS: Record<string, string> = {
  student: 'Студент',
  teacher: 'Преподаватель',
  curator: 'Куратор',
  admin: 'Администратор',
  mck_chairman: 'Председатель МЦК'
};

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
  
  const [activeRole, setActiveRole] = useState<string>('student');
  const [userRoles, setUserRoles] = useState<string[]>([]);
  const [userName, setUserName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const muiTheme = useMuiTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await userAPI.getProfile();
        const data = response.data;
        
        const fullName = [data.last_name, data.first_name, data.middle_name]
          .filter(Boolean)
          .join(' ');
        setUserName(fullName || data.email || 'Пользователь');
        
        if (data.roles && Array.isArray(data.roles)) {
          setUserRoles(data.roles);
          
          const storedRole = localStorage.getItem('activeRole');
          if (storedRole && data.roles.includes(storedRole)) {
            setActiveRole(storedRole);
          } else {
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

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  
  const handleRoleChange = (role: string) => {
    setActiveRole(role);
    localStorage.setItem('activeRole', role);
    
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

  const getPageTitle = () => {
    return ROUTE_TITLES[location.pathname] || 'Главная';
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
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

          {userRoles.length > 0 && (
            <FormControl size="small" sx={{ mx: 2, minWidth: 140 }}>
              <Select
                value={activeRole}
                onChange={(e) => handleRoleChange(e.target.value)}
                renderValue={(selected) => ROLE_LABELS[selected] || selected}
                sx={{ 
                  color: '#000000', 
                  fontWeight: 'bold',
                  '.MuiOutlinedInput-notchedOutline': { borderColor: '#ccc' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#999' },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#757575' }
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

          <Typography variant="body2" sx={{ mr: 2, color: '#000000', fontWeight: 'medium', display: { xs: 'none', sm: 'block' } }}>
            {userName}
          </Typography>

          <Button 
            size="small" 
            onClick={handleLogout} 
            sx={{ 
              ml: 1, 
              fontWeight: 'bold',
              backgroundColor: '#e0e0e0',
              color: '#000000',
              '&:hover': { backgroundColor: '#bdbdbd' }
            }}
          >
            ВЫХОД
          </Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: 'flex', flexGrow: 1, mt: '64px' }}>
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

        <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - 240px)` } }}>
          <Toolbar /> 
          
          <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
            {getPageTitle()}
          </Typography>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
              <Typography>Загрузка данных...</Typography>
            </Box>
          ) : (
            <Outlet context={{ activeRole, userName }} />
          )}
        </Box>
      </Box>

      <Footer />
    </Box>
  );
}
