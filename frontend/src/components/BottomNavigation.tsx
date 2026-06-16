import { useNavigate, useLocation } from 'react-router-dom';
import MuiBottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import HomeIcon from '@mui/icons-material/Home';
import DescriptionIcon from '@mui/icons-material/Description';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import Paper from '@mui/material/Paper';

export default function BottomNavigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const getCurrentValue = () => {
    switch (location.pathname) {
      case '/': return 0;
      case '/documents': return 1;
      case '/requests': return 2;
      case '/profile': return 3;
      default: return 0;
    }
  };

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }} elevation={3}>
      <MuiBottomNavigation
        showLabels
        value={getCurrentValue()}
        onChange={(event, newValue) => {
          const routes = ['/', '/documents', '/requests', '/profile'];
          navigate(routes[newValue]);
        }}
      >
        <BottomNavigationAction label="Главная" icon={<HomeIcon />} />
        <BottomNavigationAction label="Документы" icon={<DescriptionIcon />} />
        <BottomNavigationAction label="Заявки" icon={<SendIcon />} />
        <BottomNavigationAction label="Профиль" icon={<PersonIcon />} />
      </MuiBottomNavigation>
    </Paper>
  );
}
