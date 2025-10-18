import { zodResolver } from '@hookform/resolvers/zod';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { ApiError } from '../../lib/api/client';
import { useAuth } from '../../app/AuthProvider';

const authSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters')
});

type AuthFormValues = z.infer<typeof authSchema>;
type AuthMode = 'login' | 'register';

const modeLabels: Record<AuthMode, string> = {
  login: 'Welcome back',
  register: 'Create your account'
};

const AuthPage = () => {
  const { user, loading, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const redirectTo = searchParams.get('redirect') || '/preferences';
  const [mode, setMode] = useState<AuthMode>(searchParams.get('mode') === 'register' ? 'register' : 'login');
  const [submissionError, setSubmissionError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema),
    defaultValues: { email: '', password: '' },
    mode: 'onBlur'
  });

  useEffect(() => {
    if (!loading && user) {
      navigate(redirectTo, { replace: true });
    }
  }, [user, loading, redirectTo, navigate]);

  useEffect(() => {
    reset({ email: '', password: '' });
    setSubmissionError(null);
  }, [mode, reset]);

  const onSubmit = async (values: AuthFormValues) => {
    setSubmissionError(null);
    try {
      if (mode === 'login') {
        await login(values);
      } else {
        await register(values);
      }
      navigate(redirectTo, { replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setSubmissionError(error.message);
        return;
      }
      setSubmissionError('Something went wrong. Please try again.');
    }
  };

  if (loading && !user) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(180deg, rgba(244, 220, 202, 0.35) 0%, rgba(255, 249, 244, 1) 100%)'
        }}
      >
        <Stack spacing={2} alignItems="center">
          <CircularProgress />
          <Typography variant="h6">Preparing your account…</Typography>
        </Stack>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background: 'linear-gradient(180deg, rgba(244, 220, 202, 0.35) 0%, rgba(255, 249, 244, 1) 100%)',
        py: 8
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={6} sx={{ p: 4, borderRadius: 4 }}>
          <Stack spacing={3}>
            <Stack spacing={1} alignItems="center">
              <Typography variant="h4" fontWeight={600} textAlign="center">
                {modeLabels[mode]}
              </Typography>
              <Typography variant="body2" color="text.secondary" textAlign="center">
                {mode === 'login'
                  ? 'Sign in to continue crafting culturally rich meal plans.'
                  : 'Join us to build meal plans that celebrate your heritage.'}
              </Typography>
            </Stack>

            <Tabs
              value={mode}
              onChange={(_, value: AuthMode) => setMode(value)}
              variant="fullWidth"
              sx={{ borderRadius: 2, bgcolor: 'rgba(180, 76, 59, 0.08)' }}
            >
              <Tab label="Log In" value="login" />
              <Tab label="Register" value="register" />
            </Tabs>

            {submissionError && <Alert severity="error">{submissionError}</Alert>}

            <Stack component="form" spacing={3} onSubmit={handleSubmit(onSubmit)}>
              <Controller
                control={control}
                name="email"
                render={({ field }) => (
                  <TextField
                    label="Email"
                    type="email"
                    fullWidth
                    autoComplete="email"
                    error={Boolean(errors.email)}
                    helperText={errors.email?.message}
                    {...field}
                  />
                )}
              />

              <Controller
                control={control}
                name="password"
                render={({ field }) => (
                  <TextField
                    label="Password"
                    type="password"
                    fullWidth
                    autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                    error={Boolean(errors.password)}
                    helperText={
                      errors.password?.message ??
                      (mode === 'register' ? 'Minimum 8 characters, mix letters and numbers for strength.' : undefined)
                    }
                    {...field}
                  />
                )}
              />

              <Button type="submit" variant="contained" size="large" disabled={loading}>
                {mode === 'login' ? 'Log In' : 'Create Account'}
              </Button>
            </Stack>

            <Typography variant="body2" color="text.secondary" textAlign="center">
              <Button component={RouterLink} to="/" variant="text">
                Back to landing page
              </Button>
            </Typography>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
};

export default AuthPage;
