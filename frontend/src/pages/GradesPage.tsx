import { Typography, Box } from '@mui/material';
import SchoolIcon from '@mui/icons-material/School'; // Та же иконка, что в сайдбаре

export default function GradesPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SchoolIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
        <Typography variant="h4" fontWeight="bold">Зачётная книжка</Typography>
      </Box>
      <Typography variant="body1" color="text.secondary">
        Оценки, ведомости и средний балл
      </Typography>
      {/* Здесь будет контент зачётки */}
    </Box>
  );
}
