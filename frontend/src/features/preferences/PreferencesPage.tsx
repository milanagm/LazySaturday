import { Container, Stack, Typography } from '@mui/material';
import PreferencesForm from './PreferencesForm';
import MealPlanPreview from '../plans/MealPlanPreview';

const PreferencesPage = () => (
  <Container maxWidth="md" sx={{ py: 6 }}>
    <Stack spacing={4}>
      <Typography component="h1" variant="h4" fontWeight={600}>
        Personalise Your Experience
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Tell us about your diet, culture, and goals so we can craft a plan that tastes like home.
      </Typography>
      <PreferencesForm />
      <MealPlanPreview />
    </Stack>
  </Container>
);

export default PreferencesPage;
