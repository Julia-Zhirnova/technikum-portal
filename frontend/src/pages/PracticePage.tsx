import { Container, Typography, Card, CardContent, Alert } from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';

export default function PracticePage() {
  return (
    <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 5 }}>
          <WorkIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            💼 Практика
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Раздел в разработке. Здесь будет информация о вашей практике.
          </Alert>
        </CardContent>
      </Card>
    </Container>
  );
}
