import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useState, useEffect } from 'react';

import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import ProfilePage from './pages/ProfilePage';
import CuratorDashboard from './pages/CuratorDashboard';
import CuratorRequestsPage from './pages/CuratorRequestsPage';
import TeacherDashboard from './pages/TeacherDashboard';
import TeacherPracticePage from './pages/TeacherPracticePage';
import RequestsPage from './pages/RequestsPage';
import NotificationsPage from './pages/NotificationsPage';
import StudentDashboard from './pages/StudentDashboard';
import PracticePage from './pages/PracticePage';
import GradesPage from './pages/GradesPage';
import AdminDashboard from './pages/AdminDashboard';
import MckDashboard from './pages/MckDashboard';

import DashboardLayout from './components/DashboardLayout';
import { userAPI } from './services/api';

const theme = createTheme({ palette: { primary: { main: '#1976d2' }, secondary: { main: '#dc004e' } } });

function ProtectedRoute({ children }: { children: React.ReactElement }) {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function SmartRedirect() {
  const [loading, setLoading] = useState(true);
  const [redirect, setRedirect] = useState<string>('/login');

  useEffect(() => {
    const checkRole = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) { setRedirect('/login'); setLoading(false); return; }
      try {
        const response = await userAPI.getProfile();
        const roles = response.data.roles || [];
        const requiresPasswordChange = response.data.requires_password_change;
        console.log('DEBUG: Роли:', roles, 'Смена пароля:', requiresPasswordChange);

        if (requiresPasswordChange) { setRedirect('/change-password'); setLoading(false); return; }
        if (roles.includes('admin')) setRedirect('/admin');
        else if (roles.includes('mck_chairman')) setRedirect('/mck');
        else if (roles.includes('teacher')) setRedirect('/teacher');
        else if (roles.includes('curator')) setRedirect('/curator');
        else if (roles.includes('student')) setRedirect('/student');
        else setRedirect('/login');
      } catch (error: any) {
        console.error('Ошибка проверки роли:', error);
        localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token');
        setRedirect('/login');
      } finally { setLoading(false); }
    };
    checkRole();
  }, []);

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Загрузка...</div>;
  return <Navigate to={redirect} replace />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/" element={<SmartRedirect />} />
          <Route element={<DashboardLayout />}>
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
            <Route path="/mck" element={<ProtectedRoute><MckDashboard /></ProtectedRoute>} />
            <Route path="/curator" element={<ProtectedRoute><CuratorDashboard /></ProtectedRoute>} />
            <Route path="/curator/requests" element={<ProtectedRoute><CuratorRequestsPage /></ProtectedRoute>} />
            <Route path="/teacher" element={<ProtectedRoute><TeacherDashboard /></ProtectedRoute>} />
            <Route path="/teacher/practice" element={<ProtectedRoute><TeacherPracticePage /></ProtectedRoute>} />
            <Route path="/student" element={<ProtectedRoute><StudentDashboard /></ProtectedRoute>} />
            <Route path="/student/grades" element={<ProtectedRoute><GradesPage /></ProtectedRoute>} />
            <Route path="/student/practice" element={<ProtectedRoute><PracticePage /></ProtectedRoute>} />
            <Route path="/student/requests" element={<ProtectedRoute><RequestsPage /></ProtectedRoute>} />
            <Route path="/student/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
          </Route>
          <Route path="*" element={<SmartRedirect />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}
export default App;
