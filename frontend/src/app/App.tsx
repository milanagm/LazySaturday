import { Container, Stack, Typography } from '@mui/material';
import PreferencesForm from '../features/preferences/PreferencesForm';
import MealPlanPreview from '../features/plans/MealPlanPreview';

const App = () => (
  <Container maxWidth="md" sx={{ py: 6 }}>
    <Stack spacing={4}>
      <Typography component="h1" variant="h4" fontWeight={600}>
        Culturally Adaptive Diet Planner
      </Typography>
      <PreferencesForm />
      <MealPlanPreview />
    </Stack>
  </Container>
);

export default App;
