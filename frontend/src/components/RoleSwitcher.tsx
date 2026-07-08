import { useState } from 'react';
import { Button, Menu, MenuItem, Typography } from '@mui/material';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';

export default function RoleSwitcher() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [activeRole, setActiveRole] = useState('student');

  const roles = [
    { id: 'student', label: '🎓 Студент' },
    // { id: 'curator', label: '👨‍🏫 Куратор' },
    // { id: 'teacher', label: '👨‍🏫 Преподаватель' },
  ];

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleRoleChange = (roleId: string) => {
    setActiveRole(roleId);
    handleClose();
  };

  const currentRole = roles.find(r => r.id === activeRole);

  return (
    <>
      <Button
        color="inherit"
        onClick={handleClick}
        endIcon={<ArrowDropDownIcon />}
        sx={{ textTransform: 'none' }}
      >
        <Typography variant="body2">
          Роль: <strong>{currentRole?.label}</strong>
        </Typography>
      </Button>
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
        {roles.map(role => (
          <MenuItem
            key={role.id}
            onClick={() => handleRoleChange(role.id)}
            selected={role.id === activeRole}
          >
            {role.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
