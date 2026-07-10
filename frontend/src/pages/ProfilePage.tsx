import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Grid, Chip, Box,
  CircularProgress, Alert, Button, AppBar, Toolbar, Avatar, LinearProgress,
  Accordion, AccordionSummary, AccordionDetails, IconButton, Tabs, Tab,
  TextField, FormControlLabel, Checkbox, Select, MenuItem, FormControl, InputLabel,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LogoutIcon from '@mui/icons-material/Logout';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import { studentAPI, referencesAPI, type UserProfile } from '../services/api';
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
  const [references, setReferences] = useState<any>({});

  useEffect(() => {
    const loadData = async () => {
      try {
        const [profileResponse, referencesResponse] = await Promise.all([
          studentAPI.getProfile(),
          referencesAPI.getReferences(),
        ]);
        setProfile(profileResponse.data);
        setEditedData(profileResponse.data);
        setReferences(referencesResponse.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Ошибка загрузки данных');
        if (err.response?.status === 401) {
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [navigate]);

  const handleSave = async () => {
    try {
      setLoading(true);
      await studentAPI.updateProfile(editedData);
      setProfile(editedData);
      setIsEditing(false);
      alert('✅ Данные успешно сохранены!');
    } catch (error: any) {
      console.error('❌ Ошибка сохранения:', error);
      console.error('📋 Детали ошибки:', error.response?.data);
      alert(`❌ Ошибка при сохранении: ${JSON.stringify(error.response?.data || error.message)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditedData(profile);
    setIsEditing(false);
  };

  if (loading && !profile) {
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
          <IconButton onClick={() => navigate('/login')} color="inherit" title="Выйти">
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
                  <Typography variant="body1">{profile.snils}</Typography>
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
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.inn || ''}
                      onChange={(e) => setEditedData({...editedData, inn: e.target.value})}
                    />
                  ) : (
                    <Typography variant="body1">{profile.inn || '—'}</Typography>
                  )}
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
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Серия и номер</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.passport?.series_number || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          passport: {...editedData.passport, series_number: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.passport.series_number || '—'}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Дата выдачи</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        type="date"
                        value={editedData.passport?.issue_date || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          passport: {...editedData.passport, issue_date: e.target.value}
                        })}
                        InputLabelProps={{ shrink: true }}
                      />
                    ) : (
                      <Typography variant="body1">{profile.passport.issue_date || '—'}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Кем выдан</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.passport?.issuer || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          passport: {...editedData.passport, issuer: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.passport.issuer || '—'}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Код подразделения</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.passport?.unit_code || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          passport: {...editedData.passport, unit_code: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.passport.unit_code || '—'}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Адрес регистрации</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.passport?.address_detail || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          passport: {...editedData.passport, address_detail: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.passport.address_detail || '—'}</Typography>
                    )}
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
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Состояние здоровья</Typography>
                    {isEditing ? (
                      <FormControl fullWidth size="small">
                        <Select
                          value={editedData.health?.status || ''}
                          onChange={(e) => setEditedData({
                            ...editedData,
                            health: {...editedData.health, status: e.target.value}
                          })}
                        >
                          {references.health_status?.map((option: any) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <Typography variant="body1">{profile.health.status}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Полис ОМС</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.health?.oms_number || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          health: {...editedData.health, oms_number: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.health.oms_number || '—'}</Typography>
                    )}
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
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Номер приписного</Typography>
                    {isEditing ? (
                      <TextField
                        size="small"
                        fullWidth
                        value={editedData.military?.registration_number || ''}
                        onChange={(e) => setEditedData({
                          ...editedData,
                          military: {...editedData.military, registration_number: e.target.value}
                        })}
                      />
                    ) : (
                      <Typography variant="body1">{profile.military.registration_number || '—'}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Категория годности</Typography>
                    {isEditing ? (
                      <FormControl fullWidth size="small">
                        <Select
                          value={editedData.military?.fitness_category || ''}
                          onChange={(e) => setEditedData({
                            ...editedData,
                            military: {...editedData.military, fitness_category: e.target.value}
                          })}
                        >
                          {references.fitness_category?.map((option: any) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <Typography variant="body1">{profile.military.fitness_category || '—'}</Typography>
                    )}
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
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Статус семьи</Typography>
                    {isEditing ? (
                      <FormControl fullWidth size="small">
                        <Select
                          value={editedData.family?.status || ''}
                          onChange={(e) => setEditedData({
                            ...editedData,
                            family: {...editedData.family, status: e.target.value}
                          })}
                        >
                          {references.family_status?.map((option: any) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <Typography variant="body1">{profile.family.status}</Typography>
                    )}
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Тип жилья</Typography>
                    {isEditing ? (
                      <FormControl fullWidth size="small">
                        <Select
                          value={editedData.family?.housing_type || ''}
                          onChange={(e) => setEditedData({
                            ...editedData,
                            family: {...editedData.family, housing_type: e.target.value}
                          })}
                        >
                          {references.housing_type?.map((option: any) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    ) : (
                      <Typography variant="body1">{profile.family.housing_type}</Typography>
                    )}
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Блок 1.6: Образование */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">🎓 Предыдущее образование</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Учебное заведение</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.education?.name || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        education: {...editedData.education, name: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.education?.name || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Тип заведения</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.education?.type || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        education: {...editedData.education, type: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.education?.type || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Профиль класса</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.education?.profile || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        education: {...editedData.education, profile: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.education?.profile || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Дата окончания</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      type="date"
                      value={editedData.education?.graduation_date || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        education: {...editedData.education, graduation_date: e.target.value}
                      })}
                      InputLabelProps={{ shrink: true }}
                    />
                  ) : (
                    <Typography variant="body1">{profile.education?.graduation_date || '—'}</Typography>
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Блок 1.7: Профиль студента */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">💼 Профиль и интересы</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Языки программирования</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      multiline
                      rows={2}
                      value={editedData.profile?.programming_langs || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        profile: {...editedData.profile, programming_langs: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.profile?.programming_langs || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Хобби и увлечения</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      multiline
                      rows={3}
                      value={editedData.profile?.hobbies || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        profile: {...editedData.profile, hobbies: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.profile?.hobbies || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Дополнительное образование</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      multiline
                      rows={2}
                      value={editedData.profile?.extra_edu || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        profile: {...editedData.profile, extra_edu: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.profile?.extra_edu || '—'}</Typography>
                  )}
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Спортивные разряды</Typography>
                  {isEditing ? (
                    <TextField
                      size="small"
                      fullWidth
                      value={editedData.profile?.sports_ranks || ''}
                      onChange={(e) => setEditedData({
                        ...editedData,
                        profile: {...editedData.profile, sports_ranks: e.target.value}
                      })}
                    />
                  ) : (
                    <Typography variant="body1">{profile.profile?.sports_ranks || '—'}</Typography>
                  )}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
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
