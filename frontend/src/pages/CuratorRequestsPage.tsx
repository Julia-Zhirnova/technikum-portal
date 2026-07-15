import { useEffect, useState } from 'react';
import {
  Container, Typography, Card, CardContent, Box, Chip, CircularProgress, 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import { curatorRequestsAPI } from '../services/api';

interface Request {
  id_request: number;
  student_name: string;
  request_type_display: string;
  description: string;
  status: string;
  status_display: string;
  comment: string;
  created_at: string;
}

export default function CuratorRequestsPage() {
  const [requests, setRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState<Request | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [updateData, setUpdateData] = useState({ status: 'pending', comment: '' });

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const response = await curatorRequestsAPI.getList();
      const data = response.data;
      const requestsArray = Array.isArray(data) ? data : (data.results || []);
      setRequests(requestsArray);
    } catch (err) {
      console.error('Ошибка загрузки заявок', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (req: Request) => {
    setSelectedRequest(req);
    setUpdateData({ status: req.status, comment: req.comment || '' });
    setOpenDialog(true);
  };

  const handleUpdate = async () => {
    if (!selectedRequest) return;
    try {
      await curatorRequestsAPI.update(selectedRequest.id_request, updateData);
      setOpenDialog(false);
      loadRequests();
    } catch (err: any) {
      alert('Ошибка обновления: ' + (err.response?.data?.error || err.message));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'info';
      case 'rejected': return 'error';
      case 'ready': return 'success';
      default: return 'default';
    }
  };

  if (loading) return <Box sx={{ textAlign: 'center', mt: 5 }}><CircularProgress /></Box>;

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>📨 Заявки студентов моей группы</Typography>

      {requests.length === 0 ? (
        <Card><CardContent><Typography color="text.secondary">Нет активных заявок от студентов вашей группы.</Typography></CardContent></Card>
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow sx={{ bgcolor: 'grey.100' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Студент</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Тип заявки</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Описание</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Дата</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Статус</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.map((req) => (
                <TableRow key={req.id_request} hover>
                  <TableCell>
                    {req.student_name}
                  </TableCell>
                  <TableCell>{req.request_type_display}</TableCell>
                  <TableCell>{req.description || '—'}</TableCell>
                  <TableCell>{new Date(req.created_at).toLocaleDateString('ru-RU')}</TableCell>
                  <TableCell>
                    <Chip label={req.status_display} color={getStatusColor(req.status) as any} size="small" />
                  </TableCell>
                  <TableCell>
                    <Button size="small" variant="outlined" onClick={() => handleOpenDialog(req)}>
                      Ответить
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Обработка заявки</DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                Студент: {selectedRequest.student_name}
              </Typography>
              <Typography variant="body2" sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                <strong>Описание:</strong> {selectedRequest.description || 'Нет описания'}
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Новый статус</InputLabel>
                <Select
                  value={updateData.status}
                  label="Новый статус"
                  onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
                >
                  <MenuItem value="pending">В обработке</MenuItem>
                  <MenuItem value="approved">Одобрено</MenuItem>
                  <MenuItem value="rejected">Отклонено</MenuItem>
                  <MenuItem value="ready">Готово к выдаче</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Комментарий для студента"
                value={updateData.comment}
                onChange={(e) => setUpdateData({ ...updateData, comment: e.target.value })}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
          <Button onClick={handleUpdate} variant="contained">Сохранить</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
