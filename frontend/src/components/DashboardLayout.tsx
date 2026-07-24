import React, { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Drawer } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Sidebar from './Sidebar';
import Footer from './Footer';
import RoleSwitcher from './RoleSwitcher';
import { userAPI } from '../services/api';

const ROLE_LABELS: Record<string, string> = {
  student: 'Студент',
  teacher: 'Преподаватель',
  curator: 'Куратор',
  admin: 'Администратор',
  mck_chairman: 'МЦК'
};

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [activeRole, setActiveRole] = useState<string>('student');
  const [userRoles, setUserRoles] = useState<string[]>([]);
  const [userName, setUserName] = useState<string>('');
  const [mobileOpen, setMobileOpen] = useState(false);

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
          
          let validRole = storedRole && data.roles.includes(storedRole) ? storedRole : (data.roles[0] || 'student');
          setActiveRole(validRole);
          localStorage.setItem('activeRole', validRole);
        }
      } catch (error) {
        console.error('Не удалось загрузить профиль:', error);
      }
    };
    fetchUserProfile();
  }, [navigate]);

  useEffect(() => {
    if (userRoles.length > 0 && activeRole) {
      const path = location.pathname;
      let targetPath = '';
      
      if (activeRole === 'student' && (path.startsWith('/teacher/') || path.startsWith('/admin/') || path.startsWith('/curator/'))) {
        targetPath = '/student/profile';
      } else if (activeRole === 'teacher' && (path.startsWith('/admin/') || path.startsWith('/curator/'))) {
        targetPath = '/teacher/statements';
      } else if (activeRole === 'curator' && path.startsWith('/admin/')) {
        targetPath = '/curator/group';
      }

      if (targetPath && path !== targetPath) {
        navigate(targetPath, { replace: true });
      }
    }
  }, [activeRole, userRoles, location.pathname, navigate]);

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  
  const handleRoleChange = (role: string) => {
    setActiveRole(role);
    localStorage.setItem('activeRole', role);
    const roleRoutes: Record<string, string> = {
      student: '/student/profile', teacher: '/teacher/statements',
      curator: '/curator/group', admin: '/admin/users', mck_chairman: '/mck/rpd'
    };
    navigate(roleRoutes[role] || '/student/profile');
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 1, sm: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ display: { xs: 'block', md: 'none' }, mr: 1 }}
              data-testid="burger-menu-button"
            >
              <MenuIcon data-testid="MenuIcon" />
            </IconButton>

            <Box component="img" src="/logo.png" alt="Логотип" sx={{ height: 45, width: 'auto', display: { xs: 'none', sm: 'block' } }} />
            <Typography variant="body2" fontWeight="bold" sx={{ display: { xs: 'none', lg: 'block' }, lineHeight: 1.2, fontSize: '0.8rem' }}>
              ГБПОУ МО<br/>Люберецкий техникум<br/>имени Героя Советского Союза,<br/>лётчика-космонавта Ю. А. Гагарина
            </Typography>
            <Typography variant="h6" fontWeight="900" sx={{ flexGrow: 1, textAlign: 'center', display: { xs: 'none', md: 'block' } }}>
              ТехноПортал
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 2 } }}>
            {/* Показываем роль, если она одна, иначе показываем переключатель */}
            {userRoles.length > 1 ? (
              <RoleSwitcher roles={userRoles} currentRole={activeRole} onRoleChange={handleRoleChange} />
            ) : (
              <Typography variant="body2" fontWeight="bold" sx={{ whiteSpace: 'nowrap', textTransform: 'capitalize', mr: 1 }}>
                {ROLE_LABELS[activeRole] || activeRole}
              </Typography>
            )}
            
            <Typography variant="body2" fontWeight="bold" sx={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flexShrink: 0, display: { xs: 'none', sm: 'block' } }}>
              {userName}
            </Typography>

            <Button size="small" onClick={handleLogout} title="Выйти из системы" sx={{ fontWeight: 'bold', color: '#fff', border: '1px solid rgba(255,255,255,0.5)' }}>
              ВЫХОД
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: 'flex', flexGrow: 1, mt: '64px' }}>
        <Drawer
          variant="permanent"
          sx={{
            width: 240,
            flexShrink: 0,
            display: { xs: 'none', md: 'block' },
            zIndex: (theme) => theme.zIndex.drawer - 1,
            '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box', borderRight: '1px solid rgba(0,0,0,0.12)' },
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
          <Toolbar>
            <IconButton onClick={handleDrawerToggle}>
              <MenuIcon />
            </IconButton>
          </Toolbar>
          <Sidebar role={activeRole} onClose={handleDrawerToggle} />
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - 240px)` }, bgcolor: 'background.default', display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 64px)' }}>
          <Outlet context={{ activeRole, userName }} />
        </Box>
      </Box>
      <Footer />
    </Box>
  );
}
