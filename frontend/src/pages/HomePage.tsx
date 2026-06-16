import { useEffect, useState } from 'react';
import { Container, Typography, Card, CardContent, Grid, Chip, Box } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import axios from 'axios';

interface Korpus {
  id: number;
  nazvanie: string;
  adres: string;
  telefon: string;
}

export default function HomePage() {
  const [korpusy, setKorpusy] = useState<Korpus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/korpusy/')
      .then(response => {
        setKorpusy(response.data.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Ошибка загрузки данных:', error);
        setLoading(false);
      });
  }, []);

  return (
    <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <SchoolIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Люберецкий техникум
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          имени Героя Советского Союза, лётчика-космонавта Ю.А. Гагарина
        </Typography>
        <Chip label="Портал персональных данных студентов" color="primary" sx={{ mt: 2 }} />
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Добро пожаловать!</Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Этот портал предназначен для управления персональными данными студентов техникума.
            Здесь вы можете:
          </Typography>
          <ul style={{ paddingLeft: '20px', margin: '10px 0' }}>
            <li>Просматривать и редактировать свои данные</li>
            <li>Загружать сканы документов</li>
            <li>Подавать заявки на справки и материальную помощь</li>
            <li>Отслеживать статус заявок</li>
          </ul>
        </CardContent>
      </Card>

      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        🏢 Корпуса техникума
      </Typography>

      {loading ? (
        <Typography>Загрузка...</Typography>
      ) : korpusy.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="error">
              ⚠️ Не удалось загрузить данные. Убедитесь, что Django backend запущен на порту 8000.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={2}>
          {korpusy.map(korpus => (
            <Grid item xs={12} md={6} key={korpus.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>{korpus.nazvanie}</Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    📍 {korpus.adres}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    📞 {korpus.telefon}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}
