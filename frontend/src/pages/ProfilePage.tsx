import { Container, Typography, Card, CardContent } from '@mui/material';

export default function ProfilePage() {
  return (
    <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
      <Typography variant="h4" gutterBottom>
        👤 Мой профиль
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Здесь будет ваша анкета с персональными данными
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Функционал в разработке...
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
}
