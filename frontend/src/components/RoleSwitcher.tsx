import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Menu, MenuItem, Typography } from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { authAPI } from '../services/api';

export default function RoleSwitcher() {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [activeRole, setActiveRole] = useState('student');
  const [userRoles, setUserRoles] = useState<string[]>([]);

  useEffect(() => {
    const loadRoles = async () => {
      try {
        const response = await authAPI.whoami();
        setUserRoles(response.data.roles);
        if (response.data.roles.length > 0) {
          setActiveRole(response.data.roles[0]);
        }
      } catch (err) {
        console.error('Ошибка загрузки ролей:', err);
      }
    };
    loadRoles();
  }, []);

  const roles = [
    { id: 'student', label: '🎓 Студент', path: '/profile' },
    { id: 'curator', label: '👨‍🏫 Куратор', path: '/curator' },
    { id: 'teacher', label: '👨‍🏫 Преподаватель', path: '/teacher' },
    { id: 'admin', label: '🔧 Администратор', path: '/admin' },
  ];

  const availableRoles = roles.filter(r => userRoles.includes(r.id));

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleRoleChange = (roleId: string, path: string) => {
    setActiveRole(roleId);
    handleClose();
    
    if (roleId === 'admin') {
      window.location.href = 'http://localhost:8000/admin/';
    } else {
      navigate(path);
    }
  };

  const currentRole = roles.find(r => r.id === activeRole);

  if (availableRoles.length <= 1) {
    return null; // Не показываем переключатель, если только одна роль
  }

  return (
    <>
      <Button
        color="inherit"
        onClick={handleClick}
        endIcon={<ArrowDropDownIcon />}
        sx={{ textTransform: 'none', mr: 2 }}
      >
        <Typography variant="body2">
          Роль: <strong>{currentRole?.label}</strong>
        </Typography>
      </Button>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        {availableRoles.map(role => (
          <MenuItem
            key={role.id}
            onClick={() => handleRoleChange(role.id, role.path)}
            selected={role.id === activeRole}
          >
            {role.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
