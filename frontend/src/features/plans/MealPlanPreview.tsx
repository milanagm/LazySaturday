import { Button, Card, CardContent, CardHeader, Divider, List, ListItem, ListItemText, Stack, Typography } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api/client';

const MealPlanPreview = () => {
  const queryClient = useQueryClient();
  const { data, isFetching } = useQuery({ queryKey: ['meal-plan'], queryFn: api.getLatestMealPlan });

  const mutation = useMutation({
    mutationFn: api.generatePlan,
    onSuccess: (plan) => {
      queryClient.setQueryData(['meal-plan'], plan);
    }
  });

  return (
    <Card>
      <CardHeader
        title="Meal Plan Preview"
        action={
          <Button variant="outlined" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
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
            <Divider textAlign="left">Meals</Divider>
            <List dense>
              {data.meals.map((meal) => (
                <ListItem key={`${meal.day_of_week}-${meal.meal_type}`}>
                  <ListItemText
                    primary={`${meal.day_of_week} – ${meal.recipe_title}`}
                    secondary={meal.instructions}
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
          </Stack>
        )}
      </CardContent>
    </Card>
  );
};

export default MealPlanPreview;
