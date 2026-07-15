import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, AppBar, Toolbar, IconButton, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Accordion, AccordionSummary, AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import SchoolIcon from '@mui/icons-material/School';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import RefreshIcon from '@mui/icons-material/Refresh';
import { studentAPI } from '../services/api';
import NotificationBell from '../components/NotificationBell';
import RoleSwitcher from '../components/RoleSwitcher';

export default function GradesPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [gradesData, setGradesData] = useState<any>(null);

  useEffect(() => {
    const loadGrades = async () => {
      try {
        const response = await studentAPI.getGrades();
        setGradesData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Ошибка загрузки оценок');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadGrades();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', mt: 10 }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <>
        <Container maxWidth="md" sx={{ mt: 5 }}>
          <Alert severity="error">{error}</Alert>
        </Container>
      </>
    );
  }

  const getGradeColor = (grade: string) => {
    if (grade === '5' || grade === 'отлично' || grade === 'Отлично') return 'success';
    if (grade === '4' || grade === 'хорошо' || grade === 'Хорошо') return 'primary';
    if (grade === '3' || grade === 'удовлетворительно' || grade === 'Удовлетворительно') return 'warning';
    if (grade === '2' || grade === 'неудовлетворительно' || grade === 'Неудовлетворительно' || grade === 'не зачтено' || grade === 'Не зачтено') return 'error';
    if (grade === 'зачтено' || grade === 'Зачтено') return 'success';
    return 'default';
  };

  return (
    <>

      <Container maxWidth="lg" sx={{ pb: 5, pt: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
           Зачётная книжка
        </Typography>

        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Группа: {gradesData.group} | СНИЛС: {gradesData.student_snils}
        </Typography>

        {/* Статистика */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SchoolIcon sx={{ fontSize: 50, color: 'primary.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {gradesData.total_grades}
                </Typography>
                <Typography color="text.secondary" variant="body2">Всего оценок</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <EmojiEventsIcon sx={{ fontSize: 50, color: 'success.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  {gradesData.excellent_count}
                </Typography>
                <Typography color="text.secondary" variant="body2">Отлично</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" fontWeight="bold" color="primary.main">
                  {gradesData.good_count}
                </Typography>
                <Typography color="text.secondary" variant="body2">Хорошо</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" fontWeight="bold" color="warning.main">
                  {gradesData.satisfactory_count}
                </Typography>
                <Typography color="text.secondary" variant="body2">Удовл.</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" fontWeight="bold" color="error.main">
                  {gradesData.unsatisfactory_count}
                </Typography>
                <Typography color="text.secondary" variant="body2">Неудовл.</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <RefreshIcon sx={{ fontSize: 50, color: 'warning.main', mb: 1 }} />
                <Typography variant="h3" fontWeight="bold">
                  {gradesData.retake_count}
                </Typography>
                <Typography color="text.secondary" variant="body2">Пересдач</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {gradesData.average_score > 0 && (
          <Card sx={{ mb: 4, bgcolor: 'primary.light', color: 'white' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h5" fontWeight="bold">
                Средний балл: {gradesData.average_score}
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Семестры */}
        {gradesData.semesters.length > 0 ? (
          gradesData.semesters.map((semester: any) => (
            <Accordion key={semester.semester} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  Семестр {semester.semester} ({semester.grades.length} оценок)
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.100' }}>
                        <TableCell><strong>Дисциплина</strong></TableCell>
                        <TableCell><strong>Оценка</strong></TableCell>
                        <TableCell><strong>Дата</strong></TableCell>
                        <TableCell><strong>Ведомость</strong></TableCell>
                        <TableCell><strong>Пересдача</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {semester.grades.map((grade: any, idx: number) => (
                        <TableRow key={idx} hover>
                          <TableCell>{grade.discipline}</TableCell>
                          <TableCell>
                            <Chip
                              label={grade.grade}
                              size="small"
                              color={getGradeColor(grade.grade)}
                            />
                          </TableCell>
                          <TableCell>{grade.date}</TableCell>
                          <TableCell>{grade.statement_number}</TableCell>
                          <TableCell>
                            <Chip
                              label={grade.is_retake ? 'Да' : 'Нет'}
                              size="small"
                              color={grade.is_retake ? 'warning' : 'default'}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          ))
        ) : (
          <Alert severity="info">Оценки не сгруппированы по семестрам</Alert>
        )}
      </Container>
    </>
  );
}
