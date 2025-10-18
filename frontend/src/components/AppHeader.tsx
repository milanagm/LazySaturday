import { useState, MouseEvent } from 'react';
import {
  AppBar,
  Avatar,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Toolbar,
  Typography
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { UserProfile } from '../lib/api/client';

type AppHeaderProps = {
  user: UserProfile | null;
  onLogin: () => void;
  onLogout: () => void;
};

const AppHeader = ({ user, onLogin, onLogout }: AppHeaderProps) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const menuOpen = Boolean(anchorEl);

  const handleMenuOpen = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const initials = user?.email?.[0]?.toUpperCase() ?? 'U';
  const friendlyName = user?.email?.split('@')[0] ?? 'Guest';

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        backgroundColor: '#fff4e6',
        borderBottom: '1px solid rgba(0,0,0,0.06)',
        color: 'text.primary'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', gap: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Box
            component={RouterLink}
            to="/"
            sx={{ textDecoration: 'none', color: 'inherit' }}
          >
            <Typography variant="h6" fontWeight={700}>
              Diet Planner
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            Eat healthy, stay rooted.
          </Typography>
        </Stack>

        {!user ? (
          <Button
            color="primary"
            variant="contained"
            onClick={onLogin}
            sx={{ borderRadius: 999 }}
          >
            Log in
          </Button>
        ) : (
          <Stack direction="row" spacing={2} alignItems="center">
            <Button component={RouterLink} to="/plan/today" variant="outlined" color="primary">
              Today&apos;s plan
            </Button>
            <Typography variant="body2" color="text.secondary">
              Hi, {friendlyName}
            </Typography>
            <IconButton onClick={handleMenuOpen} size="small" sx={{ p: 0 }}>
              <Avatar sx={{ bgcolor: 'primary.main', color: 'primary.contrastText' }}>
                {initials}
              </Avatar>
            </IconButton>
            <Menu anchorEl={anchorEl} open={menuOpen} onClose={handleMenuClose} keepMounted>
              <MenuItem disabled>{user.email}</MenuItem>
              <MenuItem
                component={RouterLink}
                to="/preferences"
                onClick={() => {
                  handleMenuClose();
                }}
              >
                Preferences
              </MenuItem>
              <MenuItem
                onClick={() => {
                  handleMenuClose();
                  onLogout();
                }}
              >
                Log out
              </MenuItem>
            </Menu>
          </Stack>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default AppHeader;
