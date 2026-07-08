import { useEffect, useState } from 'react';
import { Container, Typography, Card, CardContent, Grid, Chip, Box, CircularProgress, Alert } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import axios from 'axios';

interface StudentProfile {
  snils: string;
  user_full_name: string;
  group_name: string;
  birth_date: string;
  gender: string;
  birth_place: string;
  phone: string;
  inn: string | null;
  status: string;
  passport: {
    series_number: string;
    issue_date: string;
    issuer: string;
    unit_code: string;
  } | null;
  health: {
    status: string;
    oms_number: string;
    oms_issuer: string;
  } | null;
  military: {
    registration_number: string;
    fitness_category: string;
    commissariat: string;
  } | null;
  family: {
    status: string;
    housing_type: string;
  } | null;
  profile: {
    it_skills: any;
    programming_langs: string;
    hobbies: string;
  } | null;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Пока что используем тестовые данные, позже добавим авторизацию
    const testProfile: StudentProfile = {
      snils: '123-456-789 00',
      user_full_name: 'Иванов Иван Иванович',
      group_name: 'ИС-24',
      birth_date: '2007-01-01',
      gender: 'мужской',
      birth_place: 'Москва',
      phone: '89991234567',
      inn: '123456789012',
      status: 'обучается (студент)',
      passport: {
        series_number: '4619 123456',
        issue_date: '2023-01-15',
        issuer: 'ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ',
        unit_code: '500-066'
      },
      health: {
        status: 'здоров',
        oms_number: '5999000999000999',
        oms_issuer: 'ЗАО "МАКС-М" Московской области'
      },
      military: {
        registration_number: 'СА №1239900',
        fitness_category: 'А',
        commissariat: 'Военный комиссариат г. Люберцы'
      },
      family: {
        status: 'полная',
        housing_type: 'в_собственном_жилье_с_родителями'
      },
      profile: {
        it_skills: ['программирование', 'создание сайтов'],
        programming_langs: 'Python, JavaScript',
        hobbies: 'Спорт, чтение'
      }
    };
    
    setProfile(testProfile);
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ pb: 10, pt: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка профиля...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!profile) {
    return (
      <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
        <Alert severity="warning">Профиль не найден</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ pb: 10, pt: 3 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <PersonIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          Мой профиль
        </Typography>
        <Chip label={profile.status} color="primary" sx={{ mt: 1 }} />
      </Box>

      {/* Основная информация */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>👤 Основная информация</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">ФИО</Typography>
              <Typography variant="body1" fontWeight="bold">{profile.user_full_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">Группа</Typography>
              <Typography variant="body1" fontWeight="bold">{profile.group_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">Дата рождения</Typography>
              <Typography variant="body1">{profile.birth_date}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">Место рождения</Typography>
              <Typography variant="body1">{profile.birth_place}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">Телефон</Typography>
              <Typography variant="body1">{profile.phone}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">СНИЛС</Typography>
              <Typography variant="body1">{profile.snils}</Typography>
            </Grid>
            {profile.inn && (
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">ИНН</Typography>
                <Typography variant="body1">{profile.inn}</Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Паспорт */}
      {profile.passport && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>📄 Паспорт</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Серия и номер</Typography>
                <Typography variant="body1">{profile.passport.series_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Дата выдачи</Typography>
                <Typography variant="body1">{profile.passport.issue_date}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Кем выдан</Typography>
                <Typography variant="body1">{profile.passport.issuer}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Код подразделения</Typography>
                <Typography variant="body1">{profile.passport.unit_code}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Здоровье */}
      {profile.health && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>🏥 Здоровье</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Состояние</Typography>
                <Typography variant="body1">{profile.health.status}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Номер полиса ОМС</Typography>
                <Typography variant="body1">{profile.health.oms_number}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Кем выдан полис</Typography>
                <Typography variant="body1">{profile.health.oms_issuer}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Воинский учет */}
      {profile.military && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>🎖️ Воинский учет</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Номер приписного</Typography>
                <Typography variant="body1">{profile.military.registration_number}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Категория годности</Typography>
                <Typography variant="body1">{profile.military.fitness_category}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Военкомат</Typography>
                <Typography variant="body1">{profile.military.commissariat}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Семья */}
      {profile.family && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>👨‍👩‍👧‍👦 Семья</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Статус семьи</Typography>
                <Typography variant="body1">{profile.family.status}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Тип жилья</Typography>
                <Typography variant="body1">{profile.family.housing_type}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Профиль */}
      {profile.profile && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>💼 Профиль</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">IT-навыки</Typography>
                <Typography variant="body1">
                  {Array.isArray(profile.profile.it_skills) 
                    ? profile.profile.it_skills.join(', ') 
                    : '—'}
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Языки программирования</Typography>
                <Typography variant="body1">{profile.profile.programming_langs || '—'}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">Хобби</Typography>
                <Typography variant="body1">{profile.profile.hobbies || '—'}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Container>
  );
}
