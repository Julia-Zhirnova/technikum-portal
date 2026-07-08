import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, Button, AppBar, Toolbar, Avatar, LinearProgress,
  Accordion, AccordionSummary, AccordionDetails, IconButton, Tabs, Tab,
  TextField, FormControlLabel, Checkbox,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { studentAPI, type UserProfile } from '../services/api';
import NotificationBell from '../components/NotificationBell';
import RoleSwitcher from '../components/RoleSwitcher';
import PracticePage from './PracticePage';
import GradesPage from './GradesPage';
import AttendancePage from './AttendancePage';
import RequestsPage from './RequestsPage';
import NotificationsPage from './NotificationsPage';

const API_BASE_URL = 'http://localhost:8000';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export default function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<any>({});

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await studentAPI.getProfile();
        setProfile(response.data);
        setEditedData(response.data);
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

  const handleSave = () => {
    // TODO: API запрос на сохранение
    setProfile(editedData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedData(profile);
    setIsEditing(false);
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
          <RoleSwitcher />
          <NotificationBell />
          <Typography sx={{ mx: 2 }}>{profile.user.full_name}</Typography>
          <IconButton onClick={handleLogout} color="inherit" title="Выйти">
            <LogoutIcon />
          </IconButton>
        </Toolbar>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} variant="scrollable">
          <Tab label="📋 Анкета" />
          <Tab label="💼 Практика" />
          <Tab label="📖 Зачётка" />
          <Tab label="📅 Посещаемость" />
          <Tab label="📨 Заявки" />
          <Tab label="🔔 Уведомления" />
        </Tabs>
      </AppBar>

      <TabPanel value={activeTab} index={0}>
        <Container maxWidth="md" sx={{ pb: 5, pt: 3 }}>
          {/* Шапка профиля */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item>
                  <Box sx={{ position: 'relative' }}>
                    <Avatar
                      src={photoUrl || undefined}
                      sx={{ width: 120, height: 120, fontSize: 48 }}
                    >
                      {profile.user.first_name[0]}{profile.user.last_name[0]}
                    </Avatar>
                    {isEditing && (
                      <IconButton
                        sx={{
                          position: 'absolute',
                          bottom: 0,
                          right: 0,
                          bgcolor: 'primary.main',
                          color: 'white',
                          '&:hover': { bgcolor: 'primary.dark' },
                        }}
                        size="small"
                      >
                        <PhotoCameraIcon />
                      </IconButton>
                    )}
                  </Box>
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
                    <Chip label={`Учебный план: ${profile.study_plan}`} size="small" variant="outlined" />
                    <Chip label={`Анкета: ${profile.completion_percentage}%`} color="primary" size="small" />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={profile.completion_percentage}
                    sx={{ mt: 2, height: 8, borderRadius: 4 }}
                  />
                </Grid>
                <Grid item>
                  {isEditing ? (
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSave}
                        color="success"
                      >
                        Сохранить
                      </Button>
                      <Button variant="outlined" onClick={handleCancel}>
                        Отмена
                      </Button>
                    </Box>
                  ) : (
                    <Button
                      variant="contained"
                      startIcon={<EditIcon />}
                      onClick={() => setIsEditing(true)}
                    >
                      Редактировать
                    </Button>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Блок 1.1: Основные документы */}
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">📎 Основные документы</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">СНИЛС (только чтение)</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1" sx={{ flexGrow: 1 }}>{profile.snils}</Typography>
                    <ScanButton filePath={profile.snils_file} />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Email</Typography>
                  <Typography variant="body1">{profile.user.email}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Телефон</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.phone || ''}
                      onChange={(e) => setEditedData({...editedData, phone: e.target.value})}
                    />
                  ) : (
                    <Typography variant="body1">{profile.phone}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">ИНН</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.inn || ''}
                        onChange={(e) => setEditedData({...editedData, inn: e.target.value})}
                      />
                    ) : (
                      <Typography variant="body1" sx={{ flexGrow: 1 }}>{profile.inn || '—'}</Typography>
                    )}
                    <ScanButton filePath={profile.inn_file} />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={profile.pd_consent}
                        disabled={!isEditing}
                      />
                    }
                    label={`Согласие на ПДн ${profile.pd_consent_date ? `(от ${profile.pd_consent_date})` : ''}`}
                  />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Блок 1.2: Паспорт */}
          {profile.passport && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">📄 Паспорт</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Серия и номер" value={profile.passport.series_number || '—'} editable={isEditing} />
                  <InfoRow label="Дата выдачи" value={profile.passport.issue_date || '—'} />
                  <InfoRow label="Кем выдан" value={profile.passport.issuer || '—'} editable={isEditing} />
                  <InfoRow label="Код подразделения" value={profile.passport.unit_code || '—'} editable={isEditing} />
                  <InfoRow label="Регион и город" value={profile.passport.region_city || '—'} editable={isEditing} />
                  <InfoRow label="Адрес регистрации" value={profile.passport.address_detail || '—'} editable={isEditing} />
                  <InfoRow label="Фактический адрес" value={profile.passport.fact_detail || '—'} editable={isEditing} />
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={<Checkbox checked={profile.passport.temp_reg} disabled={!isEditing} />}
                      label="Временная прописка"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <ScanButton filePath={profile.passport.file_path} label="Скан паспорта" />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.3: Здоровье */}
          {profile.health && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">🏥 Здоровье</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Состояние" value={profile.health.status} editable={isEditing} />
                  <InfoRow label="Полис ОМС" value={profile.health.oms_number || '—'} editable={isEditing} />
                  <InfoRow label="Дата выдачи ОМС" value={profile.health.oms_date || '—'} />
                  <InfoRow label="Кем выдан ОМС" value={profile.health.oms_issuer || '—'} editable={isEditing} />
                  <Grid item xs={12}>
                    <ScanButton filePath={profile.health.oms_scan} label="Скан полиса ОМС" />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.4: Воинский учёт */}
          {profile.military && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">🎖️ Воинский учёт</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Номер приписного" value={profile.military.registration_number || '—'} editable={isEditing} />
                  <InfoRow label="Категория годности" value={profile.military.fitness_category || '—'} />
                  <InfoRow label="Военкомат" value={profile.military.commissariat || '—'} editable={isEditing} />
                  <InfoRow label="Дата выдачи" value={profile.military.issue_date || '—'} />
                  <Grid item xs={12}>
                    <ScanButton filePath={profile.military.file_path} label="Скан приписного" />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.5: Семья */}
          {profile.family && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">👨‍👩‍👧‍👦 Семья</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Статус семьи" value={profile.family.status} editable={isEditing} />
                  <InfoRow label="Тип жилья" value={profile.family.housing_type} editable={isEditing} />
                  <InfoRow label="Несовершеннолетних" value={String(profile.family.minors_count ?? '—')} editable={isEditing} />
                  <InfoRow label="Совершеннолетних" value={String(profile.family.adults_count ?? '—')} editable={isEditing} />
                </Grid>
                {profile.family.members?.length > 0 && (
                  <>
                    <Typography variant="subtitle1" sx={{ mt: 3, mb: 1, fontWeight: 'bold' }}>
                      Члены семьи:
                    </Typography>
                    {profile.family.members.map((member: any) => (
                      <Card key={member.id_member} variant="outlined" sx={{ mb: 1, p: 2 }}>
                        <Grid container spacing={1}>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">Родство</Typography>
                            <Typography variant="body1" fontWeight="bold">{member.relation}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">ФИО</Typography>
                            <Typography variant="body1">{member.full_name}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">Дата рождения</Typography>
                            <Typography variant="body1">{member.birth_date || '—'}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">Телефон</Typography>
                            <Typography variant="body1">{member.phone || '—'}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">Образование</Typography>
                            <Typography variant="body1">{member.education || '—'}</Typography>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                            <Typography variant="body2" color="text.secondary">Место работы</Typography>
                            <Typography variant="body1">{member.workplace || '—'}</Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                              {member.is_pensioner && <Chip label="👴 Пенсионер" size="small" />}
                              {member.is_svo && <Chip label="🎖️ СВО" size="small" color="warning" />}
                              {member.is_priority_contact && <Chip label="⭐ Приоритетный контакт" size="small" color="primary" />}
                            </Box>
                          </Grid>
                        </Grid>
                      </Card>
                    ))}
                  </>
                )}
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.6: Предыдущее образование */}
          {profile.education && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">🎓 Предыдущее образование</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Учебное заведение" value={profile.education.name} editable={isEditing} />
                  <InfoRow label="Тип" value={profile.education.type} editable={isEditing} />
                  <InfoRow label="Профиль" value={profile.education.profile || '—'} editable={isEditing} />
                  <InfoRow label="Дата окончания" value={profile.education.graduation_date || '—'} />
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.7: Профиль */}
          {profile.profile && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">💼 Профиль и увлечения</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <InfoRow label="Языки программирования" value={profile.profile.programming_langs || '—'} editable={isEditing} />
                  <InfoRow label="Хобби" value={profile.profile.hobbies || '—'} editable={isEditing} />
                  <InfoRow label="Доп. образование" value={profile.profile.extra_edu || '—'} editable={isEditing} />
                  <InfoRow label="Спорт. разряды" value={profile.profile.sports_ranks || '—'} editable={isEditing} />
                  <InfoRow label="Характер" value={profile.profile.character_behavior || '—'} editable={isEditing} />
                </Grid>
                {profile.profile.foreign_langs?.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">Иностранные языки:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      {profile.profile.foreign_langs.map((lang: string, i: number) => (
                        <Chip key={i} label={lang} size="small" />
                      ))}
                    </Box>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          )}
        </Container>
      </TabPanel>

      <TabPanel value={activeTab} index={1}><PracticePage /></TabPanel>
      <TabPanel value={activeTab} index={2}><GradesPage /></TabPanel>
      <TabPanel value={activeTab} index={3}><AttendancePage /></TabPanel>
      <TabPanel value={activeTab} index={4}><RequestsPage /></TabPanel>
      <TabPanel value={activeTab} index={5}><NotificationsPage /></TabPanel>
    </>
  );
}

function InfoRow({ label, value, editable }: { label: string; value: string; editable?: boolean }) {
  return (
    <Grid item xs={12} sm={6}>
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      {editable ? (
        <TextField size="small" fullWidth defaultValue={value} />
      ) : (
        <Typography variant="body1">{value}</Typography>
      )}
    </Grid>
  );
}

function ScanButton({ filePath, label = 'Скан' }: { filePath: string | null; label?: string }) {
  if (!filePath) {
    return (
      <Button size="small" startIcon={<AttachFileIcon />} variant="outlined">
        Загрузить {label}
      </Button>
    );
  }
  return (
    <Button size="small" startIcon={<VisibilityIcon />} href={filePath} target="_blank">
      Просмотр
    </Button>
  );
}
