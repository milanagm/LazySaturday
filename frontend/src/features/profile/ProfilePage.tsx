import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Collapse,
  Container,
  Divider,
  Grid,
  Stack,
  Typography
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { useAuth } from '../../app/AuthProvider';
import { api, type PreferencesPayload } from '../../lib/api/client';
import PreferencesForm from '../preferences/PreferencesForm';

type SummaryItem = {
  label: string;
  value: string | number | null | undefined;
  hint?: string;
  chips?: string[];
};

const renderValue = (item: SummaryItem) => {
  if (item.chips && item.chips.length > 0) {
    return (
      <Stack direction="row" spacing={1} flexWrap="wrap" rowGap={1}>
        {item.chips.map((chip) => (
          <Chip key={chip} label={chip} size="small" />
        ))}
      </Stack>
    );
  }

  if (item.value === null || item.value === undefined || item.value === '') {
    return (
      <Typography variant="body2" color="text.secondary">
        Not provided
      </Typography>
    );
  }

  return (
    <Typography variant="body1" fontWeight={500}>
      {item.value}
    </Typography>
  );
};

const PreferencesSummary = ({ preferences }: { preferences: PreferencesPayload }) => {
  const items: SummaryItem[] = [
    { label: 'Primary Diet', value: preferences.diet_id },
    { label: 'Primary Culture', value: preferences.culture_id },
    { label: 'Additional Cultures', value: preferences.additional_cultures.join(', '), chips: preferences.additional_cultures },
    { label: 'Country', value: preferences.country },
    { label: 'City', value: preferences.city },
    { label: 'Dietary Goals', value: preferences.dietary_goals.join(', '), chips: preferences.dietary_goals },
    { label: 'Allergies', value: preferences.allergies.join(', '), chips: preferences.allergies },
    { label: 'Disliked Ingredients', value: preferences.disliked_ingredients.join(', '), chips: preferences.disliked_ingredients },
    { label: 'Meals Per Day', value: preferences.meals_per_day },
    { label: 'Household Size', value: preferences.household_size },
    { label: 'Cooking Time Limit (minutes)', value: preferences.cooking_time_limit }
  ];

  return (
    <Grid container spacing={2}>
      {items.map((item) => (
        <Grid key={item.label} item xs={12} sm={6}>
          <Stack spacing={0.5}>
            <Typography variant="body2" color="text.secondary">
              {item.label}
            </Typography>
            {renderValue(item)}
            {item.hint && (
              <Typography variant="caption" color="text.secondary">
                {item.hint}
              </Typography>
            )}
          </Stack>
        </Grid>
      ))}
    </Grid>
  );
};

const ProfilePage = () => {
  const { user } = useAuth();
  const [editing, setEditing] = useState(false);

  const userEmail = user?.email ?? null;

  const {
    data: preferences,
    isLoading,
    isFetching,
    isError,
    error
  } = useQuery({
    queryKey: ['user-preferences', userEmail],
    queryFn: api.getPreferences,
    enabled: Boolean(userEmail)
  });

  if (!user) {
    return null;
  }

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Stack spacing={4}>
        <Stack spacing={1}>
          <Typography component="h1" variant="h4" fontWeight={600}>
            Your Profile
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Review your account details and keep your cultural preferences up to date.
          </Typography>
        </Stack>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={2}>
              <Stack direction="row" spacing={2} alignItems="center">
                <Typography variant="h6">Account</Typography>
                <Chip
                  label={user.is_verified ? 'Verified' : 'Verification pending'}
                  color={user.is_verified ? 'success' : 'default'}
                  size="small"
                />
              </Stack>
              <Stack spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  Email
                </Typography>
                <Typography variant="body1" fontWeight={500}>
                  {user.email}
                </Typography>
              </Stack>
              <Stack spacing={1}>
                <Typography variant="body2" color="text.secondary">
                  User ID
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {user.id}
                </Typography>
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack spacing={3}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="h6">Saved Preferences</Typography>
                <Button
                  variant={editing ? 'outlined' : 'contained'}
                  onClick={() => setEditing((current) => !current)}
                >
                  {editing ? 'Close Editor' : 'Edit Preferences'}
                </Button>
              </Stack>
              {isLoading ? (
                <Stack spacing={2} alignItems="center" justifyContent="center" minHeight={160}>
                  <CircularProgress size={32} />
                  <Typography variant="body2" color="text.secondary">
                    Loading your preferences…
                  </Typography>
                </Stack>
              ) : isError ? (
                <Alert severity="error">
                  {error instanceof Error ? error.message : 'Unable to load preferences right now.'}
                </Alert>
              ) : preferences ? (
                <Stack spacing={3}>
                  <PreferencesSummary preferences={preferences} />
                  {isFetching && (
                    <Typography variant="caption" color="text.secondary">
                      Refreshing with your latest updates…
                    </Typography>
                  )}
                </Stack>
              ) : (
                <Alert severity="info">
                  You have not saved any preferences yet. Use the editor below to personalise your plan.
                </Alert>
              )}
              <Divider />
              <Typography variant="body2" color="text.secondary">
                Changes you make in the editor are saved automatically and power your personalised meal plans.
              </Typography>
              <Collapse in={editing} mountOnEnter unmountOnExit>
                <Box mt={2}>
                  <PreferencesForm />
                </Box>
              </Collapse>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Container>
  );
};

export default ProfilePage;
