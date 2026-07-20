import React from 'react';
import { Box, Container, Typography, useMediaQuery } from '@mui/material';

export default function Footer({ height = 60 }) {
  const isMobile = useMediaQuery('(max-width:600px)');
  
  return (
    <Box sx={{ 
      height: `${height}px`, width: '100%', 
      bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      position: 'fixed', bottom: 0, left: 0, zIndex: 1200
    }}>
      <Container maxWidth="lg">
        <Box sx={{ 
          display: 'flex', 
          flexDirection: isMobile ? 'column' : 'row',
          gap: 2, 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          height: '100%' 
        }}>
          <Typography variant="caption" color="text.secondary">
            © 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина».
          </Typography>
          {!isMobile && (
            <Typography variant="caption" color="text.secondary">
              г. Люберцы, Октябрьский проспект, д.114 | Тел: 8(495) 503-45-77
            </Typography>
          )}
        </Box>
      </Container>
    </Box>
  );
}