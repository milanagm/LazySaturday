import { Box } from '@mui/material';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import AppHeader from '../components/AppHeader';
import { useAuth } from './AuthProvider';

const MainLayout = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const location = useLocation();

  const handleLogin = () => {
    const current = `${location.pathname}${location.search}` || '/';
    const redirectTarget = current === '/' ? '/preferences' : current;
    navigate(`/auth?redirect=${encodeURIComponent(redirectTarget)}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <Box display="flex" flexDirection="column" minHeight="100vh">
      <AppHeader user={user} onLogin={handleLogin} onLogout={handleLogout} />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
