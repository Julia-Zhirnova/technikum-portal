import React from 'react';
import { Box, Container, Grid, Paper, Typography, Button } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import GroupsIcon from '@mui/icons-material/Groups';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const roles = [
  { id: 'student', title: 'Студент', desc: 'Личный кабинет', icon: <PersonIcon /> },
  { id: 'teacher', title: 'Преподаватель', desc: 'Журналы и ведомости', icon: <SchoolIcon /> },
  { id: 'curator', title: 'Куратор', desc: 'Управление группой', icon: <GroupsIcon /> },
  { id: 'admin', title: 'Администратор', desc: 'Полный доступ', icon: <AdminPanelSettingsIcon /> },
];

export default function Login() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', overflowY: 'auto' }}>
      <Box sx={{ 
        width: { xs: '100%', md: '45%' }, 
        position: 'relative', 
        bgcolor: 'primary.main',
        color: 'white',
        p: 4,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <Box sx={{ 
          position: 'absolute', inset: 0, 
          backgroundImage: 'url(/login-bg.jpg)', 
          backgroundSize: 'cover', 
          backgroundPosition: 'center',
          '&::after': {
            content: '""', position: 'absolute', inset: 0,
            bgcolor: 'primary.main', opacity: 0.1, zIndex: 1
          }
        }} />
        
        <Box sx={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
          <Typography variant="h2" fontWeight="900" sx={{ fontSize: { xs: '2rem', md: '3.5rem' }, mb: 2 }}>
            ТехноПортал
          </Typography>
          <Typography variant="h5" sx={{ fontSize: { xs: '1rem', md: '1.5rem' }, maxWidth: '80%', mx: 'auto' }}>
            Единое цифровое пространство техникума
          </Typography>
        </Box>
      </Box>

      <Container maxWidth="md" sx={{ py: 6, flex: 1 }}>
        <Typography variant="h4" align="center" gutterBottom>Выберите вашу роль</Typography>
        
        <Grid container spacing={3}>
          {roles.map((role) => (
            <Grid item xs={12} sm={6} key={role.id}>
              <Paper elevation={3} sx={{ 
                p: 3, height: '100%', display: 'flex', flexDirection: 'column', 
                alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
                transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' }
              }}>
                {React.cloneElement(role.icon as React.ReactElement, { sx: { fontSize: 48, mb: 2 } })}
                <Typography variant="h6" fontWeight="bold">{role.title}</Typography>
                <Typography variant="body2" color="text.secondary" align="center">
                  {role.desc}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Button variant="contained" fullWidth size="large" sx={{ mt: 4 }}>
          Войти в систему
        </Button>
      </Container>
    </Box>
  );
}
