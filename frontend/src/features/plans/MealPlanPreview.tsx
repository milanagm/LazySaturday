import {
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemText,
  Stack,
  Typography
} from '@mui/material';
import { useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type PreferencesPayload } from '../../lib/api/client';
import { useAuth } from '../../app/AuthProvider';

const MealPlanPreview = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const userEmail = user?.email ?? '';
  const { data, isFetching } = useQuery({
    queryKey: ['meal-plan', userEmail],
    queryFn: api.getLatestMealPlan,
    enabled: Boolean(userEmail)
  });
  const savedPreferences = queryClient.getQueryData<PreferencesPayload | null>([
    'user-preferences',
    userEmail
  ]);

  const planPayload = useMemo(
    () => ({
      email: userEmail,
      diet_id: savedPreferences?.diet_id ?? 'balanced',
      culture_id: savedPreferences?.culture_id ?? 'indian'
    }),
    [savedPreferences, userEmail]
  );

  const mutation = useMutation({
    mutationFn: () => api.generatePlan(planPayload),
    onSuccess: (plan) => {
      queryClient.setQueryData(['meal-plan', userEmail], plan);
    }
  });

  return (
    <Card>
      <CardHeader
        title="Meal Plan Preview"
        action={
          <Button
            variant="outlined"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !userEmail}
          >
            {mutation.isPending ? 'Generating…' : 'Generate Plan'}
          </Button>
        }
      />
      <CardContent>
        {isFetching && <Typography variant="body2">Loading meal plan…</Typography>}
        {!isFetching && !data && <Typography variant="body2">No plan generated yet.</Typography>}
        {data && (
          <Stack spacing={2}>
            <Typography variant="subtitle1">Week starting {data.week_start}</Typography>
            {data.summary && (
              <Stack spacing={1}>
                <Typography variant="body2">{data.summary.overview}</Typography>
                {data.summary.calorie_total && (
                  <Typography variant="caption" color="text.secondary">
                    Total calories: {data.summary.calorie_total}
                  </Typography>
                )}
              </Stack>
            )}
            <Divider textAlign="left">Meals</Divider>
            <List dense>
              {data.meals.map((meal) => (
                <ListItem key={`${meal.day_of_week}-${meal.meal_type}-${meal.recipe_id ?? ''}`}>
                  <ListItemText
                    primary={`${meal.day_of_week} – ${meal.recipe_title}`}
                    secondary={
                      meal.instruction_steps.length
                        ? meal.instruction_steps.map((step) => `${step.step_number}. ${step.description}`).join(' ')
                        : meal.instructions
                    }
                  />
                </ListItem>
              ))}
            </List>
            <Divider textAlign="left">Shopping List</Divider>
            <List dense>
              {data.shopping_list.map((item) => (
                <ListItem key={item.name}>
                  <ListItemText primary={`${item.name}: ${item.quantity}`} />
                </ListItem>
              ))}
            </List>
            {data.warnings.length > 0 && (
              <>
                <Divider textAlign="left">Warnings</Divider>
                <List dense>
                  {data.warnings.map((warning) => (
                    <ListItem key={warning.code}>
                      <ListItemText
                        primary={warning.message}
                        secondary={warning.blocking ? 'Action required' : 'Informational'}
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </Stack>
        )}
      </CardContent>
    </Card>
  );
};

export default MealPlanPreview;
