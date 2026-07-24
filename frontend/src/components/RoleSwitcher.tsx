import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PersonIcon from '@mui/icons-material/Person';
import SchoolIcon from '@mui/icons-material/School';
import GroupsIcon from '@mui/icons-material/Groups';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import BusinessIcon from '@mui/icons-material/Business';

interface RoleSwitcherProps {
  roles: string[];
  currentRole: string;
  onRoleChange?: (role: string) => void;
}

const roleIcons: Record<string, JSX.Element> = {
  student: <PersonIcon fontSize="small" />,
  teacher: <SchoolIcon fontSize="small" />,
  curator: <GroupsIcon fontSize="small" />,
  admin: <AdminPanelSettingsIcon fontSize="small" />,
  mck_chairman: <BusinessIcon fontSize="small" />,
};

const roleNames: Record<string, string> = {
  student: 'Студент',
  teacher: 'Преподаватель',
  curator: 'Куратор',
  admin: 'Администратор',
  mck_chairman: 'МЦК',
};

const getDefaultRoute = (role: string) => {
  switch (role) {
    case 'admin': return '/admin/users';
    case 'mck_chairman': return '/mck/rpd';
    case 'teacher': return '/teacher/statements';
    case 'curator': return '/curator/group';
    case 'student': default: return '/student/profile';
  }
};

export default function RoleSwitcher({ roles, currentRole, onRoleChange }: RoleSwitcherProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleRoleChange = (newRole: string) => {
    localStorage.setItem('activeRole', newRole);
    
    if (onRoleChange) {
      onRoleChange(newRole);
    } else {
      navigate(getDefaultRoute(newRole));
    }
    
    handleClose();
  };

  return (
    <>
      <Button
        id="role-switcher-button"
        data-testid="role-switcher-button"
        aria-controls={open ? 'role-switcher-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        onClick={handleClick}
        endIcon={<ExpandMoreIcon />}
        sx={{ 
          color: 'inherit', 
          textTransform: 'none', 
          fontWeight: 'bold',
          borderColor: 'rgba(255, 255, 255, 0.5)',
          '&:hover': { borderColor: 'white', bgcolor: 'rgba(255, 255, 255, 0.1)' }
        }}
      >
        {roleNames[currentRole] || currentRole}
      </Button>
      <Menu
        id="role-switcher-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{ 'aria-labelledby': 'role-switcher-button' }}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        {roles.map((role) => (
          <MenuItem 
            key={role} 
            onClick={() => handleRoleChange(role)}
            selected={role === currentRole}
            sx={{ minWidth: 180 }}
          >
            <ListItemIcon sx={{ color: role === currentRole ? 'primary.main' : 'inherit' }}>
              {roleIcons[role] || <PersonIcon fontSize="small" />}
            </ListItemIcon>
            <ListItemText primary={roleNames[role] || role} />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
