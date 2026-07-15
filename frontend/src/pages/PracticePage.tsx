import { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Button, Tabs, Tab, Divider
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';

export default function PracticePage() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Пример данных (в будущем будут приходить с бэкенда)
  const practiceInfo = {
    type: 'Учебная практика (УП.02.01)',
    place: 'ООО "ТехноСервис", г. Люберцы, ул. Кирова, д. 15',
    supervisor: 'Иванов Иван Иванович',
    dates: '17.12.2025 – 23.12.2025',
    status: 'Завершена'
  };

  const diaryEntries = [
    { date: '17.12.2025', content: 'Ознакомление с правилами техники безопасности и внутренним распорядком организации.', hours: 6 },
    { date: '18.12.2025', content: 'Изучение структуры ИТ-отдела и используемого программного обеспечения.', hours: 6 },
    { date: '19.12.2025', content: 'Участие в настройке рабочих мест и установке необходимого ПО.', hours: 6 },
    { date: '20.12.2025', content: 'Самостоятельное выполнение заданий руководителя практики.', hours: 6 },
    { date: '23.12.2025', content: 'Оформление отчета по практике, подписание дневника руководителем.', hours: 4 },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        💼 Производственная / Учебная практика
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight="bold">{practiceInfo.type}</Typography>
            <Chip 
              icon={<CheckCircleIcon />} 
              label={practiceInfo.status} 
              color="success" 
              variant="outlined" 
            />
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Место прохождения:</Typography>
              <Typography variant="body1" fontWeight="medium">{practiceInfo.place}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Руководитель от организации:</Typography>
              <Typography variant="body1" fontWeight="medium">{practiceInfo.supervisor}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Период прохождения:</Typography>
              <Typography variant="body1" fontWeight="medium">{practiceInfo.dates}</Typography>
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
              {diaryEntries.map((entry, index) => (
                <TableRow key={index} hover>
                  <TableCell>{entry.date}</TableCell>
                  <TableCell>{entry.content}</TableCell>
                  <TableCell sx={{ textAlign: 'right' }}>{entry.hours}</TableCell>
                </TableRow>
              ))}
              <TableRow sx={{ bgcolor: 'grey.50', fontWeight: 'bold' }}>
                <TableCell colSpan={2} align="right" sx={{ fontWeight: 'bold' }}>Итого:</TableCell>
                <TableCell sx={{ textAlign: 'right', fontWeight: 'bold' }}>
                  {diaryEntries.reduce((sum, item) => sum + item.hours, 0)}
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
