import { Outlet, useNavigate } from 'react-router-dom';
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
        if (savedRole && roles.includes(savedRole)) setActiveRole(savedRole);
        else if (roles.includes('admin')) setActiveRole('admin');
        else if (roles.includes('mck_chairman')) setActiveRole('mck_chairman');
        else if (roles.includes('teacher')) setActiveRole('teacher');
        else if (roles.includes('curator')) setActiveRole('curator');
        else setActiveRole(roles[0] || 'student');
      } catch (error) { navigate('/login'); }
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
              <button key={role.key} onClick={() => handleRoleSwitch(role.key)} style={{
                padding: '5px 10px', borderRadius: '4px', border: 'none', cursor: 'pointer',
                backgroundColor: activeRole === role.key ? '#ffffff' : '#1565c0',
                color: activeRole === role.key ? '#1976d2' : '#ffffff',
                fontWeight: activeRole === role.key ? 'bold' : 'normal',
              }}>{role.label}</button>
            ))}
          </div>
          <button onClick={() => { localStorage.clear(); navigate('/login'); }} style={{ padding: '5px 10px', borderRadius: '4px', border: '1px solid white', backgroundColor: 'transparent', color: 'white', cursor: 'pointer' }}>Выход</button>
        </div>
      </header>
      <main style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5' }}><Outlet /></main>
    </div>
  );
}
