import { Box, Typography, Link, Container } from '@mui/material';

export default function Footer() {
  const yandexMapUrl = "https://yandex.ru/maps/?ll=37.969070%2C55.638299&mode=search&sctx=ZAAAAAgBEAAaKAoSCfcDHhhA8kJAEbZN8bio0ktAEhIJDJQUWABT1j8Rc4I2OXzSvT8iBgABAgMEBSgKOABAooIGSAFqAnJ1nQHNzMw9oAEAqAEAvQF4Cb%2FLwgEU6YLN8QPxmaKcBP%2B61%2FAD2aTZzgSCAjLQu9GO0LHQtdGA0LXRhtC60LjQuSDRgtC10YXQvdC40LrRg9C8INC60L7RgNC%2F0YPRgYoCAJICAJoCDGRlc2t0b3AtbWFwcw%3D%3D&sll=37.969070%2C55.638299&source=serp_navig&sspn=0.348816%2C0.116516&text=%D0%BB%D1%8E%D0%B1%D0%B5%D1%80%D0%B5%D1%86%D0%BA%D0%B8%D0%B9%20%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D1%83%D0%BC%20%D0%BA%D0%BE%D1%80%D0%BF%D1%83%D1%81&z=12";

  return (
    <Box 
      component="footer" 
      sx={{ 
        bgcolor: 'background.paper', 
        borderTop: '1px solid', 
        borderColor: 'divider', 
        py: 3, 
        mt: 'auto' 
      }}
    >
      <Container maxWidth="lg">
        {/* 1.5.1: Текст копирайта */}
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
          © 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина»
        </Typography>

        {/* 1.5.4: Корпуса в строчку */}
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2, fontWeight: 'medium' }}>
          Корпуса: Люберецкий, Гагаринский, Красково, Угреша
        </Typography>

        {/* 1.5.2 и 1.5.3: Ссылки */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
          <Link 
            href="https://luberteh.ru/" 
            target="_blank" 
            rel="noopener noreferrer"
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            Перейти на сайт →
          </Link>
          <Link 
            href={yandexMapUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            Посмотреть на карте →
          </Link>
        </Box>
      </Container>
    </Box>
  );
}
