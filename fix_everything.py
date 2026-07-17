import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Role, UserRole

print("🔧 Начинаю исправление файлов...")

# 1. Исправляем accounts/serializers.py
serializer_code = """from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        from core.models import UserRole
        roles = list(UserRole.objects.filter(user=user).values_list('role__id_role', flat=True))
        token['roles'] = roles
        token['requires_password_change'] = user.requires_password_change
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            data['requires_password_change'] = self.user.requires_password_change
            return data
        except AuthenticationFailed as e:
            error_msg = str(e).lower()
            if "active" in error_msg or "no active account" in error_msg:
                raise AuthenticationFailed(_("Ваша учетная запись заблокирована. Обратитесь к администратору."))
            raise e
"""
with open('accounts/serializers.py', 'w', encoding='utf-8') as f:
    f.write(serializer_code)
print("✅ accounts/serializers.py исправлен")

# 2. Исправляем frontend/src/App.tsx
app_code = """import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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

const theme = createTheme({
  palette: { primary: { main: '#1976d2' }, secondary: { main: '#dc004e' } },
});

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
      if (!token) {
        setRedirect('/login');
        setLoading(false);
        return;
      }

      try {
        const response = await userAPI.getProfile();
        const roles = response.data.roles || [];
        const requiresPasswordChange = response.data.requires_password_change;
        
        console.log('DEBUG: Роли:', roles, 'Смена пароля:', requiresPasswordChange);

        if (requiresPasswordChange) {
          setRedirect('/change-password');
          setLoading(false);
          return;
        }

        if (roles.includes('admin')) setRedirect('/admin');
        else if (roles.includes('mck_chairman')) setRedirect('/mck');
        else if (roles.includes('teacher')) setRedirect('/teacher');
        else if (roles.includes('curator')) setRedirect('/curator');
        else if (roles.includes('student')) setRedirect('/student');
        else setRedirect('/login');
      } catch (error: any) {
        console.error('Ошибка проверки роли:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setRedirect('/login');
      } finally {
        setLoading(false);
      }
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
"""
with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(app_code)
print("✅ frontend/src/App.tsx исправлен")

# 3. Исправляем frontend/src/components/DashboardLayout.tsx
layout_code = """import { Outlet, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { userAPI } from '../services/api';

export default function DashboardLayout() {
  const navigate = useNavigate();
  const [userRoles, setUserRoles] = useState<string[]>([]);
  const [activeRole, setActiveRole] = useState<string>('');

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await userAPI.getProfile();
        const roles = response.data.roles || [];
        setUserRoles(roles);
        
        const savedRole = localStorage.getItem('activeRole');
        if (savedRole && roles.includes(savedRole)) {
          setActiveRole(savedRole);
        } else if (roles.includes('admin')) {
          setActiveRole('admin');
        } else if (roles.includes('mck_chairman')) {
          setActiveRole('mck_chairman');
        } else if (roles.includes('teacher')) {
          setActiveRole('teacher');
        } else if (roles.includes('curator')) {
          setActiveRole('curator');
        } else {
          setActiveRole(roles[0] || 'student');
        }
      } catch (error) {
        navigate('/login');
      }
    };
    fetchUser();
  }, [navigate]);

  const handleRoleSwitch = (role: string) => {
    setActiveRole(role);
    localStorage.setItem('activeRole', role);
    if (role === 'admin') navigate('/admin');
    else if (role === 'mck_chairman') navigate('/mck');
    else if (role === 'teacher') navigate('/teacher');
    else if (role === 'curator') navigate('/curator');
    else navigate('/student');
  };

  const roleButtons = [];
  if (userRoles.includes('admin')) roleButtons.push({ key: 'admin', label: 'Администратор' });
  if (userRoles.includes('mck_chairman')) roleButtons.push({ key: 'mck_chairman', label: 'Председатель МЦК' });
  if (userRoles.includes('teacher')) roleButtons.push({ key: 'teacher', label: 'Преподаватель' });
  if (userRoles.includes('curator')) roleButtons.push({ key: 'curator', label: 'Куратор' });
  if (userRoles.includes('student')) roleButtons.push({ key: 'student', label: 'Студент' });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <header style={{ backgroundColor: '#1976d2', color: 'white', padding: '10px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>Люберецкий техникум</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ display: 'flex', gap: '5px' }}>
            {roleButtons.map((role) => (
              <button
                key={role.key}
                onClick={() => handleRoleSwitch(role.key)}
                style={{
                  padding: '5px 10px', borderRadius: '4px', border: 'none', cursor: 'pointer',
                  backgroundColor: activeRole === role.key ? '#ffffff' : '#1565c0',
                  color: activeRole === role.key ? '#1976d2' : '#ffffff',
                  fontWeight: activeRole === role.key ? 'bold' : 'normal',
                }}
              >
                {role.label}
              </button>
            ))}
          </div>
          <button onClick={() => { localStorage.clear(); navigate('/login'); }} style={{ padding: '5px 10px', borderRadius: '4px', border: '1px solid white', backgroundColor: 'transparent', color: 'white', cursor: 'pointer' }}>
            Выход
          </button>
        </div>
      </header>
      <main style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5' }}>
        <Outlet />
      </main>
    </div>
  );
}
"""
with open('frontend/src/components/DashboardLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(layout_code)
print("✅ frontend/src/components/DashboardLayout.tsx исправлен")

# 4. Создаем тестовых пользователей
User = get_user_model()

u1, _ = User.objects.get_or_create(email='test_password_change@luberteh.ru')
u1.set_password('OldPassword123!')
u1.requires_password_change = True
u1.is_active = True
u1.save()
r1, _ = Role.objects.get_or_create(id_role='student', defaults={'name': 'Студент'})
UserRole.objects.get_or_create(user=u1, role=r1)
print("✅ Пользователь для смены пароля создан/обновлен")

u2, _ = User.objects.get_or_create(email='blocked_user@luberteh.ru')
u2.set_password('Password123!')
u2.is_active = False
u2.requires_password_change = False
u2.save()
UserRole.objects.get_or_create(user=u2, role=r1)
print("✅ Заблокированный пользователь создан/обновлен")

print("\n🎉 ВСЁ ИСПРАВЛЕНО! Можете закрывать этот файл и перезапускать серверы.")
