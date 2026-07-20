import { createTheme } from '@mui/material/styles';

const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
  h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
  h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
  h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
  h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
  h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
};

export const lightBlueTheme = createTheme({
  palette: { mode: 'light', primary: { main: '#22577a' }, secondary: { main: '#38a3a5' } },
  typography,
});

export const pastelGreenTheme = createTheme({
  palette: { mode: 'light', primary: { main: '#52b788' }, secondary: { main: '#74c69d' } },
  typography,
});

// ИСПРАВЛЕНИЕ ТЕМНОЙ ТЕМЫ: Темно-зеленый фон для читаемости белого текста
export const darkGagarinTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#69f0ae' },
    secondary: { main: '#5bc0be' },
    background: { default: '#0d2b1a', paper: '#1a3a2a' },
    text: { primary: '#ffffff', secondary: '#e0e0e0' },
  },
  typography,
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: '#0d2b1a' },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundColor: '#1a3a2a', color: '#ffffff' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { backgroundColor: '#1a3a2a', color: '#ffffff' },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a3a2a',
          '& .MuiTableCell-root': { color: '#ffffff', fontWeight: 'bold' },
        },
      },
    },
  },
}); // <-- ВОССТАНОВЛЕНЫ ЗАКРЫВАЮЩИЕ СКОБКИ
