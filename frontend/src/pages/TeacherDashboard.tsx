import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, AppBar, Toolbar, IconButton, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import SchoolIcon from '@mui/icons-material/School';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { teacherAPI } from '../services/api';
import NotificationBell from '../components/NotificationBell';
import RoleSwitcher from '../components/RoleSwitcher';

export default function TeacherDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statements, setStatements] = useState<any[]>([]);

  useEffect(() => {
    const loadStatements = async () => {
      try {
        const response = await teacherAPI.getStatements();
        const data = Array.isArray(response.data) ? response.data : (response.data.results || []);
        setStatements(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки данных');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadStatements();
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
              🎓 Люберецкий техникум — Преподаватель
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

  return (
    <>
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🎓 Люберецкий техникум — Преподаватель
          </Typography>
          <RoleSwitcher />
          <NotificationBell />
          <IconButton onClick={handleLogout} color="inherit" title="Выйти">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ pb: 5, pt: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          📖 Мои ведомости
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AssignmentIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {statements.length}
                </Typography>
                <Typography color="text.secondary">Всего ведомостей</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SchoolIcon sx={{ fontSize: 60, color: 'success.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {statements.filter(s => s.status === 'в_работе').length}
                </Typography>
                <Typography color="text.secondary">В работе</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SchoolIcon sx={{ fontSize: 60, color: 'warning.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {statements.filter(s => s.status === 'закрыта').length}
                </Typography>
                <Typography color="text.secondary">Закрыто</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              📋 Список ведомостей
            </Typography>
            {statements.length > 0 ? (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.100' }}>
                      <TableCell><strong>№ ведомости</strong></TableCell>
                      <TableCell><strong>Группа</strong></TableCell>
                      <TableCell><strong>Дисциплина</strong></TableCell>
                      <TableCell><strong>Дата выдачи</strong></TableCell>
                      <TableCell><strong>Статус</strong></TableCell>
                      <TableCell><strong>Оценок</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {statements.map((statement: any) => (
                      <TableRow key={statement.id_statement} hover>
                        <TableCell>{statement.number}</TableCell>
                        <TableCell>{statement.group_name}</TableCell>
                        <TableCell>{statement.discipline_name}</TableCell>
                        <TableCell>{statement.issue_date || '—'}</TableCell>
                        <TableCell>
                          <Chip
                            label={statement.status}
                            size="small"
                            color={
                              statement.status === 'в_работе' ? 'warning' :
                              statement.status === 'закрыта' ? 'success' : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>{statement.grades?.length || 0}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info">У вас пока нет ведомостей</Alert>
            )}
          </CardContent>
        </Card>
      </Container>
    </>
  );
}
