import { Container, Typography, Card, CardContent } from '@mui/material';

export default function DocumentsPage() {
  return (
    <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
      <Typography variant="h4" gutterBottom>
        📄 Мои документы
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1">
            Здесь будет список загруженных документов (паспорт, СНИЛС, ИНН и т.д.)
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Функционал в разработке...
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
}
