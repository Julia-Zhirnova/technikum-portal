import { Container, Typography, Card, CardContent, Alert } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

export default function NotificationsPage() {
  return (
    <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 5 }}>
          <NotificationsIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            🔔 Уведомления
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Раздел в разработке. Здесь будут все ваши уведомления.
          </Alert>
        </CardContent>
      </Card>
    </Container>
  );
}
