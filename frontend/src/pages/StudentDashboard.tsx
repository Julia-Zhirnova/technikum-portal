import { useNavigate } from 'react-router-dom';
import { Box, Typography, Grid, Card, CardContent, CardActionArea, Avatar } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import WorkIcon from '@mui/icons-material/Work';
import MailIcon from '@mui/icons-material/Mail';
import NotificationsIcon from '@mui/icons-material/Notifications';

export default function StudentDashboard() {
  const navigate = useNavigate();

  const menuItems = [
    { 
      title: 'Мой профиль', 
      desc: 'Персональные данные, семья, здоровье', 
      icon: <PersonIcon sx={{ fontSize: 40, color: '#1976d2' }} />, 
      path: '/profile' 
    },
    { 
      title: 'Зачётная книжка', 
      desc: 'Оценки, ведомости и средний балл', 
      icon: <SchoolIcon sx={{ fontSize: 40, color: '#2e7d32' }} />, 
      path: '/student/grades' 
    },
    { 
      title: 'Практика', 
      desc: 'Место прохождения, дневник и отчеты', 
      icon: <WorkIcon sx={{ fontSize: 40, color: '#ed6c02' }} />, 
      path: '/student/practice' 
    },
    { 
      title: 'Заявки', 
      desc: 'Заказ справок и документов', 
      icon: <MailIcon sx={{ fontSize: 40, color: '#9c27b0' }} />, 
      path: '/student/requests' 
    },
    { 
      title: 'Уведомления', 
      desc: 'Оповещения от администрации и куратора', 
      icon: <NotificationsIcon sx={{ fontSize: 40, color: '#d32f2f' }} />, 
      path: '/student/notifications' 
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom sx={{ mb: 4 }}>
        👋 Добро пожаловать в личный кабинет студента
      </Typography>
      
      <Grid container spacing={3}>
        {menuItems.map((item, index) => (
          <Grid size={{ xs: 12 }} sm={6} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%', 
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': { transform: 'translateY(-4px)', boxShadow: 6 }
              }}
            >
              <CardActionArea onClick={() => navigate(item.path)} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Avatar sx={{ bgcolor: 'transparent', mb: 2 }}>
                  {item.icon}
                </Avatar>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  {item.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.desc}
                </Typography>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
