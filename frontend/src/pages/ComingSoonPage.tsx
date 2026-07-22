import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ConstructionIcon from '@mui/icons-material/Construction';

export default function ComingSoonPage() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ py: 10 }}>
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        textAlign: 'center',
        p: 4,
        border: '1px dashed #ccc',
        borderRadius: 4,
        bgcolor: 'background.paper'
      }}>
        <ConstructionIcon sx={{ fontSize: 80, color: '#757575', mb: 3 }} />
        
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#000' }}>
          Страница в разработке
        </Typography>
        
        <Typography variant="body1" sx={{ color: '#424242', mb: 4, maxWidth: 500 }}>
          Этот раздел портала ТехноПортал пока находится в активной разработке. 
          Мы работаем над тем, чтобы сделать его максимально удобным для вас. 
          Пожалуйста, воспользуйтесь другими пунктами меню или вернитесь позже.
        </Typography>
        
        <Button 
          variant="contained" 
          onClick={() => navigate(-1)}
          sx={{ 
            backgroundColor: '#e0e0e0', 
            color: '#000',
            '&:hover': { backgroundColor: '#bdbdbd' },
            px: 4,
            py: 1.5
          }}
        >
          Вернуться назад
        </Button>
      </Box>
    </Container>
  );
}
