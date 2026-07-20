import React, { createContext, useContext, useState, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme, CssBaseline } from '@mui/material';

type ThemeMode = 'light-blue' | 'dark-gagarin' | 'light-eco';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({ mode: 'light-blue', toggleTheme: () => {} });

export const useTheme = () => useContext(ThemeContext);

// Глобальная анимация fadeIn
const fadeInAnimation = `
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

// Глобальные стили для четкости шрифтов
const globalStyles = `
  body { 
    animation: fadeIn 0.5s ease-out; 
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  * {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
`;

const themes = {
  // Светлая тема
  'light-blue': createTheme({
    palette: {
      mode: 'light',
      primary: { main: '#22577a' },
      secondary: { main: '#38a3a5' },
      background: { default: '#f0f4f8', paper: '#FFFFFF' },
      text: { primary: '#1a202c', secondary: '#4a5568' },
    },
    typography: {
      fontFamily: '"Inter", sans-serif',
      h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
    },
    components: {
      MuiTableContainer: { styleOverrides: { root: { bgcolor: 'background.paper', borderRadius: 2, boxShadow: 1 } } },
      MuiTableCell: { styleOverrides: { head: { fontWeight: 'bold', color: 'text.primary' }, body: { color: 'text.secondary' } } },
      MuiTableRow: { styleOverrides: { root: { '&:hover': { bgcolor: 'action.hover' } } } },
      MuiCard: { styleOverrides: { root: { animation: 'fadeIn 0.3s ease-out' } } },
    },
  }),
  
  // Темная тема (Космический Гагарин)
  // Убрал #00ff00 из фона и шапки, оставил только как акцент
  'dark-gagarin': createTheme({
    palette: {
      mode: 'dark',
      primary: { main: '#69f0ae' }, // Яркий акцент для кнопок
      secondary: { main: '#5bc0be' },
      background: { default: '#0d2b1a', paper: '#1a3a2a' }, // Тёмно-зелёный фон
      text: { primary: '#ffffff', secondary: '#b0b0b0' },
    },
    typography: {
      fontFamily: '"Inter", sans-serif',
      h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
    },
    components: {
      MuiTableContainer: { styleOverrides: { root: { bgcolor: 'background.paper', borderRadius: 2, border: '1px solid #3a506b' } } },
      MuiTableCell: { styleOverrides: { 
        root: { borderBottom: '1px solid #3a506b', color: '#e2e8f0' },
        head: { fontWeight: 'bold', color: '#ccff00', backgroundColor: '#1c2541' } // Акцент в заголовке таблицы
      } },
      MuiTableRow: { styleOverrides: { root: { '&:hover': { bgcolor: 'rgba(204, 255, 0, 0.05)' } } } },
      MuiCard: { styleOverrides: { root: { animation: 'fadeIn 0.3s ease-out', border: '1px solid #3a506b', bgcolor: '#1c2541' } } },
      MuiAppBar: { styleOverrides: { root: { bgcolor: '#1a3a2a' } } }, // Тёмно-зелёная шапка // Шапка темно-синяя, не зеленая
    },
  }),
  
  // Пастельная тема
  'light-eco': createTheme({
    palette: {
      mode: 'light',
      primary: { main: '#2d6a4f' },
      secondary: { main: '#52b788' },
      background: { default: '#d8f3dc', paper: '#ffffff' },
      text: { primary: '#081c15', secondary: '#40916c' },
    },
    typography: {
      fontFamily: '"Inter", sans-serif',
      h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
      h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700 },
    },
    components: {
      MuiTableContainer: { styleOverrides: { root: { bgcolor: 'background.paper', borderRadius: 2, boxShadow: 1 } } },
      MuiTableCell: { styleOverrides: { head: { fontWeight: 'bold', color: 'primary.main' }, body: { color: 'text.secondary' } } },
      MuiTableRow: { styleOverrides: { root: { '&:hover': { bgcolor: 'action.hover' } } } },
      MuiCard: { styleOverrides: { root: { animation: 'fadeIn 0.3s ease-out' } } },
    },
  }),
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>('light-blue');

  const toggleTheme = () => {
    setMode(prev => {
      if (prev === 'light-blue') return 'dark-gagarin';
      if (prev === 'dark-gagarin') return 'light-eco';
      return 'light-blue';
    });
  };

  const themeWithStyles = useMemo(() => {
    const baseTheme = themes[mode];
    return createTheme(baseTheme, {
      components: {
        MuiCssBaseline: {
          styleOverrides: `${fadeInAnimation} ${globalStyles}`,
        },
      },
    });
  }, [mode]);

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme }}>
      <MuiThemeProvider theme={themeWithStyles}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}
