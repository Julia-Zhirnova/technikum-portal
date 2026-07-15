import { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Button, Tabs, Tab, Divider, CircularProgress, Alert
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';
import { practiceAPI } from '../services/api';

interface PracticeData {
  id_place: number;
  organization_name: string;
  position: string;
  status: string;
  diary: Array<{
    id_entry: number;
    date: string;
    work_content: string;
    hours: number;
    is_approved_by_org: boolean;
  }>;
  attestation?: {
    id_attestation: number;
    competencies_eval: string;
    characteristic_text: string;
    recommended_grade: string;
    fill_date: string;
  };
}

export default function PracticePage() {
  const [tabValue, setTabValue] = useState(0);
  const [practice, setPractice] = useState<PracticeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPractice();
  }, []);

  const loadPractice = async () => {
    try {
      setLoading(true);
      const response = await practiceAPI.getStudentPractice();
      setPractice(response.data);
    } catch (err: any) {
      console.error('Ошибка загрузки практики', err);
      setError('Информация о практике не найдена');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !practice) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          {error || 'Информация о практике не найдена. Обратитесь к куратору.'}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        💼 Моя практика
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight="bold">
              {practice.organization_name || 'Организация не указана'}
            </Typography>
            <Chip 
              icon={<CheckCircleIcon />} 
              label={practice.status || 'Неизвестно'} 
              color={practice.status === 'Завершена' ? 'success' : 'warning'} 
              variant="outlined" 
            />
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Должность:</Typography>
              <Typography variant="body1" fontWeight="medium">{practice.position || 'Не указана'}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Дневник практики" />
          <Tab label="Отчетность и документы" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead sx={{ bgcolor: 'grey.100' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Дата</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Содержание выполненных работ</TableCell>
                <TableCell sx={{ fontWeight: 'bold', textAlign: 'right' }}>Часы</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {practice.diary && practice.diary.map((entry) => (
                <TableRow key={entry.id_entry} hover>
                  <TableCell>{new Date(entry.date).toLocaleDateString('ru-RU')}</TableCell>
                  <TableCell>{entry.work_content}</TableCell>
                  <TableCell sx={{ textAlign: 'right' }}>{entry.hours}</TableCell>
                </TableRow>
              ))}
              <TableRow sx={{ bgcolor: 'grey.50', fontWeight: 'bold' }}>
                <TableCell colSpan={2} align="right" sx={{ fontWeight: 'bold' }}>Итого:</TableCell>
                <TableCell sx={{ textAlign: 'right', fontWeight: 'bold' }}>
                  {practice.diary?.reduce((sum, item) => sum + item.hours, 0) || 0}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {tabValue === 1 && (
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <DescriptionIcon color="primary" sx={{ fontSize: 40 }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Отчет по практике</Typography>
                  <Typography variant="body2" color="text.secondary">PDF, 2.4 МБ • Загружен 23.12.2025</Typography>
                </Box>
                <Button variant="outlined" size="small">Скачать</Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <DescriptionIcon color="success" sx={{ fontSize: 40 }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Дневник практики (подписанный)</Typography>
                  <Typography variant="body2" color="text.secondary">PDF, 1.1 МБ • Загружен 23.12.2025</Typography>
                </Box>
                <Button variant="outlined" size="small">Скачать</Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <PendingIcon color="warning" sx={{ fontSize: 40 }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">Характеристика от руководителя</Typography>
                  <Typography variant="body2" color="text.secondary">Ожидает загрузки от организации</Typography>
                </Box>
                <Button variant="contained" size="small">Загрузить</Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
