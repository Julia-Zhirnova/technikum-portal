import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './ThemeContext';
import CssBaseline from '@mui/material/CssBaseline';

// Страницы
import LoginPage from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import ProfilePage from './pages/ProfilePage';
import PassportPage from './pages/PassportPage';
import HealthPage from './pages/HealthPage';
import CuratorDashboard from './pages/CuratorDashboard';
import CuratorRequestsPage from './pages/CuratorRequestsPage';
import TeacherDashboard from './pages/TeacherDashboard';
import TeacherPracticePage from './pages/TeacherPracticePage';
import RequestsPage from './pages/RequestsPage';
import NotificationsPage from './pages/NotificationsPage';
import PracticePage from './pages/PracticePage';
import GradesPage from './pages/GradesPage';
import ComingSoonPage from './pages/ComingSoonPage';
import AccessDeniedPage from './pages/AccessDeniedPage';

import DashboardLayout from './components/DashboardLayout';

function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

function SmartRedirect() {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" replace />;

  const payload = parseJwt(token);
  if (payload && payload.requires_password_change === true) {
    return <Navigate to="/change-password" replace />;
  }

  let targetPath = '/student/profile';
  if (payload && payload.roles && Array.isArray(payload.roles)) {
    const roles = payload.roles;
    // БП 1.1.3: если ролей нет → редирект на /access-denied
    if (roles.length === 0 || payload.no_roles === true) {
      return <Navigate to="/access-denied" replace />;
    }
    if (roles.includes('admin')) targetPath = '/admin/users';
    else if (roles.includes('mck_chairman')) targetPath = '/mck/rpd';
    else if (roles.includes('teacher')) targetPath = '/teacher/statements';
    else if (roles.includes('curator')) targetPath = '/curator/group';
    else if (roles.includes('student')) targetPath = '/student/profile';
  } else {
    // Ролей нет вообще — редирект на /access-denied
    return <Navigate to="/access-denied" replace />;
  }

  return <Navigate to={targetPath} replace />;
}

function App() {
  return (
    <ThemeProvider>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          <Route path="/access-denied" element={<AccessDeniedPage />} />
          <Route path="/" element={<SmartRedirect />} />
          
          <Route element={<DashboardLayout />}>
            {/* === СТУДЕНТ === */}
            <Route path="/student/profile" element={<ProfilePage />} />
            <Route path="/student" element={<Navigate to="/student/profile" replace />} /> {/* <-- ДОБАВЛЕНО */}
            <Route path="/student/passport" element={<PassportPage />} />
            <Route path="/student/health" element={<HealthPage />} />
            <Route path="/student/grades" element={<GradesPage />} />
            <Route path="/student/practice" element={<PracticePage />} />
            <Route path="/student/requests" element={<RequestsPage />} />
            <Route path="/student/notifications" element={<NotificationsPage />} />
            <Route path="/student/*" element={<ComingSoonPage />} />

            {/* === ПРЕПОДАВАТЕЛЬ === */}
            <Route path="/teacher/statements" element={<TeacherDashboard />} />
            <Route path="/teacher/schedule" element={<ComingSoonPage />} />
            <Route path="/teacher/practice" element={<TeacherPracticePage />} />
            <Route path="/teacher/rpd" element={<ComingSoonPage />} />
            <Route path="/teacher/*" element={<ComingSoonPage />} />

            {/* === КУРАТОР === */}
            <Route path="/curator/group" element={<CuratorDashboard />} />
            <Route path="/curator/grades" element={<ComingSoonPage />} />
            <Route path="/curator/attendance" element={<ComingSoonPage />} />
            <Route path="/curator/schedule" element={<ComingSoonPage />} />
            <Route path="/curator/requests" element={<CuratorRequestsPage />} />
            <Route path="/curator/*" element={<ComingSoonPage />} />

            {/* === АДМИНИСТРАТОР === */}
            <Route path="/admin/users" element={<ComingSoonPage />} />
            <Route path="/admin/references" element={<ComingSoonPage />} />
            <Route path="/admin/*" element={<ComingSoonPage />} />

            {/* === МЦК === */}
            <Route path="/mck/rpd" element={<ComingSoonPage />} />
            <Route path="/mck/monitoring" element={<ComingSoonPage />} />
            <Route path="/mck/protocols" element={<ComingSoonPage />} />
            <Route path="/mck/*" element={<ComingSoonPage />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
