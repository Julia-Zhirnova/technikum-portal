import React from 'react';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#757575' },
    background: { default: '#ffffff', paper: '#ffffff' },
    text: { primary: '#000000', secondary: '#424242' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          backgroundColor: '#e0e0e0', // Светло-серый фон
          color: '#000000',         // ЧЕРНЫЙ ТЕКСТ
          '&:hover': { backgroundColor: '#bdbdbd', color: '#000000' },
        },
        containedPrimary: { backgroundColor: '#9e9e9e', color: '#000000' },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: '#ffffff', color: '#000000', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' },
      },
    },
  },
});

export const useAppTheme = () => ({ mode: 'light', toggleTheme: () => {} });

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MuiThemeProvider theme={theme}><CssBaseline />{children}</MuiThemeProvider>
);
