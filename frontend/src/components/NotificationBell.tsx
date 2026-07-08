import { useState } from 'react';
import { IconButton, Badge, Menu, MenuItem, Typography, Box } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';

export default function NotificationBell() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const unreadCount = 3; // TODO: получать из API

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{ sx: { width: 320, maxHeight: 400 } }}
      >
        <MenuItem onClick={handleClose}>
          <Box>
            <Typography variant="subtitle2" fontWeight="bold">
              Ваша заявка одобрена
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Справка об обучении готова
            </Typography>
          </Box>
        </MenuItem>
        <MenuItem onClick={handleClose}>
          <Box>
            <Typography variant="subtitle2">
              Новая оценка
            </Typography>
            <Typography variant="caption" color="text.secondary">
              МДК.01.01 — 5 (отлично)
            </Typography>
          </Box>
        </MenuItem>
        <MenuItem onClick={handleClose} sx={{ borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="body2" color="primary" sx={{ width: '100%', textAlign: 'center' }}>
            Все уведомления
          </Typography>
        </MenuItem>
      </Menu>
    </>
  );
}
