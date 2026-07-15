import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, Typography, Card, CardContent, Chip, Box,
  CircularProgress, Alert, AppBar, Toolbar, IconButton, Table,
  TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Button, Select, MenuItem, FormControl, InputLabel, Dialog,
  DialogTitle, DialogContent, DialogActions, Menu,
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import EditIcon from '@mui/icons-material/Edit';
import RestoreIcon from '@mui/icons-material/Restore';
import LockIcon from '@mui/icons-material/Lock';
import DownloadIcon from '@mui/icons-material/Download';
import UploadIcon from '@mui/icons-material/Upload';
import DescriptionIcon from '@mui/icons-material/Description';
import { teacherAPI } from '../services/api';
import RoleSwitcher from '../components/RoleSwitcher';

interface Statement {
  id_statement: number;
  number: string;
  group_name: string;
  discipline_name: string;
  status: string;
  issue_date: string;
  students_count: number;
}

interface Grade {
  id_grade: number;
  student_snils: string;
  student_name: string;
  grade: string;
  date: string;
  is_retake: boolean;
}

export default function TeacherDashboard() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statements, setStatements] = useState<Statement[]>([]);
  const [selectedStatement, setSelectedStatement] = useState<Statement | null>(null);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [gradesLoading, setGradesLoading] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingGrade, setEditingGrade] = useState<Grade | null>(null);
  const [newGradeValue, setNewGradeValue] = useState('');
  const [saving, setSaving] = useState(false);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);
  const [docxMenuAnchor, setDocxMenuAnchor] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadStatements();
  }, []);

  const loadStatements = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getStatements();
      const data = response.data.results || response.data;
      setStatements(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки ведомостей');
      setStatements([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStatement = async (statement: Statement) => {
    setSelectedStatement(statement);
    setGradesLoading(true);
    setError(null);
    
    try {
      const response = await teacherAPI.getStatementGrades(statement.id_statement);
      setGrades(Array.isArray(response.data) ? response.data : []);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Ошибка загрузки оценок');
      setGrades([]);
    } finally {
      setGradesLoading(false);
    }
  };

  const normalizeGradeValue = (grade: string): string => {
    const gradeMap: Record<string, string> = {
      'Зачтено': 'зачтено',
      'Не зачтено': 'не_зачтено',
      'Неудовлетворительно': '2 (неудовлетворительно)',
      'Удовлетворительно': '3 (удовлетворительно)',
      'Хорошо': '4 (хорошо)',
      'Отлично': '5 (отлично)',
    };
    return gradeMap[grade] || grade;
  };

  const handleEditGrade = (grade: Grade) => {
    setEditingGrade(grade);
    setNewGradeValue(normalizeGradeValue(grade.grade || ''));
    setEditDialogOpen(true);
  };

  const handleSaveGrade = async () => {
    if (!editingGrade) return;
    
    try {
      setSaving(true);
      await teacherAPI.updateGrade(editingGrade.id_grade, { grade: newGradeValue });
      setEditDialogOpen(false);
      if (selectedStatement) {
        const response = await teacherAPI.getStatementGrades(selectedStatement.id_statement);
        setGrades(Array.isArray(response.data) ? response.data : []);
      }
      alert('✅ Оценка сохранена');
    } catch (err: any) {
      alert('❌ ' + (err.response?.data?.error || err.message));
    } finally {
      setSaving(false);
    }
  };

  const handleRestoreStatement = async (statementId: number) => {
    if (!confirm('Вернуть ведомость в работу?')) return;
    try {
      await teacherAPI.restoreStatement(statementId);
      await loadStatements();
      alert('✅ Ведомость возвращена в работу');
    } catch (err: any) {
      alert('❌ ' + (err.response?.data?.error || err.message));
    }
  };

  const handleExport = async (format: string) => {
    if (!selectedStatement) return;
    setExportMenuAnchor(null);
    
    try {
      const response = await teacherAPI.exportGrades(selectedStatement.id_statement, format);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const ext = format === 'excel' ? 'xlsx' : format;
      link.download = `${selectedStatement.number}.${ext}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('❌ Ошибка экспорта: ' + (err.message || 'Неизвестная ошибка'));
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedStatement) return;
    
    try {
      const response = await teacherAPI.importGrades(selectedStatement.id_statement, file);
      let msg = '✅ ' + response.data.message;
      if (response.data.errors && response.data.errors.length > 0) {
        msg += '\n\nОшибки:\n' + response.data.errors.join('\n');
      }
      alert(msg);
      // Перезагружаем оценки
      const gradesResponse = await teacherAPI.getStatementGrades(selectedStatement.id_statement);
      setGrades(Array.isArray(gradesResponse.data) ? gradesResponse.data : []);
    } catch (err: any) {
      alert('❌ Ошибка импорта: ' + (err.response?.data?.error || err.message));
    }
    
    // Очищаем input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGenerateDocx = async (type: string) => {
    if (!selectedStatement) return;
    setDocxMenuAnchor(null);
    
    try {
      const response = await teacherAPI.generateDocx(selectedStatement.id_statement, type);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const docName = type === 'protocol' ? 'Протокол' : 'Зачетная_ведомость';
      link.download = `${docName}_${selectedStatement.number}.docx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('❌ Ошибка генерации: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  const canEdit = (status: string): boolean => {
    return status === 'в_работе';
  };

  const getGradeColor = (grade: string): any => {
    if (!grade) return 'default';
    const g = grade.toLowerCase();
    if (g.includes('5') || g.includes('отлично') || g === 'зачтено') return 'success';
    if (g.includes('4') || g.includes('хорошо')) return 'primary';
    if (g.includes('3') || g.includes('удовлетворительно')) return 'warning';
    if (g.includes('2') || g.includes('неудовлетворительно') || g === 'не_зачтено' || g.includes('не зачтено')) return 'error';
    return 'default';
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', mt: 10 }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Загрузка...</Typography>
      </Box>
    );
  }

  return (
    <>

      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          📋 Мои ведомости
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept=".xlsx,.csv"
          onChange={handleFileChange}
        />

        <Box sx={{ display: 'flex', gap: 3 }}>
          {/* Список ведомостей */}
          <Box sx={{ width: '380px', flexShrink: 0 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ведомости ({statements.length})
                </Typography>
                <Box sx={{ maxHeight: '75vh', overflow: 'auto' }}>
                  {statements.map((stmt) => (
                    <Card
                      key={stmt.id_statement}
                      sx={{
                        mb: 1,
                        cursor: 'pointer',
                        bgcolor: selectedStatement?.id_statement === stmt.id_statement ? 'primary.light' : 'background.paper',
                        '&:hover': { bgcolor: 'action.hover' },
                      }}
                      onClick={() => handleSelectStatement(stmt)}
                    >
                      <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {stmt.number}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {stmt.group_name} • {stmt.discipline_name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                          <Chip
                            label={stmt.status === 'в_работе' ? 'В работе' : stmt.status === 'закрыта' ? 'Закрыта' : stmt.status}
                            size="small"
                            color={stmt.status === 'в_работе' ? 'success' : stmt.status === 'закрыта' ? 'warning' : 'default'}
                          />
                          {canEdit(stmt.status) && (
                            <Chip label="✏️ Можно редактировать" size="small" color="success" variant="outlined" />
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Box>

          {/* Таблица оценок */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            {selectedStatement ? (
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                    <Box>
                      <Typography variant="h6">
                        {selectedStatement.number} — {selectedStatement.discipline_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Группа: {selectedStatement.group_name} | Статус: {selectedStatement.status} | Оценок: {grades.length}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {/* Кнопки экспорта */}
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<DownloadIcon />}
                        onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                      >
                        Экспорт
                      </Button>
                      <Menu
                        anchorEl={exportMenuAnchor}
                        open={Boolean(exportMenuAnchor)}
                        onClose={() => setExportMenuAnchor(null)}
                      >
                        <MenuItem onClick={() => handleExport('excel')}>📊 Excel (.xlsx)</MenuItem>
                        <MenuItem onClick={() => handleExport('csv')}>📄 CSV (.csv)</MenuItem>
                        <MenuItem onClick={() => handleExport('txt')}>📝 TXT (.txt)</MenuItem>
                      </Menu>

                      {/* Кнопка импорта */}
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<UploadIcon />}
                        onClick={handleImportClick}
                        disabled={!canEdit(selectedStatement.status)}
                      >
                        Импорт
                      </Button>

                      {/* Кнопка генерации DOCX */}
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<DescriptionIcon />}
                        onClick={(e) => setDocxMenuAnchor(e.currentTarget)}
                      >
                        Документ
                      </Button>
                      <Menu
                        anchorEl={docxMenuAnchor}
                        open={Boolean(docxMenuAnchor)}
                        onClose={() => setDocxMenuAnchor(null)}
                      >
                        <MenuItem onClick={() => handleGenerateDocx('zachet')}>📋 Зачетная ведомость</MenuItem>
                        <MenuItem onClick={() => handleGenerateDocx('protocol')}>📝 Протокол экзамена</MenuItem>
                      </Menu>

                      {canEdit(selectedStatement.status) ? (
                        <Chip label="✏️ Режим редактирования" color="success" icon={<EditIcon />} />
                      ) : (
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<RestoreIcon />}
                          onClick={() => handleRestoreStatement(selectedStatement.id_statement)}
                        >
                          Вернуть в работу
                        </Button>
                      )}
                    </Box>
                  </Box>

                  {gradesLoading ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <CircularProgress />
                      <Typography sx={{ mt: 2 }}>Загрузка оценок...</Typography>
                    </Box>
                  ) : grades.length === 0 ? (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      Нет оценок для этой ведомости
                    </Alert>
                  ) : (
                    <TableContainer component={Paper} variant="outlined" sx={{ mt: 2, maxHeight: '65vh' }}>
                      <Table stickyHeader size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>№</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>ФИО студента</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>СНИЛС</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>Оценка</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>Дата</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>Пересдача</TableCell>
                            <TableCell sx={{ bgcolor: 'grey.200', fontWeight: 'bold' }}>Действия</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {grades.map((grade, idx) => (
                            <TableRow key={grade.id_grade || idx} hover>
                              <TableCell>{idx + 1}</TableCell>
                              <TableCell>{grade.student_name}</TableCell>
                              <TableCell>{grade.student_snils}</TableCell>
                              <TableCell>
                                <Chip
                                  label={grade.grade || '—'}
                                  size="small"
                                  color={getGradeColor(grade.grade)}
                                />
                              </TableCell>
                              <TableCell>{grade.date || '—'}</TableCell>
                              <TableCell>
                                <Chip
                                  label={grade.is_retake ? 'Да' : 'Нет'}
                                  size="small"
                                  color={grade.is_retake ? 'warning' : 'default'}
                                />
                              </TableCell>
                              <TableCell>
                                {canEdit(selectedStatement.status) ? (
                                  <IconButton
                                    size="small"
                                    color="primary"
                                    onClick={() => handleEditGrade(grade)}
                                    title="Редактировать"
                                  >
                                    <EditIcon fontSize="small" />
                                  </IconButton>
                                ) : (
                                  <LockIcon fontSize="small" color="disabled" />
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent>
                  <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                    Выберите ведомость из списка слева
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Box>
        </Box>
      </Container>

      {/* Диалог редактирования оценки */}
      <Dialog open={editDialogOpen} onClose={() => !saving && setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>✏️ Редактировать оценку</DialogTitle>
        <DialogContent>
          {editingGrade && (
            <>
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Студент:</strong> {editingGrade.student_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                СНИЛС: {editingGrade.student_snils}
              </Typography>
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Оценка</InputLabel>
                <Select
                  value={newGradeValue}
                  label="Оценка"
                  onChange={(e) => setNewGradeValue(e.target.value)}
                >
                  <MenuItem value="5 (отлично)">5 (отлично)</MenuItem>
                  <MenuItem value="4 (хорошо)">4 (хорошо)</MenuItem>
                  <MenuItem value="3 (удовлетворительно)">3 (удовлетворительно)</MenuItem>
                  <MenuItem value="2 (неудовлетворительно)">2 (неудовлетворительно)</MenuItem>
                  <MenuItem value="н/а (не допущен)">н/а (не допущен)</MenuItem>
                  <MenuItem value="зачтено">Зачтено</MenuItem>
                  <MenuItem value="не_зачтено">Не зачтено</MenuItem>
                </Select>
              </FormControl>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)} disabled={saving}>Отмена</Button>
          <Button onClick={handleSaveGrade} variant="contained" disabled={saving || !newGradeValue}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
