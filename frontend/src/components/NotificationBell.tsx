import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  IconButton, Badge, Menu, MenuItem, Typography, Box, Button, Divider
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { notificationsAPI } from '../services/api';

interface Notification {
  id_notification: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await notificationsAPI.getList();
      const data = response.data;
      const allNotifications = Array.isArray(data) ? data : (data.results || []);
      setNotifications(allNotifications);
    } catch (err) {
      console.error('Ошибка загрузки уведомлений', err);
    }
  };

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    markAllAsRead();
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const markAllAsRead = async () => {
    const unread = notifications.filter(n => !n.is_read);
    if (unread.length === 0) return;
    
    try {
      await Promise.all(unread.map(n => notificationsAPI.markRead(n.id_notification)));
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Ошибка отметки прочтения', err);
    }
  };

  const handleViewAll = () => {
    handleClose();
    navigate('/student/notifications');
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const latestNotifications = notifications.slice(0, 3);

  return (
    <>
      <IconButton color="inherit" onClick={handleClick} size="large">
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{ sx: { width: 320, maxHeight: 400, overflow: 'auto' } }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1" fontWeight="bold">Уведомления</Typography>
          {unreadCount > 0 && (
            <Typography variant="caption" color="error" fontWeight="bold">
              {unreadCount} новых
            </Typography>
          )}
        </Box>
        <Divider />

        {latestNotifications.length === 0 ? (
          <MenuItem disabled>
            <Typography variant="body2" color="text.secondary">Нет новых уведомлений</Typography>
          </MenuItem>
        ) : (
          latestNotifications.map((notif) => (
            <MenuItem key={notif.id_notification} sx={{ flexDirection: 'column', alignItems: 'flex-start', py: 1.5 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mb: 0.5 }}>
                <Typography variant="body2" fontWeight={notif.is_read ? 'normal' : 'bold'}>
                  {notif.title}
                </Typography>
                {!notif.is_read && <Box sx={{ width: 8, height: 8, bgcolor: 'error.main', borderRadius: '50%' }} />}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5, lineHeight: 1.2 }}>
                {notif.message}
              </Typography>
              <Typography variant="caption" color="text.disabled">
                {new Date(notif.created_at).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
              </Typography>
            </MenuItem>
          ))
        )}

        <Divider />
        <Box sx={{ p: 1, display: 'flex', justifyContent: 'center' }}>
          <Button size="small" onClick={handleViewAll}>
            Посмотреть все
          </Button>
        </Box>
      </Menu>
    </>
  );
}
