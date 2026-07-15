import { useState, useEffect } from 'react';
import {
  Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, 
  TableRow, Paper, Button, TextField, Select, MenuItem, FormControl, InputLabel, 
  Dialog, DialogTitle, DialogContent, DialogActions, IconButton, Tooltip, 
  Alert, CircularProgress, Chip
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import { teacherPracticeAPI } from '../services/api';

interface PracticePlace {
  id_place: number;
  student_name: string;
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
}

export default function TeacherPracticePage() {
  const [practices, setPractices] = useState<PracticePlace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedPlace, setSelectedPlace] = useState<PracticePlace | null>(null);
  const [editForm, setEditForm] = useState({ organization_name: '', position: '', status: '' });

  useEffect(() => {
    loadPractices();
  }, []);

  const loadPractices = async () => {
    try {
      setLoading(true);
      const response = await teacherPracticeAPI.getStudents();
      const data = response.data;
      // Обрабатываем как массив, так и пагинированный ответ
      const practicesData = Array.isArray(data) ? data : (data.results || []);
      setPractices(practicesData);
    } catch (err: any) {
      console.error('Ошибка загрузки практики', err);
      setError('Не удалось загрузить данные о практике');
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (place: PracticePlace) => {
    setSelectedPlace(place);
    setEditForm({
      organization_name: place.organization_name || '',
      position: place.position || '',
      status: place.status || 'Назначена'
    });
    setEditDialogOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedPlace) return;
    try {
      await teacherPracticeAPI.updatePlace(selectedPlace.id_place, editForm);
      setEditDialogOpen(false);
      loadPractices();
    } catch (err: any) {
      console.error('Ошибка обновления', err);
      alert('Не удалось обновить данные');
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}><CircularProgress /></Box>;
  }

  if (error) {
    return <Box sx={{ p: 3 }}><Alert severity="error">{error}</Alert></Box>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Практика студентов
      </Typography>

      <TableContainer component={Paper} variant="outlined" sx={{ mt: 3 }}>
        <Table>
          <TableHead sx={{ bgcolor: 'primary.light' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Студент</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Организация</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Должность</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Статус</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Дневник</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {practices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">Нет данных о практике</TableCell>
              </TableRow>
            ) : (
              practices.map((place) => (
                <TableRow key={place.id_place} hover>
                  <TableCell>{place.student_name || 'Неизвестно'}</TableCell>
                  <TableCell>{place.organization_name || 'Не назначена'}</TableCell>
                  <TableCell>{place.position || '-'}</TableCell>
                  <TableCell>
                    <Chip label={place.status || 'Неизвестно'} color={place.status === 'Завершена' ? 'success' : 'warning'} size="small" />
                  </TableCell>
                  <TableCell>
                    {place.diary?.length || 0} записей
                    {place.diary?.filter((d: any) => !d.is_approved_by_org).length > 0 && (
                      <Chip label={`${place.diary.filter((d: any) => !d.is_approved_by_org).length} не одобрено`} color="error" size="small" sx={{ ml: 1 }} />
                    )}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Редактировать">
                      <IconButton onClick={() => handleEditClick(place)} color="primary">
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Редактировать место практики</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Организация" value={editForm.organization_name} onChange={(e) => setEditForm({...editForm, organization_name: e.target.value})} margin="normal" />
          <TextField fullWidth label="Должность" value={editForm.position} onChange={(e) => setEditForm({...editForm, position: e.target.value})} margin="normal" />
          <FormControl fullWidth margin="normal">
            <InputLabel>Статус</InputLabel>
            <Select value={editForm.status} label="Статус" onChange={(e) => setEditForm({...editForm, status: e.target.value})}>
              <MenuItem value="Назначена">Назначена</MenuItem>
              <MenuItem value="В процессе">В процессе</MenuItem>
              <MenuItem value="Завершена">Завершена</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleSaveEdit} variant="contained" color="primary">Сохранить</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
