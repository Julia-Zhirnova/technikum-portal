import { useEffect, useState } from 'react';
import {
  Container, Typography, Card, CardContent, Button, TextField,
  FormControl, InputLabel, Select, MenuItem, Box, Chip, CircularProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { requestsAPI } from '../services/api';

interface Request {
  id_request: number;
  request_type: string;
  request_type_display: string;
  description: string;
  status: string;
  status_display: string;
  comment: string;
  created_at: string;
}

export default function RequestsPage() {
  const [requests, setRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [newRequest, setNewRequest] = useState({ request_type: 'academic_certificate', description: '' });

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const response = await requestsAPI.getList();
      const data = response.data;
      // Безопасно извлекаем массив: проверяем, является ли data массивом, 
      // или берем поле results (для пагинации DRF), или пустой массив
      const requestsArray = Array.isArray(data) ? data : (data.results || []);
      setRequests(requestsArray);
    } catch (err) {
      console.error('Ошибка загрузки заявок', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      await requestsAPI.create(newRequest);
      setOpenDialog(false);
      setNewRequest({ request_type: 'academic_certificate', description: '' });
      loadRequests();
    } catch (err: any) {
      alert('Ошибка создания заявки: ' + (err.response?.data?.error || err.message));
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
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="bold">📨 Мои заявки</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)}>
          Новая заявка
        </Button>
      </Box>

      {requests.length === 0 ? (
        <Card><CardContent><Typography color="text.secondary">У вас пока нет заявок.</Typography></CardContent></Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {requests.map((req) => (
            <Card key={req.id_request} variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">{req.request_type_display}</Typography>
                  <Chip label={req.status_display} color={getStatusColor(req.status) as any} size="small" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {new Date(req.created_at).toLocaleDateString('ru-RU')}
                </Typography>
                {req.description && <Typography variant="body2" sx={{ mb: 1 }}>Описание: {req.description}</Typography>}
                {req.comment && (
                  <Alert severity="info" sx={{ mt: 1 }}>
                    <strong>Ответ администрации:</strong> {req.comment}
                  </Alert>
                )}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Создать новую заявку</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Тип заявки</InputLabel>
            <Select
              value={newRequest.request_type}
              label="Тип заявки"
              onChange={(e) => setNewRequest({ ...newRequest, request_type: e.target.value })}
            >
              <MenuItem value="academic_certificate">Академическая справка</MenuItem>
              <MenuItem value="study_certificate">Справка с места учебы</MenuItem>
              <MenuItem value="characteristic">Характеристика</MenuItem>
              <MenuItem value="other">Другое</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Описание / Дополнительная информация"
            sx={{ mt: 2 }}
            value={newRequest.description}
            onChange={(e) => setNewRequest({ ...newRequest, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Отмена</Button>
          <Button onClick={handleSubmit} variant="contained">Отправить</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
