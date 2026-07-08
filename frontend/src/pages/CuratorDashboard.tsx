import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, AppBar, Toolbar, IconButton, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { curatorAPI } from '../services/api';
import NotificationBell from '../components/NotificationBell';

export default function CuratorDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [groupData, setGroupData] = useState<any>(null);

  useEffect(() => {
    const loadGroup = async () => {
      try {
        const response = await curatorAPI.getGroup();
        setGroupData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки данных');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadGroup();
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

  if (error || !groupData) {
    return (
      <Container maxWidth="md" sx={{ mt: 5 }}>
        <Alert severity="error">{error || 'Данные не найдены'}</Alert>
      </Container>
    );
  }

  return (
    <>
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🎓 Люберецкий техникум — Куратор
          </Typography>
          <NotificationBell />
          <IconButton onClick={handleLogout} color="inherit" title="Выйти">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ pb: 5, pt: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          📊 Моя группа: {groupData.id_group}
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <PeopleIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {groupData.students?.length || 0}
                </Typography>
                <Typography color="text.secondary">Студентов в группе</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AssignmentIcon sx={{ fontSize: 60, color: 'success.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  0
                </Typography>
                <Typography color="text.secondary">Новых заявок</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AssignmentIcon sx={{ fontSize: 60, color: 'warning.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  92%
                </Typography>
                <Typography color="text.secondary">Средняя посещаемость</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              👥 Студенты группы
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>ФИО</strong></TableCell>
                    <TableCell><strong>СНИЛС</strong></TableCell>
                    <TableCell><strong>Телефон</strong></TableCell>
                    <TableCell><strong>Статус</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {groupData.students?.map((student: any) => (
                    <TableRow key={student.snils} hover>
                      <TableCell>{student.full_name}</TableCell>
                      <TableCell>{student.snils}</TableCell>
                      <TableCell>{student.phone || '—'}</TableCell>
                      <TableCell>
                        <Chip label={student.status} size="small" color="success" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Container>
    </>
  );
}
