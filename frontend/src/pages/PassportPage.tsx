import React, { useState } from 'react';
import { Container, Typography, Card, CardContent, Grid, TextField, Checkbox, FormControlLabel, Button } from '@mui/material';

export default function PassportPage() {
  const [isForeign, setIsForeign] = useState(false);
  const [noPassport, setNoPassport] = useState(false);
  const [passportSeries, setPassportSeries] = useState('');
  const [registrationAddress, setRegistrationAddress] = useState('');
  const [actualAddress, setActualAddress] = useState('');

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>Паспортные данные</Typography>
      <Card>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox 
                    data-testid="foreign-citizen-checkbox"
                    checked={isForeign} 
                    onChange={(e) => setIsForeign(e.target.checked)} 
                  />
                }
                label="Иностранный гражданин"
              />
            </Grid>
            
            <Grid item xs={12}>
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
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                label="Серия и номер паспорта"
                data-testid="passport-series-input"
                value={passportSeries}
                onChange={(e) => setPassportSeries(e.target.value)}
                disabled={noPassport}
                fullWidth
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Адрес регистрации"
                data-testid="registration-address-input"
                value={registrationAddress}
                onChange={(e) => setRegistrationAddress(e.target.value)}
                fullWidth
              />
            </Grid>

            <Grid item xs={12}>
              <Button 
                variant="outlined" 
                data-testid="copy-address-button"
                onClick={() => setActualAddress(registrationAddress)}
              >
                Совпадает с регистрацией
              </Button>
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Фактический адрес"
                data-testid="actual-address-input"
                value={actualAddress}
                onChange={(e) => setActualAddress(e.target.value)}
                fullWidth
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
}
