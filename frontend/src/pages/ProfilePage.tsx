import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, Button, AppBar, Toolbar, Avatar, LinearProgress,
  Accordion, AccordionSummary, AccordionDetails, IconButton,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import { studentAPI, type UserProfile } from '../services/api';

const API_BASE_URL = 'http://localhost:8000';

export default function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await studentAPI.getProfile();
        setProfile(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки профиля');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ textAlign: 'center', mt: 10 }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка профиля...</Typography>
      </Container>
    );
  }

  if (error || !profile) {
    return (
      <Container maxWidth="md" sx={{ mt: 5 }}>
        <Alert severity="error">{error || 'Профиль не найден'}</Alert>
      </Container>
    );
  }

  const photoUrl = profile.photo_path ? `${API_BASE_URL}/media/${profile.photo_path}` : null;

  return (
    <>
      <AppBar position="sticky" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            🎓 Люберецкий техникум
          </Typography>
          <Typography sx={{ mr: 2 }}>{profile.user.full_name}</Typography>
          <IconButton onClick={handleLogout} color="inherit" title="Выйти">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3} alignItems="center">
              <Grid item>
                <Avatar
                  src={photoUrl || undefined}
                  sx={{ width: 120, height: 120, fontSize: 48 }}
                >
                  {profile.user.first_name[0]}{profile.user.last_name[0]}
                </Avatar>
              </Grid>
              <Grid item xs>
                <Typography variant="h5" fontWeight="bold">
                  {profile.user.full_name}
                </Typography>
                <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                  Группа: <strong>{profile.group_name}</strong> • {profile.age} лет • {profile.age_status}
                </Typography>
                <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={profile.status} color="success" size="small" />
                  <Chip label={`Анкета заполнена на ${profile.completion_percentage}%`} color="primary" size="small" />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={profile.completion_percentage}
                  sx={{ mt: 2, height: 8, borderRadius: 4 }}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">👤 Основная информация</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <InfoRow label="СНИЛС" value={profile.snils} />
              <InfoRow label="Email" value={profile.user.email} />
              <InfoRow label="Телефон" value={profile.phone} />
              <InfoRow label="ИНН" value={profile.inn || '—'} />
              <InfoRow label="Дата рождения" value={profile.birth_date} />
              <InfoRow label="Пол" value={profile.gender} />
              <InfoRow label="Место рождения" value={profile.birth_place} />
              <InfoRow label="Согласие на ПДн" value={profile.pd_consent ? '✅ Дано' : '❌ Не дано'} />
            </Grid>
          </AccordionDetails>
        </Accordion>

        {profile.passport && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">📄 Паспорт</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Серия и номер" value={profile.passport.series_number || '—'} />
                <InfoRow label="Дата выдачи" value={profile.passport.issue_date || '—'} />
                <InfoRow label="Кем выдан" value={profile.passport.issuer || '—'} />
                <InfoRow label="Код подразделения" value={profile.passport.unit_code || '—'} />
                <InfoRow label="Регион" value={profile.passport.region_city || '—'} />
                <InfoRow label="Адрес" value={profile.passport.address_detail || '—'} />
              </Grid>
              {profile.passport.file_path && (
                <Button
                  href={profile.passport.file_path}
                  target="_blank"
                  variant="outlined"
                  size="small"
                  sx={{ mt: 2 }}
                >
                  📎 Посмотреть скан
                </Button>
              )}
            </AccordionDetails>
          </Accordion>
        )}

        {profile.health && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🏥 Здоровье</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Состояние" value={profile.health.status} />
                <InfoRow label="Полис ОМС" value={profile.health.oms_number || '—'} />
                <InfoRow label="Выдан" value={profile.health.oms_issuer || '—'} />
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {profile.military && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🎖️ Воинский учёт</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Номер приписного" value={profile.military.registration_number || '—'} />
                <InfoRow label="Категория" value={profile.military.fitness_category || '—'} />
                <InfoRow label="Военкомат" value={profile.military.commissariat || '—'} />
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {profile.family && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">👨‍👩‍👧‍👦 Семья</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Статус" value={profile.family.status} />
                <InfoRow label="Тип жилья" value={profile.family.housing_type} />
                <InfoRow label="Несовершеннолетних" value={String(profile.family.minors_count ?? '—')} />
                <InfoRow label="Совершеннолетних" value={String(profile.family.adults_count ?? '—')} />
              </Grid>
              {profile.family.members?.length > 0 && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Члены семьи:</Typography>
                  {profile.family.members.map((member: any) => (
                    <Card key={member.id_member} variant="outlined" sx={{ mb: 1, p: 1 }}>
                      <Typography variant="body2">
                        <strong>{member.relation}:</strong> {member.full_name}
                      </Typography>
                      {member.phone && (
                        <Typography variant="caption" color="text.secondary">
                          📞 {member.phone}
                        </Typography>
                      )}
                    </Card>
                  ))}
                </>
              )}
            </AccordionDetails>
          </Accordion>
        )}

        {profile.education && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🎓 Предыдущее образование</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Учебное заведение" value={profile.education.name} />
                <InfoRow label="Тип" value={profile.education.type} />
                <InfoRow label="Профиль" value={profile.education.profile || '—'} />
                <InfoRow label="Год окончания" value={profile.education.graduation_date} />
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}

        {profile.profile && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">💼 Профиль</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <InfoRow label="Языки программирования" value={profile.profile.programming_langs || '—'} />
                <InfoRow label="Хобби" value={profile.profile.hobbies || '—'} />
                <InfoRow label="Доп. образование" value={profile.profile.extra_edu || '—'} />
                <InfoRow label="Спорт. разряды" value={profile.profile.sports_ranks || '—'} />
              </Grid>
            </AccordionDetails>
          </Accordion>
        )}
      </Container>
    </>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <Grid item xs={12} sm={6}>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body1">{value}</Typography>
    </Grid>
  );
}
