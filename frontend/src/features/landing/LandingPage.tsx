import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Divider,
  Grid,
  Stack,
  Typography
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import LocalDiningIcon from '@mui/icons-material/LocalDining';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import StarIcon from '@mui/icons-material/Star';
import { styled } from '@mui/material/styles';
import { useAuth } from '../../app/AuthProvider';

const HeroImage = styled('div')(({ theme }) => ({
  position: 'relative',
  width: '100%',
  paddingTop: '75%',
  borderRadius: theme.shape.borderRadius * 2,
  overflow: 'hidden',
  backgroundImage: 'url(/assets/hero-family-dinner.png)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundColor: '#f3c7a7',
  boxShadow: theme.shadows[6]
}));

const SecondaryImage = styled('div')(({ theme }) => ({
  position: 'absolute',
  bottom: theme.spacing(-4),
  right: theme.spacing(-4),
  width: '45%',
  paddingTop: '45%',
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
  backgroundImage: 'url(/assets/hero-market-basket.png)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  backgroundColor: '#e2b48c',
  border: `4px solid ${theme.palette.background.paper}`
}));
import { Link as RouterLink } from 'react-router-dom';

const featureHighlights = [
  {
    title: 'Culture-centric recipes',
    description:
      'AI blends your heritage with local ingredients, ensuring every dinner tastes like home.',
    icon: <RestaurantIcon fontSize="large" color="primary" />
  },
  {
    title: 'Smart shopping lists',
    description: 'Automatically curated ingredients matched to stores near you and your budget.',
    icon: <LocalDiningIcon fontSize="large" color="primary" />
  },
  {
    title: 'Automated reminders',
    description: 'Daily nudges and prep reminders keep you on track without the mental load.',
    icon: <AccessTimeIcon fontSize="large" color="primary" />
  }
];

const flowSteps = [
  {
    title: 'Share your story',
    body: 'Select diet, culture, and goals in a guided, friendly wizard in under five minutes.'
  },
  {
    title: 'AI crafts your plan',
    body: 'n8n orchestrates recipes, shopping list, and schedule tailored to your household.'
  },
  {
    title: 'Cook with confidence',
    body: 'Receive weekly plans, smart ingredient swaps, and notifications that respect your time.'
  }
];

const testimonials = [
  {
    quote:
      '“It finally feels like my Berlin kitchen speaks Moroccan again. The ingredient swaps are genius.”',
    name: 'Amina · Product Designer'
  },
  {
    quote: '“Meal prep is smoother knowing each dish honours my Nigerian roots.”',
    name: 'Chidi · Software Engineer'
  }
];

const deliverables = [
  {
    title: 'Weekly cultural meal plan',
    description: 'Printed PDF and mobile view with stories behind each recipe.'
  },
  {
    title: 'Smart shopping list',
    description: 'Aggregated ingredients with local substitutes and metric units.'
  },
  {
    title: 'Daily guidance',
    description: 'Reminders delivered when you actually have time to cook.'
  }
];

