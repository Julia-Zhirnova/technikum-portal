import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';

export default function ProfilePage() {
  const [snils, setSnils] = useState('');
  const [snilsError, setSnilsError] = useState('');
  const [phone, setPhone] = useState('');
  const [pdConsent, setPdConsent] = useState(false);
  const [pdConsentDate, setPdConsentDate] = useState('');
  
  const [passportSeries, setPassportSeries] = useState('');
  const [registrationAddress, setRegistrationAddress] = useState('');
  const [actualAddress, setActualAddress] = useState('');
  const [noPassport, setNoPassport] = useState(false);
  
  const [healthStatus, setHealthStatus] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [noOms, setNoOms] = useState(false);
  const [omsNumber, setOmsNumber] = useState('');
  
  const [autosaveIcon, setAutosaveIcon] = useState('');
  const [showRestoreModal, setShowRestoreModal] = useState(false);

  useEffect(() => {
    const draft = localStorage.getItem('student_profile_draft');
    if (draft) setShowRestoreModal(true);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (snils || phone || passportSeries) {
        localStorage.setItem('student_profile_draft', JSON.stringify({ snils, phone, passportSeries }));
        setAutosaveIcon('✅');
        setTimeout(() => setAutosaveIcon(''), 2000);
      }
    }, 30000);
    return () => clearTimeout(timer);
  }, [snils, phone, passportSeries]);

  const handleSnilsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const digits = value.replace(/\D/g, '').slice(0, 11);
    
    const formatted = digits.replace(/(\d{3})(\d{3})(\d{3})(\d{0,2})/, (match, p1, p2, p3, p4) => {
      let res = `${p1}-${p2}-${p3}`;
      if (p4) res += ` ${p4}`;
      return res;
    });
    setSnils(formatted);

    if (digits.length === 11) {
      const weights = [9, 8, 7, 6, 5, 4, 3, 2, 1];
      let sum = 0;
      for (let i = 0; i < 9; i++) sum += parseInt(digits[i]) * weights[i];
      
      let checksum = 0;
      if (sum < 100) checksum = sum;
      else if (sum === 100 || sum === 101) checksum = 0;
      else {
        checksum = sum % 101;
        if (checksum === 100 || checksum === 101) checksum = 0;
      }
      
      const expectedChecksum = parseInt(digits.slice(9, 11));
      if (checksum !== expectedChecksum) {
        setSnilsError('Неверный формат СНИЛС или контрольная сумма');
      } else {
        setSnilsError('');
      }
    } else if (digits.length > 0) {
      setSnilsError('Неверный формат СНИЛС');
    } else {
      setSnilsError('');
    }
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPhone(e.target.value.replace(/\D/g, '').slice(0, 11));
  };

  const handlePdConsentChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setPdConsent(checked);
    setPdConsentDate(checked ? new Date().toISOString().split('T')[0] : '');
  };

  const handleCopyAddress = () => setActualAddress(registrationAddress);

  const handleRestoreDraft = () => {
    const draft = localStorage.getItem('student_profile_draft');
    if (draft) {
      const parsed = JSON.parse(draft);
      if (parsed.snils) setSnils(parsed.snils);
      if (parsed.phone) setPhone(parsed.phone);
    }
    setShowRestoreModal(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Профиль студента</Typography>

      <Box sx={{ position: 'fixed', top: 20, right: 20, zIndex: 1000 }}>
        <Typography data-testid="autosave-icon" sx={{ fontSize: 24 }}>{autosaveIcon}</Typography>
      </Box>

      <Dialog open={showRestoreModal} onClose={() => setShowRestoreModal(false)}>
        <DialogTitle>Восстановление данных</DialogTitle>
        <DialogContent><Typography>Восстановить черновик?</Typography></DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRestoreModal(false)}>Нет</Button>
          <Button onClick={handleRestoreDraft} autoFocus>Восстановить черновик</Button>
        </DialogActions>
      </Dialog>

      <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
        <TextField
          label="СНИЛС"
          data-testid="snils-input"
          value={snils}
          onChange={handleSnilsChange}
          error={!!snilsError}
          helperText={snilsError}
          fullWidth
        />

        <TextField
          label="Телефон"
          data-testid="phone-input"
          value={phone}
          onChange={handlePhoneChange}
          fullWidth
        />

        <FormControlLabel
          control={
            <Checkbox 
              data-testid="pd-consent-checkbox"
              checked={pdConsent} 
              onChange={handlePdConsentChange} 
            />
          }
          label="Согласие на обработку ПДн"
        />
        {pdConsentDate && (
          <Typography data-testid="pd-consent-date" variant="body2" color="text.secondary">
            Дата согласия: {pdConsentDate}
          </Typography>
        )}

        <Typography variant="h6" sx={{ mt: 2 }}>Паспортные данные</Typography>
        
        <FormControlLabel
          control={<Checkbox data-testid="foreign-citizen-checkbox" checked={false} onChange={() => {}} />}
          label="Иностранный гражданин"
        />

        <FormControlLabel
          control={
            <Checkbox 
              data-testid="no-passport-checkbox"
              checked={noPassport} 
              onChange={(e) => setNoPassport(e.target.checked)} 
            />
          }
          label="Паспорта нет"
        />

        <TextField
          label="Серия и номер паспорта"
          data-testid="passport-series-input"
          value={passportSeries}
          onChange={(e) => setPassportSeries(e.target.value)}
          disabled={noPassport}
          fullWidth
        />

        <TextField
          label="Адрес регистрации"
          data-testid="registration-address-input"
          value={registrationAddress}
          onChange={(e) => setRegistrationAddress(e.target.value)}
          fullWidth
        />

        <Button variant="outlined" data-testid="copy-address-button" onClick={handleCopyAddress} sx={{ alignSelf: 'flex-start' }}>
          Совпадает с регистрацией
        </Button>

        <TextField
          label="Фактический адрес"
          data-testid="actual-address-input"
          value={actualAddress}
          onChange={(e) => setActualAddress(e.target.value)}
          fullWidth
        />

                <Typography variant="h6" sx={{ mt: 2 }}>Здоровье</Typography>

        <FormControl fullWidth>
          <InputLabel id="health-status-label">Состояние здоровья</InputLabel>
          <Select
            labelId="health-status-label"
            value={healthStatus}
            label="Состояние здоровья"
            onChange={(e) => setHealthStatus(e.target.value)}
            native
            inputProps={{ 'data-testid': 'health-status-select' }} // <-- ВАЖНО: атрибут попадет прямо в тег <select>
          >
            <option value="">Выберите...</option>
            <option value="Практически здоров">Практически здоров</option>
            <option value="Инвалидность">Инвалидность</option>
          </Select>
        </FormControl>

        {healthStatus === 'Инвалидность' && (
          <TextField
            label="Диагноз"
            data-testid="diagnosis-input"
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
            fullWidth
          />
        )}

        <FormControlLabel
          control={
            <Checkbox 
              data-testid="no-oms-checkbox"
              checked={noOms} 
              onChange={(e) => setNoOms(e.target.checked)} 
            />
          }
          label="Полиса ОМС нет"
        />

        <TextField
          label="Номер полиса ОМС"
          data-testid="oms-number-input"
          value={omsNumber}
          onChange={(e) => setOmsNumber(e.target.value)}
          disabled={noOms}
          fullWidth
        />
      </Box>
    </Container>
  );
}
