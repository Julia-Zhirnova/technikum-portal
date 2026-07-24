import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './ThemeContext';
import CssBaseline from '@mui/material/CssBaseline';

// Страницы
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
import ComingSoonPage from './pages/ComingSoonPage';

import DashboardLayout from './components/DashboardLayout';

// Функция для безопасного декодирования JWT payload
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

// Компонент умного редиректа после входа (1.2.1)
function SmartRedirect() {
  const token = localStorage.getItem('access_token');
  
  // Проверяем, что токен существует и содержит requires_password_change
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const payload = parseJwt(token);
  
  // 1.2.1: Приоритетная проверка флага смены пароля
  if (payload && payload.requires_password_change === true) {
    return <Navigate to="/change-password" replace />;
  }

  let targetPath = '/student/profile'; // Дефолтный путь

  if (payload && payload.roles && Array.isArray(payload.roles)) {
    const roles = payload.roles;
    // Приоритет ролей: admin > mck_chairman > teacher > curator > student
    if (roles.includes('admin')) targetPath = '/admin/users';
    else if (roles.includes('mck_chairman')) targetPath = '/mck/rpd';
    else if (roles.includes('teacher')) targetPath = '/teacher/statements';
    else if (roles.includes('curator')) targetPath = '/curator/group';
    else if (roles.includes('student')) targetPath = '/student/profile';
  }

  return <Navigate to={targetPath} replace />;
}

function App() {
  return (
    <ThemeProvider>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Публичные маршруты */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/change-password" element={<ChangePasswordPage />} />
          
          {/* Корневой путь — умный редирект */}
          <Route path="/" element={<SmartRedirect />} />
          
          {/* Защищенные маршруты внутри DashboardLayout */}
          <Route element={<DashboardLayout />}>
            {/* === СТУДЕНТ === */}
            <Route path="/student/profile" element={<ProfilePage />} />
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
          
          {/* Все остальные пути — на логин */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
