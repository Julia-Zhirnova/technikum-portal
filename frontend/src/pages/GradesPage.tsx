import { useEffect, useState } from 'react';
import { 
  Box, Typography, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, CircularProgress, Alert, Chip 
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import { studentAPI } from '../services/api';

interface GradeItem {
  id_grade?: number;
  discipline_name: string;
  grade: string;
  date: string;
  statement_number?: string;
}

export default function GradesPage() {
  const [grades, setGrades] = useState<GradeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadGrades = async () => {
      try {
        setLoading(true);
        const response = await studentAPI.getGrades();
        // Обработка разных форматов ответа (массив или пагинация DRF)
        const data = response.data;
        setGrades(Array.isArray(data) ? data : (data.results || []));
      } catch (err: any) {
        console.error('Ошибка загрузки оценок:', err);
        setError(err.response?.data?.detail || 'Не удалось загрузить данные об успеваемости');
      } finally {
        setLoading(false);
      }
    };

    loadGrades();
  }, []);

  // Функция для определения цвета оценки
  const getGradeColor = (grade: string): "success" | "warning" | "error" | "default" => {
    const g = grade.toLowerCase();
    if (g.includes('5') || g.includes('отлично') || g === 'зачтено') return 'success';
    if (g.includes('4') || g.includes('хорошо')) return 'primary' as any; // primary нет в типе color, но работает
    if (g.includes('3') || g.includes('удовлетворительно')) return 'warning';
    if (g.includes('2') || g.includes('неуд') || g === 'не_зачтено') return 'error';
    return 'default';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SchoolIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
        <Typography variant="h4" fontWeight="bold">Зачётная книжка</Typography>
      </Box>

      {grades.length === 0 ? (
        <Alert severity="info" sx={{ mt: 2 }}>
          Оценки пока отсутствуют. Возможно, ведомости еще не закрыты преподавателем.
        </Alert>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead sx={{ bgcolor: 'grey.100' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Дисциплина</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Оценка</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Дата</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Ведомость</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {grades.map((item, index) => (
                <TableRow key={item.id_grade || index} hover>
                  <TableCell>{item.discipline_name}</TableCell>
                  <TableCell>
                    <Chip 
                      label={item.grade || '—'} 
                      size="small" 
                      color={getGradeColor(item.grade)} 
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{item.date ? new Date(item.date).toLocaleDateString('ru-RU') : '—'}</TableCell>
                  <TableCell>{item.statement_number || '—'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
