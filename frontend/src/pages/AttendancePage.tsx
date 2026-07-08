import { Container, Typography, Card, CardContent, Alert } from '@mui/material';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

export default function AttendancePage() {
  return (
    <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 5 }}>
          <CalendarTodayIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            📅 Посещаемость
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Раздел в разработке. Здесь будет табель посещаемости.
          </Alert>
        </CardContent>
      </Card>
    </Container>
  );
}
