import { Container, Typography, Card, CardContent, Alert } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';

export default function GradesPage() {
  return (
    <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 5 }}>
          <SchoolIcon sx={{ fontSize: 60, color: 'grey.400', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            📖 Зачётная книжка
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Раздел в разработке. Здесь будут ваши оценки по семестрам.
          </Alert>
        </CardContent>
      </Card>
    </Container>
  );
}
