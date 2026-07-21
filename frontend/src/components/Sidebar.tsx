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
import AnalyticsIcon from '@mui/icons-material/Analytics';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import ReceiptIcon from '@mui/icons-material/Receipt';

interface MenuItem {
  text: string;
  path: string;
  icon: React.ReactNode;
  external?: boolean;
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

const adminMenu: MenuItem[] = [
  { text: 'Управление пользователями', path: '/admin/users', icon: <GroupsIcon /> },
  { text: 'Справочники', path: '/admin/references', icon: <MenuBookIcon /> },
  { text: 'Приказы', path: '/admin/orders', icon: <ReceiptIcon /> },
  { text: 'Аналитика', path: '/admin/analytics', icon: <AnalyticsIcon /> },
  { text: 'Импорт/Экспорт', path: '/admin/import-export', icon: <UploadFileIcon /> },
  { text: 'Django Admin', path: '/admin/', icon: <AdminPanelSettingsIcon />, external: true },
];

const mckMenu: MenuItem[] = [
  { text: 'Рабочие программы (РПД)', path: '/mck/rpd', icon: <MenuBookIcon /> },
  { text: 'Мониторинг РПД', path: '/mck/monitoring', icon: <AnalyticsIcon /> },
  { text: 'Протоколы МЦК', path: '/mck/protocols', icon: <DescriptionIcon /> },
];

export default function Sidebar({ role, onClose }: SidebarProps) {
  const location = useLocation();

  const getMenuByRole = (): MenuItem[] => {
    switch (role) {
      case 'student': return studentMenu;
      case 'teacher': return teacherMenu;
      case 'curator': return curatorMenu;
      case 'admin': return adminMenu;
      case 'mck_chairman': return mckMenu;
      default: return [];
    }
  };

  const menuItems = getMenuByRole();

  return (
    <Box sx={{ width: 240, height: '100%', overflowY: 'auto', overflowX: 'hidden', pt: 4, px: 2, bgcolor: 'background.paper' }}>
      <List sx={{ px: 0 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          
          // Формируем пропы для ListItem в зависимости от типа ссылки
          const listItemProps = item.external 
            ? { component: 'a', href: item.path, target: '_blank', rel: 'noopener noreferrer' }
            : { component: Link, to: item.path };

          return (
            <ListItem
              {...listItemProps}
              onClick={onClose}
              key={item.path}
              sx={{
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',     
                py: 2.5,
                mb: 1,
                borderRadius: 3,
                bgcolor: isActive ? 'primary.main' : 'transparent',
                color: isActive ? 'primary.contrastText' : 'text.primary',
                '&:hover': {
                  bgcolor: isActive ? 'primary.dark' : 'action.hover',
                },
                transition: 'all 0.2s',
                cursor: 'pointer',
              }}
            >
              <Box sx={{ mb: 1, color: isActive ? 'inherit' : 'primary.main', transform: isActive ? 'scale(1.1)' : 'scale(1)', transition: 'transform 0.2s' }}>
                {item.icon}
              </Box>
              <ListItemText 
                primary={item.text}
                sx={{ 
                  m: 0, 
                  '& .MuiTypography-root': { 
                    textAlign: 'center',
                    fontSize: '0.75rem',
                    lineHeight: 1.2,
                    fontWeight: isActive ? 'bold' : 'medium',
                    display: 'block'
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
