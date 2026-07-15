import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import TopNavbar from './TopNavbar';

export default function DashboardLayout() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <TopNavbar />
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 3 } }}>
        <Outlet />
      </Box>
    </Box>
  );
}
