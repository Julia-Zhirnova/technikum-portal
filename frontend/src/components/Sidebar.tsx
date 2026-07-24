import { List, ListItem, ListItemText, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import NotificationsIcon from '@mui/icons-material/Notifications';
import GroupsIcon from '@mui/icons-material/Groups';
import AssignmentIcon from '@mui/icons-material/Assignment';
import VisibilityIcon from '@mui/icons-material/Visibility';
import MenuBookIcon from '@mui/icons-material/MenuBook';

interface MenuItem {
  text: string;
  path: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  role: string;
  onClose?: () => void;
}

const studentMenu: MenuItem[] = [
  { text: 'Мой профиль', path: '/student/profile', icon: <PersonIcon /> },
  { text: 'Зачётная книжка', path: '/student/grades', icon: <SchoolIcon /> },
  { text: 'Практика', path: '/student/practice', icon: <WorkIcon /> },
  { text: 'Заявки', path: '/student/requests', icon: <DescriptionIcon /> },
  { text: 'Уведомления', path: '/student/notifications', icon: <NotificationsIcon /> },
];

const teacherMenu: MenuItem[] = [
  { text: 'Мои ведомости', path: '/teacher/statements', icon: <AssignmentIcon /> },
  { text: 'Расписание экзаменов', path: '/teacher/schedule', icon: <CalendarTodayIcon /> },
  { text: 'Практика', path: '/teacher/practice', icon: <WorkIcon /> },
  { text: 'Рабочие программы', path: '/teacher/rpd', icon: <MenuBookIcon /> },
];

const curatorMenu: MenuItem[] = [
  { text: 'Моя группа', path: '/curator/group', icon: <GroupsIcon /> },
  { text: 'Успеваемость', path: '/curator/grades', icon: <SchoolIcon /> },
  { text: 'Посещаемость', path: '/curator/attendance', icon: <VisibilityIcon /> },
  { text: 'Расписание', path: '/curator/schedule', icon: <CalendarTodayIcon /> },
  { text: 'Заявки студентов', path: '/curator/requests', icon: <DescriptionIcon /> },
  { text: 'Практика', path: '/curator/practice', icon: <WorkIcon /> },
];

export default function Sidebar({ role, onClose }: SidebarProps) {
  const location = useLocation();

  const getMenuByRole = (): MenuItem[] => {
    switch (role) {
      case 'student': return studentMenu;
      case 'teacher': return teacherMenu;
      case 'curator': return curatorMenu;
      default: return [];
    }
  };

  const menuItems = getMenuByRole();

  return (
    <Box 
      data-testid="sidebar-content"
      // 1.4.10: overflowX: 'hidden', 1.4.12: pt: 6 (достаточный отступ сверху, чтобы первый элемент был виден)
      sx={{ 
        width: 240, 
        height: '100%', 
        overflowY: 'auto', 
        overflowX: 'hidden', 
        pt: 6, 
        pb: 4, 
        px: 1, 
        bgcolor: 'background.paper' 
      }}
    >
      <List sx={{ px: 0 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          
          return (
            <ListItem
              component={Link}
              to={item.path}
              onClick={onClose}
              key={item.path}
              data-testid={isActive ? 'active-menu-item' : 'menu-item'}
              sx={{
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                py: 2,
                mb: 1,
                borderRadius: 2,
                bgcolor: isActive ? 'primary.main' : 'transparent',
                color: isActive ? 'primary.contrastText' : 'text.primary',
                '&:hover': {
                  bgcolor: isActive ? 'primary.dark' : 'action.hover',
                },
                transition: 'all 0.2s',
              }}
            >
              <Box sx={{ mb: 0.5, color: isActive ? 'inherit' : 'primary.main' }}>
                {item.icon}
              </Box>
              <ListItemText 
                primary={item.text}
                sx={{ 
                  m: 0, 
                  '& .MuiTypography-root': { 
                    fontSize: '0.75rem',
                    fontWeight: isActive ? 'bold' : 'medium'
                  } 
                }}
              />
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
}
