import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, AppBar, Toolbar, Button, IconButton, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  FormControl, InputLabel, Select, MenuItem,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SchoolIcon from '@mui/icons-material/School';
import MailIcon from '@mui/icons-material/Mail';
import { curatorAPI } from '../services/api';
import NotificationBell from '../components/NotificationBell';
import RoleSwitcher from '../components/RoleSwitcher';

export default function CuratorDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [groups, setGroups] = useState<any[]>([]);
  const [selectedGroupIndex, setSelectedGroupIndex] = useState(0);

  useEffect(() => {
    const loadGroups = async () => {
      try {
        const response = await curatorAPI.getGroup();
        console.log('Данные групп:', response.data);
        
        // API теперь возвращает массив без пагинации
        const groupsData = Array.isArray(response.data) 
          ? response.data 
          : (response.data.results || [response.data]);
        
        console.log('Обработанные группы:', groupsData);
        setGroups(groupsData);
      } catch (err: any) {
        console.error('Ошибка загрузки групп:', err);
        setError(err.response?.data?.detail || 'Ошибка загрузки данных');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadGroups();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ textAlign: 'center', mt: 10 }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <>
        <AppBar position="sticky" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              🎓 Люберецкий техникум — Куратор
            </Typography>
            <RoleSwitcher />
            <NotificationBell />
            <IconButton onClick={handleLogout} color="inherit" title="Выйти">
              <LogoutIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ mt: 5 }}>
          <Alert severity="error">{error}</Alert>
        </Container>
      </>
    );
  }

  if (groups.length === 0) {
    return (
      <>
        <AppBar position="sticky" color="default" elevation={1}>
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              🎓 Люберецкий техникум — Куратор
            </Typography>
            <RoleSwitcher />
            <NotificationBell />
            <IconButton onClick={handleLogout} color="inherit" title="Выйти">
              <LogoutIcon />
            </IconButton>
          </Toolbar>
        </AppBar>
        <Container maxWidth="md" sx={{ mt: 5 }}>
          <Alert severity="info">
            У вас нет назначенных групп. Обратитесь к администратору.
          </Alert>
        </Container>
      </>
    );
  }

  const currentGroup = groups[selectedGroupIndex];
  const totalStudents = groups.reduce((sum, g) => sum + (g.students?.length || 0), 0);

  return (
    <>
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🎓 Люберецкий техникум — Куратор
          </Typography>
          <RoleSwitcher />
          <NotificationBell />
          <IconButton onClick={handleLogout} color="inherit" title="Выйти">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ pb: 5, pt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          📊 Панель куратора
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          startIcon={<MailIcon />}
          onClick={() => navigate('/curator/requests')}
        >
          📨 Заявки студентов
        </Button>
      </Box>
        {/* Выбор группы */}
        {groups.length > 1 && (
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Выберите группу</InputLabel>
            <Select
              value={selectedGroupIndex}
              label="Выберите группу"
              onChange={(e) => setSelectedGroupIndex(Number(e.target.value))}
            >
              {groups.map((g, idx) => (
                <MenuItem key={g.id_group} value={idx}>
                  {g.id_group} ({g.students?.length || 0} студентов)
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <Typography variant="h4" gutterBottom fontWeight="bold">
          📊 Группа: {currentGroup.id_group}
          {currentGroup.curator_name && (
            <Typography variant="subtitle1" color="text.secondary" component="span">
              {' '}— куратор: {currentGroup.curator_name}
            </Typography>
          )}
        </Typography>

        {/* Карточки статистики */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <PeopleIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {currentGroup.students?.length || 0}
                </Typography>
                <Typography color="text.secondary">Студентов в группе</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SchoolIcon sx={{ fontSize: 60, color: 'success.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {totalStudents}
                </Typography>
                <Typography color="text.secondary">Всего студентов</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AssignmentIcon sx={{ fontSize: 60, color: 'warning.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {groups.length}
                </Typography>
                <Typography color="text.secondary">Групп на кураторстве</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Таблица студентов */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              👥 Студенты группы ({currentGroup.students?.length || 0})
            </Typography>
            {currentGroup.students?.length > 0 ? (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.100' }}>
                      <TableCell><strong>№</strong></TableCell>
                      <TableCell><strong>ФИО</strong></TableCell>
                      <TableCell><strong>СНИЛС</strong></TableCell>
                      <TableCell><strong>Телефон</strong></TableCell>
                      <TableCell><strong>Статус</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {currentGroup.students.map((student: any, idx: number) => (
                      <TableRow key={student.snils} hover>
                        <TableCell>{idx + 1}</TableCell>
                        <TableCell>{student.full_name}</TableCell>
                        <TableCell>{student.snils}</TableCell>
                        <TableCell>{student.phone || '—'}</TableCell>
                        <TableCell>
                          <Chip
                            label={student.status}
                            size="small"
                            color={student.status.includes('обучается') ? 'success' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info">В группе пока нет студентов</Alert>
            )}
          </CardContent>
        </Card>
      </Container>
    </>
  );
}
