import React from 'react';
import { Box, Container, Typography, Stack, Link } from '@mui/material';

export default function Footer() {
  return (
    <Container maxWidth="lg">
      <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between" sx={{ height: '100%' }}>
        <Typography variant="caption" color="text.secondary">
          © 2026 ТехноПортал. ГБПОУ МО «Люберецкий техникум им. Ю.А. Гагарина».
        </Typography>
        <Stack direction="row" spacing={2}>
          <Link href="https://luberteh.ru/" target="_blank" rel="noopener" variant="caption" fontWeight="bold">
            Перейти на сайт →
          </Link>
          <Link href="https://yandex.ru/maps/-/CDu~J~J~J~" target="_blank" rel="noopener" variant="caption" fontWeight="bold">
            Посмотреть на карте →
          </Link>
        </Stack>
      </Stack>
    </Container>
  );
}
