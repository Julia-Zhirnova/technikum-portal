import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { 
  Box, AppBar, Toolbar, Typography, Button, IconButton, Drawer, Breadcrumbs, Link,
  useMediaQuery, useTheme 
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import HomeIcon from '@mui/icons-material/Home';
import { userAPI } from '../services/api';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useTheme as useAppTheme } from '../ThemeContext';

// Маппинг путей для хлебных крошек
const routeLabels: Record<string, string> = {
  '/student': 'Личный кабинет студента',
  '/student/profile': 'Мой профиль',
  '/student/grades': 'Зачётная книжка',
  '/student/practice': 'Практика',
  '/student/requests': 'Заявки',
  '/student/notifications': 'Уведомления',
  '/teacher': 'Кабинет преподавателя',
  '/teacher/statements': 'Мои ведомости',
  '/teacher/schedule': 'Расписание экзаменов',
  '/teacher/practice': 'Практика студентов',
  '/teacher/rpd': 'Рабочие программы',
  '/curator': 'Кабинет куратора',
  '/curator/group': 'Моя группа',
  '/curator/grades': 'Успеваемость',
  '/curator/attendance': 'Посещаемость',
  '/curator/schedule': 'Расписание',
  '/curator/requests': 'Заявки студентов',
  '/admin': 'Панель администратора',
  '/admin/users': 'Управление пользователями',
  '/admin/references': 'Справочники',
  '/mck': 'Кабинет председателя МЦК',
};

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [userRoles, setUserRoles] = useState<string[]>([]);
  const [activeRole, setActiveRole] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const { mode, toggleTheme } = useAppTheme();
  const muiTheme = useTheme();
  const isMobile = useMediaQuery(muiTheme.breakpoints.down('md'));

  const HEADER_HEIGHT = 64;
  const SIDEBAR_WIDTH = 240;

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await userAPI.getProfile();
        const roles = response.data.roles || [];
        setUserRoles(roles);
        setUserName(`${response.data.last_name || ''} ${response.data.first_name || ''} ${response.data.middle_name || ''}`.trim());
        
        let currentActiveRole = localStorage.getItem('activeRole');
        if (!currentActiveRole || !roles.includes(currentActiveRole)) {
          const ROLE_PRIORITY = ['admin', 'mck_chairman', 'teacher', 'curator', 'student'];
          currentActiveRole = ROLE_PRIORITY.find(r => roles.includes(r)) || roles[0];
          localStorage.setItem('activeRole', currentActiveRole);
        }
        setActiveRole(currentActiveRole);
      } catch (error) {
        localStorage.clear();
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [navigate]);

  const handleRoleSwitch = (role: string) => {
    setActiveRole(role);
    localStorage.setItem('activeRole', role);
    const lastUrl = localStorage.getItem(`last_url_${role}`);
    navigate(lastUrl || `/${role}`);
    setMobileOpen(false);
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Загрузка...</div>;

  const roleLabels: Record<string, string> = {
    admin: 'Администратор',
    mck_chairman: 'Председатель МЦК',
    teacher: 'Преподаватель',
    curator: 'Куратор',
    student: 'Студент'
  };

  const pathnames = location.pathname.split('/').filter((x) => x);
  const breadcrumbs = pathnames.map((value, index) => {
    const to = `/${pathnames.slice(0, index + 1).join('/')}`;
    const label = routeLabels[to] || value;
    const isLast = index === pathnames.length - 1;
    
    return isLast ? (
      <Typography key={to} color="text.primary" fontWeight="bold">{label}</Typography>
    ) : (
      <Link underline="hover" key={to} color="inherit" href={to} onClick={(e) => { e.preventDefault(); navigate(to); }}>
        {label}
      </Link>
    );
  });

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      
      {/* ШАПКА (Standard Fixed AppBar) */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: 'primary.main' }}>
        <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 1, sm: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <IconButton color="inherit" aria-label="open drawer" edge="start" onClick={handleDrawerToggle} sx={{ mr: 1, display: { md: 'none' } }}>
              <MenuIcon />
            </IconButton>
            <Box component="img" src="/logo.png" alt="Логотип" sx={{ height: { xs: 32, sm: 40 }, width: 'auto', display: 'block' }} />
            <Box sx={{ display: { xs: 'none', lg: 'block' } }}>
              <Typography variant="caption" sx={{ fontWeight: 'bold', lineHeight: 1.1, display: 'block', color: 'white', fontSize: '0.7rem' }}>
                ГБПОУ МО Люберецкий техникум<br/>имени Героя Советского Союза, лётчика-космонавта Ю. А. Гагарина
              </Typography>
            </Box>
          </Box>

          <Typography variant="h4" component="div" sx={{ flexGrow: 1, textAlign: { xs: 'left', md: 'center' }, fontWeight: 900, letterSpacing: '1px', textShadow: '0px 2px 4px rgba(0,0,0,0.3)', color: 'white', fontSize: { xs: '1.2rem', sm: '1.8rem', md: '2.125rem' }, ml: { xs: 1, md: 0 } }}>
            ТехноПортал
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 0.5, sm: 1.5 }, ml: 'auto' }}>
            <Typography variant="body2" sx={{ display: { xs: 'none', xl: 'block' }, fontWeight: 'medium', color: 'white', whiteSpace: 'normal', fontSize: '0.8rem', mr: 1, maxWidth: '200px', lineHeight: 1.2 }}>{userName}</Typography>
            
            {userRoles.slice(0, 2).map((role) => (
              <Button key={role} size="small" onClick={() => handleRoleSwitch(role)} sx={{ color: activeRole === role ? '#fff' : 'rgba(255,255,255,0.8)', bgcolor: activeRole === role ? 'rgba(255,255,255,0.2)' : 'transparent', border: activeRole === role ? '1px solid rgba(255,255,255,0.5)' : '1px solid transparent', textTransform: 'none', fontWeight: activeRole === role ? 'bold' : 'normal', fontSize: { xs: '0.65rem', sm: '0.75rem' }, px: { xs: 1, sm: 1.5 }, py: { xs: 0.5, sm: 0.75 }, '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                {roleLabels[role]}
              </Button>
            ))}
            
            <Button onClick={toggleTheme} size="small" sx={{ color: '#fff', ml: 0.5, border: '1px solid rgba(255,255,255,0.3)', textTransform: 'none', fontSize: '0.75rem', px: 1.5, minWidth: 'auto' }}>
              {mode === 'light-blue' ? '☀️ Светлая' : mode === 'dark-gagarin' ? '🌙 Тёмная' : ' Пастельная'}
            </Button>

            <Button size="small" onClick={() => { localStorage.clear(); navigate('/login'); }} sx={{ color: '#fff', ml: 0.5, fontWeight: 'bold', display: { xs: 'none', sm: 'block' }, fontSize: '0.75rem' }}>ВЫХОД</Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* ТЕЛО: Сайдбар + Контент (Standard Flex Layout) */}
      <Box sx={{ display: 'flex', flex: 1, mt: `${HEADER_HEIGHT}px` }}> 
        
        {/* САЙДБАР (Permanent Drawer) */}
        <Box component="nav" sx={{ width: { md: SIDEBAR_WIDTH }, flexShrink: { md: 0 } }}>
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: SIDEBAR_WIDTH } }}
          >
            <Sidebar role={activeRole} onClose={handleDrawerToggle} />
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { boxSizing: 'border-box', width: SIDEBAR_WIDTH } }}
            open
          >
            <Sidebar role={activeRole} />
          </Drawer>
        </Box>

        {/* ОСНОВНОЙ КОНТЕНТ + ПОДВАЛ */}
        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 3 }, width: { md: `calc(100% - ${SIDEBAR_WIDTH}px)` }, display: 'flex', flexDirection: 'column' }}>
          
          {/* Хлебные крошки */}
          <Breadcrumbs separator="›" aria-label="breadcrumb" sx={{ mb: 3 }}>
            <Link underline="hover" color="inherit" href="/" onClick={(e) => { e.preventDefault(); navigate('/'); }}>
              <HomeIcon sx={{ fontSize: 20, verticalAlign: 'middle', mr: 0.5 }} /> Главная
            </Link>
            {breadcrumbs}
          </Breadcrumbs>

          {/* Контент страниц */}
          <Box sx={{ flex: 1, '& .MuiPaper-root, & .MuiCard-root, & .MuiTableContainer-root': { bgcolor: 'background.paper', color: 'text.primary', borderColor: 'divider' } }}>
            <Outlet />
          </Box>
          
          {/* Подвал внутри контента (не фиксированный) */}
          <Footer />
        </Box>
      </Box>
    </Box>
  );
}
