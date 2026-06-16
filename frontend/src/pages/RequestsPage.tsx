import { Container, Typography, Card, CardContent } from '@mui/material';

export default function RequestsPage() {
  return (
    <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
      <Typography variant="h4" gutterBottom>📨 Мои заявки</Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Здесь будут ваши заявки на справки, материальную помощь и другие услуги
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Функционал в разработке...
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
}
