import { useState } from 'react';
import { 
  Box, Typography, Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, Select, MenuItem, FormControl, 
  InputLabel, Button, CircularProgress, useTheme 
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import DescriptionIcon from '@mui/icons-material/Description';

export default function TeacherStatementsPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [groupFilter, setGroupFilter] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const theme = useTheme();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleExportDocx = () => {
    setIsExporting(true);
    // Симуляция запроса
    setTimeout(() => setIsExporting(false), 1500);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>Мои ведомости</Typography>

      {/* 5.1.4 и 5.1.5: Фильтры */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Группа</InputLabel>
          <Select
            data-testid="group-filter"
            value={groupFilter}
            label="Группа"
            onChange={(e) => setGroupFilter(e.target.value)}
          >
            <MenuItem value=""><em>Все</em></MenuItem>
            <MenuItem value="ИС-24">ИС-24</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Статус</InputLabel>
          <Select
            data-testid="status-filter"
            value={statusFilter}
            label="Статус"
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <MenuItem value=""><em>Все</em></MenuItem>
            <MenuItem value="в_работе">В работе</MenuItem>
            <MenuItem value="закрыта">Закрыта</MenuItem>
            <MenuItem value="сдана_в_архив">Сдана в архив</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* 5.4.5 и 5.4.6: Импорт и Drag & Drop */}
      <Box 
        data-testid="import-dropzone"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        sx={{ 
          border: `2px dashed ${isDragActive ? theme.palette.primary.main : theme.palette.divider}`,
          borderRadius: 2, p: 3, mb: 3, textAlign: 'center',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s'
        }}
      >
        <CloudUploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          Перетащите файл Excel сюда или нажмите для выбора
        </Typography>
        <Button 
          data-testid="import-btn"
          variant="outlined" 
          startIcon={<CloudUploadIcon />} 
          sx={{ mt: 1 }}
        >
          Импорт из Excel
        </Button>
      </Box>

      {/* 5.1.3: Таблица ведомостей */}
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Номер</strong></TableCell>
              <TableCell><strong>Группа</strong></TableCell>
              <TableCell><strong>Дисциплина</strong></TableCell>
              <TableCell><strong>Статус</strong></TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow hover>
              <TableCell>СТ-1</TableCell>
              <TableCell>ИС-24</TableCell>
              <TableCell>Основы алгоритмизации</TableCell>
              <TableCell>В работе</TableCell>
              <TableCell>
                <Button size="small" variant="text">Открыть</Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>

      {/* 5.5.4 и 5.5.5: Экспорт и индикатор загрузки */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button 
          data-testid="export-xlsx-btn"
          variant="outlined" 
          startIcon={<FileDownloadIcon />}
        >
          Экспорт в XLSX
        </Button>
        <Button 
          data-testid="export-docx-btn"
          variant="contained" 
          startIcon={isExporting ? <CircularProgress size={20} color="inherit" data-testid="loading-spinner" /> : <DescriptionIcon />}
          disabled={isExporting}
          onClick={handleExportDocx}
        >
          {isExporting ? 'Генерация...' : 'Скачать DOCX'}
        </Button>
      </Box>
    </Box>
  );
}
