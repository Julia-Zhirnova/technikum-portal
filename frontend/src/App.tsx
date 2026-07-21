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
import AdminDashboard from './pages/AdminDashboard';
import MckDashboard from './pages/MckDashboard';

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

// Компонент умного редиректа после входа
function SmartRedirect() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const payload = parseJwt(token);
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

  // Если требуется смена пароля
  if (payload && payload.requires_password_change === true) {
    return <Navigate to="/change-password" replace />;
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
          
          {/* Корневой путь — если есть токен, идем на /student, иначе на /login */}
          <Route path="/" element={<SmartRedirect />} />
          
          {/* Защищенные маршруты внутри DashboardLayout */}
          <Route element={<DashboardLayout />}>
            <Route path="/change-password" element={<ChangePasswordPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            
            <Route path="/admin/*" element={<AdminDashboard />} />
            <Route path="/mck/*" element={<MckDashboard />} />
            <Route path="/curator/*" element={<CuratorDashboard />} />
            <Route path="/curator/requests" element={<CuratorRequestsPage />} />
            <Route path="/teacher/*" element={<TeacherDashboard />} />
            <Route path="/teacher/practice" element={<TeacherPracticePage />} />
            <Route path="/student/*" element={<StudentDashboard />} />
            <Route path="/student/grades" element={<GradesPage />} />
            <Route path="/student/practice" element={<PracticePage />} />
            <Route path="/student/requests" element={<RequestsPage />} />
            <Route path="/student/notifications" element={<NotificationsPage />} />
          </Route>
          
          {/* Все остальные пути — на логин */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
