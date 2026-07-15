import { useNavigate, useLocation } from 'react-router-dom';
import { Box, List, ListItemButton, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import WorkIcon from '@mui/icons-material/Work';
import MailIcon from '@mui/icons-material/Mail';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  // Меню для студента
  const studentMenu = [
    { title: 'Главная', icon: <DashboardIcon />, path: '/student' },
    { title: 'Мой профиль', icon: <PersonIcon />, path: '/profile' },
    { title: 'Зачётная книжка', icon: <SchoolIcon />, path: '/student/grades' },
    { title: 'Практика', icon: <WorkIcon />, path: '/student/practice' },
    { title: 'Заявки', icon: <MailIcon />, path: '/student/requests' },
    { title: 'Уведомления', icon: <NotificationsIcon />, path: '/student/notifications' },
  ];

  // Меню для куратора
  const curatorMenu = [
    { title: 'Панель куратора', icon: <DashboardIcon />, path: '/curator' },
    { title: 'Заявки студентов', icon: <MailIcon />, path: '/curator/requests' },
    { title: 'Мой профиль', icon: <PersonIcon />, path: '/profile' },
  ];

  // Меню для преподавателя
  const teacherMenu = [
    { title: 'Панель преподавателя', icon: <DashboardIcon />, path: '/teacher' },
    { title: 'Практика студентов', icon: <WorkIcon />, path: '/teacher/practice' },
    { title: 'Мой профиль', icon: <PersonIcon />, path: '/profile' },
  ];

  // Определяем, какое меню показывать (по умолчанию - студенческое)
  let menu = studentMenu;
  if (location.pathname.startsWith('/curator')) {
    menu = curatorMenu;
  } else if (location.pathname.startsWith('/teacher')) {
    menu = teacherMenu;
  }

  return (
    <Box sx={{ width: 240, bgcolor: 'background.paper', borderRight: 1, borderColor: 'divider', height: '100%', overflow: 'auto' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" fontWeight="bold">
          НАВИГАЦИЯ
        </Typography>
      </Box>
      <Divider />
      <List>
        {menu.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.path}
              onClick={() => navigate(item.path)}
              selected={isActive}
              sx={{
                '&.Mui-selected': {
                  bgcolor: 'primary.light',
                  '&:hover': { bgcolor: 'primary.light' },
                },
              }}
            >
              <ListItemIcon sx={{ color: isActive ? 'primary.main' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.title} 
                sx={{ 
                  '& .MuiTypography-root': { 
                    fontWeight: isActive ? 'bold' : 'normal',
                    color: isActive ? 'primary.main' : 'inherit'
                  } 
                }} 
              />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );
}
