import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import ProfilePage from './pages/ProfilePage';
import CuratorDashboard from './pages/CuratorDashboard';
import { userAPI } from './services/api';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});

function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function SmartRedirect() {
  const [loading, setLoading] = useState(true);
  const [redirect, setRedirect] = useState<string>('/login');

  useEffect(() => {
    const checkRole = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setRedirect('/login');
        setLoading(false);
        return;
      }

      try {
        // Используем /api/user/profile/ для всех пользователей
        const response = await userAPI.getProfile();
        const roles = response.data.roles;
        
        console.log('Роли пользователя:', roles);
        
        // Определяем, куда перенаправить
        if (roles.includes('student')) {
          setRedirect('/profile');
        } else if (roles.includes('curator')) {
          setRedirect('/curator');
        } else if (roles.includes('teacher')) {
          setRedirect('/curator'); // Временно, пока нет TeacherDashboard
        } else if (roles.includes('admin')) {
          setRedirect('/curator'); // Временно, пока нет AdminDashboard
        } else {
          setRedirect('/login');
        }
      } catch (error) {
        console.error('Ошибка проверки роли:', error);
        setRedirect('/login');
      } finally {
        setLoading(false);
      }
    };

    checkRole();
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Загрузка...</div>;
  }

  return <Navigate to={redirect} replace />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<SmartRedirect />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/curator"
            element={
              <ProtectedRoute>
                <CuratorDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<SmartRedirect />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
