import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './ThemeContext';
import CssBaseline from '@mui/material/CssBaseline';
import DashboardLayout from './components/DashboardLayout';
import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/StudentDashboard';
import TeacherDashboard from './pages/TeacherDashboard';
import AdminDashboard from './pages/AdminDashboard';
import CuratorDashboard from './pages/CuratorDashboard';
import MckDashboard from './pages/MckDashboard';
import ProfilePage from './pages/ProfilePage';
import GradesPage from './pages/GradesPage';
import PracticePage from './pages/PracticePage';
import RequestsPage from './pages/RequestsPage';
import NotificationsPage from './pages/NotificationsPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import { userAPI } from './services/api';

function ProtectedRoute({ children }) {
  const [isAuthenticated, setIsAuthenticated] = React.useState(null);

  React.useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }
      try {
        await userAPI.getProfile();
        setIsAuthenticated(true);
      } catch (e) {
        localStorage.removeItem('access_token');
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, []);

  if (isAuthenticated === null) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Загрузка...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <ThemeProvider>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/student" replace />} />
            <Route path="student/*" element={<StudentDashboard />} />
            <Route path="teacher/*" element={<TeacherDashboard />} />
            <Route path="admin/*" element={<AdminDashboard />} />
            <Route path="curator/*" element={<CuratorDashboard />} />
            <Route path="mck/*" element={<MckDashboard />} />
            
            <Route path="profile" element={<ProfilePage />} />
            <Route path="grades" element={<GradesPage />} />
            <Route path="practice" element={<PracticePage />} />
            <Route path="requests" element={<RequestsPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="change-password" element={<ChangePasswordPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}