const LandingPage = () => {
  const { user } = useAuth();
  const isAuthenticated = Boolean(user);
  const primaryCtaTarget = isAuthenticated ? '/preferences' : '/auth?redirect=/preferences';
  const primaryCtaLabel = isAuthenticated ? 'Open Your Planner' : 'Start Your Cultural Plan';

  return (
    <Box sx={{ backgroundColor: 'background.default', minHeight: '100vh' }}>
      <Box
        component="section"
        sx={{
          background: (theme) =>
            `linear-gradient(135deg, ${theme.palette.primary.main}0F 0%, ${theme.palette.secondary.main}10 100%)`,
          py: { xs: 10, md: 14 }
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Stack spacing={3}>
                <Chip label="Culturally Adaptive Diet Planner" color="primary" variant="outlined" />
                <Typography component="h1" variant="h3" fontWeight={700} lineHeight={1.2}>
                  Eat healthier without losing the flavours that shaped you.
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Craft AI-guided weekly meal plans that honour your cultural background, fit your
                  dietary goals, and source ingredients from stores around you.
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <Button
                    component={RouterLink}
                    to={primaryCtaTarget}
                    variant="contained"
                    size="large"
                    endIcon={<ArrowForwardIcon />}
                  >
                    {primaryCtaLabel}
                  </Button>
                  <Button
                    href="#how-it-works"
                    variant="outlined"
                    size="large"
                    endIcon={<PlayCircleOutlineIcon />}
                  >
                    See How It Works
                  </Button>
                </Stack>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ position: 'relative', maxWidth: 520, mx: { xs: 'auto', md: 0 } }}>
                <HeroImage />
                <SecondaryImage />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container
        component="section"
        maxWidth="lg"
        sx={{ py: { xs: 8, md: 10 } }}
      >
        <Grid container spacing={4}>
          {featureHighlights.map((feature) => (
            <Grid item xs={12} md={4} key={feature.title}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: 'rgba(0,0,0,0.05)',
                  background: 'rgba(255, 249, 244, 0.9)'
                }}
              >
                <CardContent>
                  <Stack spacing={2}>
                    {feature.icon}
                    <Typography variant="h6" fontWeight={600}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box
        id="how-it-works"
        component="section"
        sx={{
          backgroundColor: '#ffe8d6',
          py: { xs: 8, md: 10 },
          borderTop: '1px solid rgba(0,0,0,0.05)',
          borderBottom: '1px solid rgba(0,0,0,0.05)'
        }}
      >
        <Container maxWidth="md">
          <Stack spacing={3} textAlign="center">
            <Typography variant="h4" fontWeight={700}>
              How it works
            </Typography>
            <Typography variant="body1" color="text.secondary">
              A guided journey from story-driven onboarding to personalised meal planning.
            </Typography>
          </Stack>
          <Grid container spacing={4} sx={{ mt: 4 }}>
            {flowSteps.map((step, index) => (
              <Grid item xs={12} md={4} key={step.title}>
                <Card
                  elevation={1}
                  sx={{
                    height: '100%',
                    borderRadius: 3,
                    background: '#fffdfa',
                    border: '1px solid rgba(0,0,0,0.04)'
                  }}
                >
                  <CardContent>
                    <Stack spacing={2}>
                      <Chip label={`Step ${index + 1}`} color="primary" variant="outlined" />
                      <Typography variant="h6" fontWeight={600}>
                        {step.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {step.body}
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      <Container component="section" maxWidth="md" sx={{ py: { xs: 8, md: 10 } }}>
        <Stack spacing={4}>
          <Typography variant="h4" fontWeight={700} textAlign="center">
            Loved by multicultural households
          </Typography>
          <Grid container spacing={3}>
            {testimonials.map((testimonial) => (
              <Grid item xs={12} md={6} key={testimonial.name}>
                <Card
                  elevation={0}
                  sx={{
                    borderRadius: 3,
                    border: '1px solid rgba(0,0,0,0.05)',
                    background: 'rgba(255, 240, 224, 0.9)'
                  }}
                >
                  <CardContent>
                    <Stack spacing={2}>
                      <Stack direction="row" spacing={1}>
                        {Array.from({ length: 5 }).map((_, index) => (
                          <StarIcon key={index} fontSize="small" color="warning" />
                        ))}
                      </Stack>
                      <Typography variant="body1" fontStyle="italic">
                        {testimonial.quote}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {testimonial.name}
                      </Typography>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </Container>

      <Box component="section" sx={{ backgroundColor: 'background.paper', py: { xs: 8, md: 10 } }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Stack spacing={3}>
                <Typography variant="h4" fontWeight={700}>
                  What you receive every week
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Your plan is more than recipes. It is a cultural companion that fits your schedule.
                </Typography>
                <Stack spacing={2}>
                  {deliverables.map((item) => (
                    <Stack key={item.title} spacing={1}>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {item.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {item.description}
                      </Typography>
                    </Stack>
                  ))}
                </Stack>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card elevation={3} sx={{ borderRadius: 4 }}>
                <CardContent>
                  <Stack spacing={3}>
                    <Typography variant="h6" fontWeight={600}>
                      Ready to taste the difference?
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Start your free cultural plan preview and see how your preferences turn into a
                      delicious, organised week.
                    </Typography>
                    <Button
                      component={RouterLink}
                      to="/preferences"
                      variant="contained"
                      size="large"
                      endIcon={<ArrowForwardIcon />}
                    >
                      Customise your first week
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Box component="footer" sx={{ backgroundColor: 'grey.900', color: 'common.white', py: 6 }}>
        <Container maxWidth="lg">
          <Stack spacing={3} alignItems={{ xs: 'flex-start', md: 'center' }} textAlign={{ xs: 'left', md: 'center' }}>
            <Typography variant="h6" fontWeight={700}>
              Culturally Adaptive Diet Planner
            </Typography>
            <Typography variant="body2" sx={{ maxWidth: 600 }}>
              Built by immigrants for immigrants — keeping your roots on the table while embracing
              the ingredients around you.
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button component={RouterLink} to="/preferences" variant="contained" color="secondary">
                Get Started
              </Button>
              <Button variant="outlined" color="inherit" href="mailto:hello@dietplanner.app">
                Contact Us
              </Button>
            </Stack>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
