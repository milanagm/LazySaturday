import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Grid,
  Skeleton,
  Stack,
  Typography
} from '@mui/material';
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../app/AuthProvider';
import { api, type TodayMeal } from '../../lib/api/client';
import { Link as RouterLink } from 'react-router-dom';

const statusChipColor = (meal: TodayMeal): 'default' | 'primary' | 'success' => {
  if (meal.status === 'current') return 'primary';
  if (meal.status === 'completed') return 'success';
  return 'default';
};

const mealTimeLabel = (meal: TodayMeal) => `${meal.scheduled_time} · ${meal.meal_label}`;

const formatLabel = (value: string) =>
  value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

const TodayPage = () => {
  const { user } = useAuth();

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['plan', 'today'],
    queryFn: api.getTodayOverview,
    staleTime: 1000 * 60 * 5,
    enabled: Boolean(user)
  });

  const friendlyName = user?.email?.split('@')[0] ?? 'friend';

  const formattedDate = useMemo(() => {
    if (!data) return '';
    const date = new Date(data.date);
    return new Intl.DateTimeFormat(undefined, {
      weekday: 'long',
      month: 'long',
      day: 'numeric'
    }).format(date);
  }, [data]);

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Stack spacing={3}>
          <Skeleton variant="text" width={220} height={40} />
          <Skeleton variant="rectangular" height={220} />
          <Skeleton variant="rectangular" height={300} />
        </Stack>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container maxWidth="sm" sx={{ py: 10 }}>
        <Stack spacing={3} alignItems="center" textAlign="center">
          <Typography variant="h4" fontWeight={600}>
            No plan yet
          </Typography>
          <Typography color="text.secondary">
            Generate your first cultural meal plan to see today&apos;s personalised recommendations.
          </Typography>
          <Button component={RouterLink} to="/preferences" variant="contained" size="large">
            Create my plan
          </Button>
        </Stack>
      </Container>
    );
  }

  const currentMeal = data.current_meal;
  const remainingMeals = data.meals;
  const planStatusLabel = formatLabel(data.plan_status);

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Stack spacing={4}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }}>
          <Box>
            <Typography variant="h4" fontWeight={700}>
              Today · {formattedDate}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {data.greeting}, {friendlyName} — your {formatLabel(data.culture_id)} plan is ready.
            </Typography>
          </Box>
          <Chip label={planStatusLabel} color="secondary" sx={{ fontWeight: 600 }} />
          <Button variant="outlined" onClick={() => refetch()} disabled={isFetching}>
            Refresh
          </Button>
        </Stack>

        {currentMeal && (
          <Card elevation={2} sx={{ borderRadius: 4 }}>
            <CardContent>
              <Stack spacing={2}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Chip label="Current" color="primary" />
                  <Typography variant="h5" fontWeight={600}>
                    {currentMeal.recipe_title}
                  </Typography>
                </Stack>
                <Typography color="text.secondary">{mealTimeLabel(currentMeal)}</Typography>
                {currentMeal.instructions && (
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                    {currentMeal.instructions}
                  </Typography>
                )}
                <Stack direction="row" spacing={2}>
                  <Button variant="contained">View recipe</Button>
                  <Button variant="outlined">Swap meal</Button>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        )}

        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Card elevation={1} sx={{ borderRadius: 4 }}>
              <CardContent>
                <Stack spacing={3}>
                  <Typography variant="h6" fontWeight={600}>
                    Today&apos;s meals
                  </Typography>
                  <Stack spacing={2}>
                    {remainingMeals.map((meal) => (
                      <Box
                        key={`${meal.meal_type}-${meal.recipe_title}`}
                        sx={{
                          borderRadius: 3,
                          border: '1px solid',
                          borderColor: meal.is_current ? 'primary.main' : 'rgba(0,0,0,0.06)',
                          p: 2,
                          backgroundColor: meal.is_current ? 'rgba(180, 76, 59, 0.08)' : 'background.paper'
                        }}
                      >
                        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ xs: 'flex-start', sm: 'center' }} justifyContent="space-between">
                          <Stack spacing={0.5}>
                            <Typography fontWeight={600}>{meal.recipe_title}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {mealTimeLabel(meal)}
                            </Typography>
                          </Stack>
                          <Chip label={formatLabel(meal.status)} color={statusChipColor(meal)} />
                        </Stack>
                      </Box>
                    ))}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              <Card elevation={1} sx={{ borderRadius: 4 }}>
                <CardContent>
                  <Stack spacing={1.5}>
                    <Typography variant="h6" fontWeight={600}>
                      Quick facts
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Diet: {formatLabel(data.diet_id)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Culture: {formatLabel(data.culture_id)}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
              <Card elevation={1} sx={{ borderRadius: 4 }}>
                <CardContent>
                  <Stack spacing={2}>
                    <Typography variant="h6" fontWeight={600}>
                      Daily prep
                    </Typography>
                    <Alert severity="info" variant="outlined">
                      Remember to review your shopping list and thaw any ingredients needed for tomorrow.
                    </Alert>
                    <Button component={RouterLink} to="/preferences" variant="text">
                      Adjust preferences
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
};

export default TodayPage;
