import { useEffect, useState } from 'react';
import {
  Container, Typography, Card, CardContent, Box, CircularProgress, Chip, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction
} from '@mui/material';
import MarkEmailReadIcon from '@mui/icons-material/MarkEmailRead';
import { notificationsAPI } from '../services/api';

interface Notification {
  id_notification: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationsAPI.getList();
      const data = response.data;
      // Безопасно извлекаем массив
      const notificationsArray = Array.isArray(data) ? data : (data.results || []);
      setNotifications(notificationsArray);
    } catch (err) {
      console.error('Ошибка загрузки уведомлений', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await notificationsAPI.markRead(id);
      setNotifications(prev => prev.map(n => n.id_notification === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error('Ошибка отметки прочтения', err);
    }
  };

  if (loading) return <Box sx={{ textAlign: 'center', mt: 5 }}><CircularProgress /></Box>;

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <Container maxWidth="md" sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="bold">🔔 Уведомления</Typography>
        {unreadCount > 0 && <Chip label={`${unreadCount} непрочитанных`} color="error" />}
      </Box>

      {notifications.length === 0 ? (
        <Card><CardContent><Typography color="text.secondary">У вас нет новых уведомлений.</Typography></CardContent></Card>
      ) : (
        <Card variant="outlined">
          <List>
            {notifications.map((notif) => (
              <ListItem 
                key={notif.id_notification} 
                sx={{ 
                  bgcolor: notif.is_read ? 'transparent' : 'action.hover',
                  borderBottom: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" fontWeight={notif.is_read ? 'normal' : 'bold'}>
                        {notif.title}
                      </Typography>
                      {!notif.is_read && <Chip label="Новое" color="primary" size="small" />}
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" sx={{ mt: 0.5 }}>{notif.message}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(notif.created_at).toLocaleString('ru-RU')}
                      </Typography>
                    </>
                  }
                />
                {!notif.is_read && (
                  <ListItemSecondaryAction>
                    <IconButton edge="end" color="primary" onClick={() => handleMarkRead(notif.id_notification)} title="Отметить как прочитанное">
                      <MarkEmailReadIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>
        </Card>
      )}
    </Container>
  );
}
