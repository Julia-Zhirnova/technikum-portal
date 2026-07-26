import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Checkbox,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select
} from '@mui/material';

export default function HealthPage() {
  const [healthStatus, setHealthStatus] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [noOms, setNoOms] = useState(false);
  const [omsNumber, setOmsNumber] = useState('');

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>🏥 Здоровье</Typography>
      <Card>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="health-status-label">Состояние здоровья</InputLabel>
                <Select
                  labelId="health-status-label"
                  value={healthStatus}
                  label="Состояние здоровья"
                  onChange={(e) => setHealthStatus(e.target.value)}
                  native
                  inputProps={{ 'data-testid': 'health-status-select' }}
                >
                  <option value="">Выберите...</option>
                  <option value="Практически здоров">Практически здоров</option>
                  <option value="Инвалидность">Инвалидность</option>
                </Select>
              </FormControl>
            </Grid>

            {healthStatus === 'Инвалидность' && (
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Диагноз"
                  data-testid="diagnosis-input"
                  value={diagnosis}
                  onChange={(e) => setDiagnosis(e.target.value)}
                  fullWidth
                />
              </Grid>
            )}

            <Grid item xs={12}>
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
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                label="Номер полиса ОМС"
                data-testid="oms-number-input"
                value={omsNumber}
                onChange={(e) => setOmsNumber(e.target.value)}
                disabled={noOms}
                fullWidth
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
}
