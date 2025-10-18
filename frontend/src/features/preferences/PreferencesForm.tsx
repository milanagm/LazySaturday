import { useEffect, useMemo, useRef, useState } from 'react';
import { Controller, FormProvider, useForm, useFormContext, useWatch } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Alert,
  Autocomplete,
  Backdrop,
  Box,
  Button,
  ButtonBase,
  Chip,
  CircularProgress,
  Divider,
  FormControlLabel,
  FormGroup,
  IconButton,
  MenuItem,
  Slider,
  Snackbar,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Switch,
  TextField,
  Typography
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import {
  api,
  type CultureOption,
  type DietOption,
  type PreferencesPayload,
  type SavePreferencesResponse
} from '../../lib/api/client';
import { useAuth } from '../../app/AuthProvider';

const schema = z.object({
  dietId: z.string().min(1, 'Please select a diet'),
  cultureIds: z.array(z.string()).min(1, 'Select at least one culture'),
  country: z.string().min(1, 'Please choose your country'),
  city: z.string().optional(),
  dietaryGoals: z.array(z.string()).default([]),
  allergies: z.array(z.string()).default([]),
  dislikedIngredients: z.array(z.string()).default([]),
  mealsPerDay: z.coerce.number().min(1).max(6),
  householdSize: z.coerce.number().min(1).max(10),
  cookingTimeLimit: z.coerce.number().min(15).max(120)
});

export type PreferencesFormValues = z.infer<typeof schema>;

const DEFAULT_VALUES: PreferencesFormValues = {
  dietId: 'balanced',
  cultureIds: ['indian'],
  country: 'germany',
  city: '',
  dietaryGoals: [],
  allergies: [],
  dislikedIngredients: [],
  mealsPerDay: 3,
  householdSize: 1,
  cookingTimeLimit: 30
};

const GOAL_OPTIONS = [
  { id: 'healthy_eating', label: '🩺 Eat healthier' },
  { id: 'weight_loss', label: '⚖️ Lose weight' },
  { id: 'gain_muscle', label: '🏋️ Gain muscle' },
  { id: 'sustainable_eating', label: '🌱 Sustainable eating' },
  { id: 'time_saving', label: '🕒 Save time cooking' }
];

const ALLERGY_OPTIONS = ['gluten', 'dairy', 'nuts', 'shellfish', 'soy', 'eggs'];

const COUNTRY_OPTIONS = [
  { id: 'germany', label: 'Germany' },
  { id: 'austria', label: 'Austria' },
  { id: 'india', label: 'India' },
  { id: 'united_kingdom', label: 'United Kingdom' },
  { id: 'united_states', label: 'United States' }
];

const DIET_DESCRIPTIONS: Record<string, string> = {
  vegan: 'Plant-based meals with zero animal products.',
  vegetarian: 'No meat, focus on vegetables and dairy.',
  halal: 'Prepared following halal-certified guidelines.',
  balanced: 'A mix of proteins, carbs, and vegetables.',
  pescatarian: 'Seafood forward with plant-based variety.',
  mediterranean: 'Olive oil, legumes, grains, and fresh produce.'
};

const DIET_IMAGES: Record<string, string> = {
  balanced: 'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?auto=format&fit=crop&w=700&q=80',
  vegan: 'https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=700&q=80',
  vegetarian: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=700&q=80',
  halal: 'https://images.unsplash.com/photo-1525755662778-989d0524087e?auto=format&fit=crop&w=700&q=80',
  pescatarian: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=700&q=80',
  mediterranean: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=700&q=80',
  low_carb: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&w=700&q=80'
};

const DEFAULT_DIET_IMAGE =
  'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?auto=format&fit=crop&w=700&q=80';

const FALLBACK_DIETS: DietOption[] = [
  { id: 'balanced', name: 'Balanced' },
  { id: 'vegan', name: 'Vegan' },
  { id: 'halal', name: 'Halal' }
];

const FALLBACK_CULTURES: CultureOption[] = [
  { id: 'indian', name: 'Indian', region_code: 'IN' },
  { id: 'ethiopian', name: 'Ethiopian', region_code: 'ET' },
  { id: 'italian', name: 'Italian', region_code: 'IT' },
  { id: 'turkish', name: 'Turkish', region_code: 'TR' }
];

const REGION_LABELS: Record<string, string> = {
  AF: 'African',
  AS: 'Asian',
  EU: 'European',
  LA: 'Latin American',
  ME: 'Middle Eastern'
};

const REGION_FROM_CODE: Record<string, string> = {
  IN: 'AS',
  ET: 'AF',
  IT: 'EU',
  TR: 'ME',
  MX: 'LA',
  KR: 'AS',
  NG: 'AF',
  PE: 'LA'
};

const steps = [
  { label: 'Diet' },
  { label: 'Culture' },
  { label: 'Goals' },
  { label: 'Location' },
  { label: 'Schedule' },
  { label: 'Allergies' }
];

const toPayload = (values: PreferencesFormValues, email: string): PreferencesPayload => {
  const cultures = values.cultureIds.length ? values.cultureIds : ['indian'];
  const [primaryCulture, ...additionalCultures] = cultures;
  return {
    email,
    diet_id: values.dietId,
    culture_id: primaryCulture,
    additional_cultures: additionalCultures,
    country: values.country,
    city: values.city?.trim() ? values.city.trim() : null,
    dietary_goals: values.dietaryGoals,
    allergies: values.allergies,
    disliked_ingredients: values.dislikedIngredients,
    meals_per_day: values.mealsPerDay,
    household_size: values.householdSize,
    cooking_time_limit: values.cookingTimeLimit
  };
};

const fromPayload = (payload: PreferencesPayload): PreferencesFormValues => {
  const cultures = [payload.culture_id, ...(payload.additional_cultures ?? [])].filter(
    (cultureId): cultureId is string => Boolean(cultureId)
  );
  return {
    dietId: payload.diet_id,
    cultureIds: cultures.length ? cultures : ['indian'],
    country: payload.country,
    city: payload.city ?? '',
    dietaryGoals: payload.dietary_goals ?? [],
    allergies: payload.allergies ?? [],
    dislikedIngredients: payload.disliked_ingredients ?? [],
    mealsPerDay: payload.meals_per_day,
    householdSize: payload.household_size,
    cookingTimeLimit: payload.cooking_time_limit
  };
};

const flagFromCode = (code: string) => {
  if (!code) return '🌍';
  return code
    .toUpperCase()
    .replace(/./g, (char) => String.fromCodePoint(127397 + char.charCodeAt(0)));
};

const PreferencesForm = () => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const methods = useForm<PreferencesFormValues>({
    resolver: zodResolver(schema),
    defaultValues: DEFAULT_VALUES,
    mode: 'onChange'
  });
  const { control, reset, getValues } = methods;

  const userEmail = user?.email ?? '';
  const [activeStep, setActiveStep] = useState(0);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const generationRef = useRef(false);
  const formReadyRef = useRef(false);
  const lastSavedPayload = useRef<string>('');
  const saveResetTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hasHydrated = useRef(false);

  useEffect(
    () => () => {
      if (saveResetTimer.current) {
        window.clearTimeout(saveResetTimer.current);
        saveResetTimer.current = null;
      }
    },
    []
  );

  const { data: dietsData = [] } = useQuery({ queryKey: ['diets'], queryFn: api.fetchDiets });
  const { data: culturesData = [] } = useQuery({ queryKey: ['cultures'], queryFn: api.fetchCultures });

  const { data: storedPreferences } = useQuery({
    queryKey: ['user-preferences', userEmail],
    queryFn: api.getPreferences,
    enabled: Boolean(userEmail)
  });

  useEffect(() => {
    if (storedPreferences && userEmail) {
      const formValues = fromPayload(storedPreferences);
      reset(formValues, { keepDirty: false });
      lastSavedPayload.current = JSON.stringify(storedPreferences);
    }
    if (!hasHydrated.current) {
      hasHydrated.current = true;
      formReadyRef.current = true;
    }
  }, [storedPreferences, reset, userEmail]);

  const mutation = useMutation({
    mutationFn: api.savePreferences,
    onMutate: () => {
      if (!generationRef.current) {
        setSaveState('saving');
      }
    },
    onSuccess: (data: SavePreferencesResponse, variables: PreferencesPayload) => {
      lastSavedPayload.current = JSON.stringify(variables);
      setSaveState('saved');
      queryClient.setQueryData(['user-preferences', variables.email], variables);
      if (saveResetTimer.current) {
        window.clearTimeout(saveResetTimer.current);
        saveResetTimer.current = null;
      }
      saveResetTimer.current = window.setTimeout(() => setSaveState('idle'), 2000);
      if (generationRef.current) {
        setSnackbarMessage(data.message);
        queryClient.invalidateQueries({ queryKey: ['meal-plan', userEmail] });
      }
    },
    onError: () => {
      setSaveState('error');
      setSnackbarMessage('Unable to save preferences. Please try again.');
    },
    onSettled: () => {
      if (generationRef.current) {
        setIsGenerating(false);
        generationRef.current = false;
      }
    }
  });

  const { mutate, isPending } = mutation;

  const watchedValues = useWatch({ control });

  useEffect(() => {
    if (!formReadyRef.current) {
      return;
    }
    if (generationRef.current || isPending) {
      return;
    }
    const parsed = schema.safeParse(watchedValues);
    if (!parsed.success) {
      return;
    }
    if (!userEmail) {
      return;
    }
    const payload = toPayload(parsed.data, userEmail);
    const payloadKey = JSON.stringify(payload);
    if (payloadKey === lastSavedPayload.current) {
      return;
    }
    const timer = window.setTimeout(() => {
      mutate(payload);
    }, 800);
    return () => window.clearTimeout(timer);
  }, [watchedValues, mutate, isPending]);

  const handleNext = () => setActiveStep((prev) => Math.min(prev + 1, steps.length - 1));
  const handleBack = () => setActiveStep((prev) => Math.max(prev - 1, 0));

  const handleGenerate = () => {
    const values = getValues();
    const parsed = schema.safeParse(values);
    if (!parsed.success) {
      setActiveStep(0);
      return;
    }
    if (!userEmail) {
      return;
    }
    const payload = toPayload(parsed.data, userEmail);
    generationRef.current = true;
    setIsGenerating(true);
    mutate(payload, {
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ['meal-plan', userEmail] });
      }
    });
  };

  const diets = useMemo(() => (dietsData.length ? dietsData : FALLBACK_DIETS), [dietsData]);
  const cultures = useMemo(() => (culturesData.length ? culturesData : FALLBACK_CULTURES), [culturesData]);

  if (!userEmail) {
    return null;
  }

  return (
    <FormProvider {...methods}>
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Typography variant="h6">Personalise Your Meal Experience</Typography>
            <Chip label={userEmail} size="small" variant="outlined" />
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center">
            {saveState === 'saving' && <Chip color="info" label="Saving…" size="small" />}
            {saveState === 'saved' && <Chip color="success" label="Saved ✓" size="small" />}
            {saveState === 'error' && <Chip color="error" label="Save failed" size="small" />}
          </Stack>
        </Stack>

        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((step) => (
            <Step key={step.label}>
              <StepLabel>{step.label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box>
          {activeStep === 0 && <DietStep diets={diets} />}
          {activeStep === 1 && <CultureStep cultures={cultures} />}
          {activeStep === 2 && <GoalsStep />}
          {activeStep === 3 && <LocationStep />}
          {activeStep === 4 && <ScheduleStep />}
          {activeStep === 5 && <AllergiesStep />}
        </Box>

        <Divider />

        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Button onClick={handleBack} disabled={activeStep === 0 || isGenerating} variant="text">
            Back
          </Button>
          <Stack direction="row" spacing={2} alignItems="center">
            <Button
              onClick={handleNext}
              disabled={activeStep === steps.length - 1 || isGenerating}
              variant="text"
            >
              Next
            </Button>
            <Button
              variant="contained"
              onClick={handleGenerate}
              disabled={isPending || isGenerating}
            >
              Generate My First Week
            </Button>
          </Stack>
        </Stack>

        {saveState === 'error' && (
          <Alert severity="warning">Your changes were not saved. Check your connection and retry.</Alert>
        )}

        <Backdrop sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }} open={isGenerating}>
          <Stack spacing={2} alignItems="center">
            <CircularProgress color="inherit" />
            <Typography variant="h6">Creating your personalised plan…</Typography>
            <Typography variant="body2">We will redirect you once your meals are ready.</Typography>
          </Stack>
        </Backdrop>

        <Snackbar
          open={Boolean(snackbarMessage)}
          autoHideDuration={4000}
          onClose={() => setSnackbarMessage(null)}
          message={snackbarMessage}
        />
      </Stack>
    </FormProvider>
  );
};

const DietStep = ({ diets }: { diets: DietOption[] }) => {
  const { control, setValue } = useFormContext<PreferencesFormValues>();
  const selectedDiet = useWatch({ control, name: 'dietId' });
  const disliked = useWatch({ control, name: 'dislikedIngredients' }) ?? [];
  const [inputValue, setInputValue] = useState('');
  const [showAvoid, setShowAvoid] = useState(disliked.length > 0);
  const carouselRef = useRef<HTMLDivElement | null>(null);
  const [atStart, setAtStart] = useState(true);
  const [atEnd, setAtEnd] = useState(false);

  const options = useMemo(
    () =>
      diets.map((diet) => ({
        ...diet,
        description: DIET_DESCRIPTIONS[diet.id] ?? 'Personalised recommendations.',
        image: DIET_IMAGES[diet.id] ?? DEFAULT_DIET_IMAGE
      })),
    [diets]
  );

  useEffect(() => {
    const element = carouselRef.current;
    if (!element) return;

    const updateScrollState = () => {
      setAtStart(element.scrollLeft <= 32);
      setAtEnd(element.scrollLeft + element.clientWidth >= element.scrollWidth - 32);
    };

    updateScrollState();
    element.addEventListener('scroll', updateScrollState, { passive: true });
    const resize = () => updateScrollState();
    window.addEventListener('resize', resize);
    return () => {
      element.removeEventListener('scroll', updateScrollState);
      window.removeEventListener('resize', resize);
    };
  }, [options.length]);

  useEffect(() => {
    if (disliked.length && !showAvoid) {
      setShowAvoid(true);
    }
  }, [disliked.length, showAvoid]);

  const handleScroll = (direction: 'left' | 'right') => {
    const element = carouselRef.current;
    if (!element) return;
    const scrollAmount = element.clientWidth * 0.8;
    element.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    });
  };

  const handleSelect = (dietId: string) => {
    if (dietId !== selectedDiet) {
      setValue('dietId', dietId, { shouldDirty: true });
    }
  };

  const handleAdd = () => {
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    const next = Array.from(new Set([...disliked, trimmed]));
    setValue('dislikedIngredients', next, { shouldDirty: true });
    setInputValue('');
  };

  const handleDelete = (value: string) => {
    const next = disliked.filter((item) => item !== value);
    setValue('dislikedIngredients', next, { shouldDirty: true });
  };

  return (
    <Stack spacing={3}>
      <Stack spacing={1}>
        <Typography variant="subtitle1">Your diet</Typography>
        <Typography variant="body2" color="text.secondary">
          Choose the pattern that matches your everyday eating habits.
        </Typography>
      </Stack>

      <Box position="relative" sx={{ px: { xs: 2, sm: 4 } }}>
        <IconButton
          onClick={() => handleScroll('left')}
          disabled={atStart}
          sx={{
            position: 'absolute',
            left: { xs: 4, sm: 8 },
            top: '50%',
            transform: 'translateY(-50%)',
            bgcolor: 'background.paper',
            boxShadow: 3,
            zIndex: 2,
            display: { xs: 'flex', md: 'inline-flex' }
          }}
          aria-label="Scroll left"
        >
          <ChevronLeftIcon />
        </IconButton>
        <Box
          ref={carouselRef}
          sx={{
            display: 'flex',
            gap: 3,
            overflowX: 'auto',
            scrollSnapType: 'x mandatory',
            scrollPadding: '0 32px',
            py: 1.5,
            '&::-webkit-scrollbar': { display: 'none' },
            scrollbarWidth: 'none'
          }}
        >
          {options.map((option) => {
            const isSelected = option.id === selectedDiet;
            return (
              <ButtonBase
                key={option.id}
                focusRipple
                onClick={() => handleSelect(option.id)}
                sx={(theme) => ({
                  flex: { xs: '0 0 85%', sm: '0 0 320px', md: '0 0 340px' },
                  maxWidth: { xs: '100%', sm: 340 },
                  borderRadius: 3,
                  overflow: 'hidden',
                  textAlign: 'left',
                  border: '2px solid',
                  borderColor: isSelected ? theme.palette.primary.main : 'transparent',
                  backgroundColor: theme.palette.background.paper,
                  boxShadow: isSelected ? theme.shadows[6] : theme.shadows[2],
                  scrollSnapAlign: 'center',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignSelf: 'stretch',
                  '.MuiTouchRipple-root': { color: theme.palette.primary.main },
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.shadows[6]
                  }
                })}
              >
                <Box
                  sx={{
                    height: { xs: 180, sm: 190 },
                    width: '100%',
                    backgroundImage: `url(${option.image})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center'
                  }}
                />
                <Stack spacing={1.5} sx={{ p: 2 }}>
                  <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                    <Typography variant="subtitle1" fontWeight={600}>
                      {option.name}
                    </Typography>
                    {isSelected && <Chip size="small" color="primary" label="Selected" />}
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {option.description}
                  </Typography>
                  <Typography variant="caption" color="text.disabled">
                    Click to set this as your default diet preference.
                  </Typography>
                </Stack>
              </ButtonBase>
            );
          })}
        </Box>
        <IconButton
          onClick={() => handleScroll('right')}
          disabled={atEnd}
          sx={{
            position: 'absolute',
            right: { xs: 4, sm: 8 },
            top: '50%',
            transform: 'translateY(-50%)',
            bgcolor: 'background.paper',
            boxShadow: 3,
            zIndex: 2,
            display: { xs: 'flex', md: 'inline-flex' }
          }}
          aria-label="Scroll right"
        >
          <ChevronRightIcon />
        </IconButton>
      </Box>

      <Stack spacing={1}>
        <FormControlLabel
          control={
            <Switch
              checked={showAvoid}
              onChange={(_, checked) => {
                setShowAvoid(checked);
                if (!checked) {
                  setValue('dislikedIngredients', [], { shouldDirty: true });
                }
              }}
            />
          }
          label="Avoid specific foods"
        />
        {showAvoid && (
          <>
            <Stack direction="row" spacing={1} alignItems="center">
              <TextField
                size="small"
                label="Add ingredient to avoid"
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    handleAdd();
                  }
                }}
              />
              <Button variant="outlined" onClick={handleAdd}>
                Add
              </Button>
            </Stack>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {disliked.map((item) => (
                <Chip key={item} label={item} onDelete={() => handleDelete(item)} />
              ))}
            </Stack>
          </>
        )}
      </Stack>
    </Stack>
  );
};

const CultureStep = ({ cultures }: { cultures: CultureOption[] }) => {
  const { control } = useFormContext<PreferencesFormValues>();
  const options = useMemo(
    () =>
      (cultures.length ? cultures : FALLBACK_CULTURES)
        .map((culture) => ({
          id: culture.id,
          label: `${flagFromCode(culture.region_code)} ${culture.name}`,
          region: REGION_LABELS[REGION_FROM_CODE[culture.region_code] ?? culture.region_code] ?? 'Global'
        }))
        .sort((a, b) => a.label.localeCompare(b.label)),
    [cultures]
  );

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1">Your cultural cuisine</Typography>
      <Typography variant="body2" color="text.secondary">
        We will source recipes inspired by your heritage and adapt them to your current pantry. Select more than one if you have a mixed background — the first choice becomes your primary cuisine.
      </Typography>
      <Controller
        control={control}
        name="cultureIds"
        render={({ field, fieldState }) => (
          <Autocomplete
            multiple
            options={options}
            disableCloseOnSelect
            value={options.filter((option) => field.value?.includes(option.id))}
            onChange={(_, selected) => field.onChange(selected.map((option) => option.id))}
            groupBy={(option) => option.region}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Cultural cuisines"
                error={Boolean(fieldState.error)}
                helperText={fieldState.error?.message ?? 'Pick one or more cuisines; we will prioritise the first selection.'}
              />
            )}
          />
        )}
      />
    </Stack>
  );
};

const GoalsStep = () => {
  const { control, setValue } = useFormContext<PreferencesFormValues>();
  const goals = useWatch({ control, name: 'dietaryGoals' }) ?? [];

  const toggleGoal = (id: string) => {
    const set = new Set(goals);
    if (set.has(id)) {
      set.delete(id);
    } else {
      set.add(id);
    }
    setValue('dietaryGoals', Array.from(set), { shouldDirty: true });
  };

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1">Your dietary goals</Typography>
      <Typography variant="body2" color="text.secondary">
        Pick one or more goals so we can fine-tune your plan.
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap">
        {GOAL_OPTIONS.map((goal) => (
          <Chip
            key={goal.id}
            label={goal.label}
            variant={goals.includes(goal.id) ? 'filled' : 'outlined'}
            color={goals.includes(goal.id) ? 'primary' : 'default'}
            onClick={() => toggleGoal(goal.id)}
            sx={{ mr: 1, mb: 1 }}
          />
        ))}
      </Stack>
    </Stack>
  );
};

const LocationStep = () => {
  const { control, setValue } = useFormContext<PreferencesFormValues>();
  const [detecting, setDetecting] = useState(false);

  const handleDetect = () => {
    if (!navigator.geolocation) {
      return;
    }
    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = `${position.coords.latitude.toFixed(2)}, ${position.coords.longitude.toFixed(2)}`;
        setValue('city', coords, { shouldDirty: true });
        setDetecting(false);
      },
      () => setDetecting(false),
      { enableHighAccuracy: false, timeout: 5000 }
    );
  };

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1">Where do you live now?</Typography>
      <Typography variant="body2" color="text.secondary">
        We adapt ingredients and shopping lists to your local stores and measurement units.
      </Typography>

      <Controller
        control={control}
        name="country"
        render={({ field }) => (
          <TextField select label="Country" {...field}>
            {COUNTRY_OPTIONS.map((country) => (
              <MenuItem key={country.id} value={country.id}>
                {country.label}
              </MenuItem>
            ))}
          </TextField>
        )}
      />

      <Controller
        control={control}
        name="city"
        render={({ field }) => (
          <TextField label="City" placeholder="e.g. Berlin" {...field} />
        )}
      />

      <Button variant="outlined" onClick={handleDetect} disabled={detecting}>
        {detecting ? 'Detecting location…' : 'Use current location'}
      </Button>
    </Stack>
  );
};

const ScheduleStep = () => {
  const { control } = useFormContext<PreferencesFormValues>();

  return (
    <Stack spacing={3}>
      <Typography variant="subtitle1">Portion & schedule preferences</Typography>
      <Controller
        control={control}
        name="householdSize"
        render={({ field }) => (
          <TextField
            label="Household size"
            type="number"
            inputProps={{ min: 1, max: 10 }}
            {...field}
          />
        )}
      />
      <Controller
        control={control}
        name="mealsPerDay"
        render={({ field }) => (
          <TextField
            label="Meals per day"
            type="number"
            inputProps={{ min: 1, max: 6 }}
            {...field}
          />
        )}
      />
      <Stack spacing={1}>
        <Typography variant="body2">Cooking time limit (minutes)</Typography>
        <Controller
          control={control}
          name="cookingTimeLimit"
          render={({ field }) => (
            <Slider
              value={field.value}
              onChange={(_, value) => {
                const next = Array.isArray(value) ? value[0] : value;
                field.onChange(next);
              }}
              step={5}
              min={15}
              max={90}
              valueLabelDisplay="auto"
            />
          )}
        />
      </Stack>
    </Stack>
  );
};

const AllergiesStep = () => {
  const { control, setValue } = useFormContext<PreferencesFormValues>();
  const allergies = useWatch({ control, name: 'allergies' }) ?? [];
  const [otherAllergy, setOtherAllergy] = useState('');

  const toggleAllergy = (value: string) => {
    const set = new Set(allergies);
    if (set.has(value)) {
      set.delete(value);
    } else {
      set.add(value);
    }
    setValue('allergies', Array.from(set), { shouldDirty: true });
  };

  const addOther = () => {
    const trimmed = otherAllergy.trim();
    if (!trimmed) return;
    toggleAllergy(trimmed.toLowerCase());
    setOtherAllergy('');
  };

  return (
    <Stack spacing={2}>
      <Typography variant="subtitle1">Allergies & intolerances</Typography>
      <FormGroup>
        {ALLERGY_OPTIONS.map((option) => (
          <FormControlLabel
            key={option}
            control={<Switch checked={allergies.includes(option)} onChange={() => toggleAllergy(option)} />}
            label={option.charAt(0).toUpperCase() + option.slice(1)}
          />
        ))}
      </FormGroup>
      <Stack direction="row" spacing={1} alignItems="center">
        <TextField
          size="small"
          label="Other"
          placeholder="e.g. Sesame"
          value={otherAllergy}
          onChange={(event) => setOtherAllergy(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault();
              addOther();
            }
          }}
        />
        <Button variant="outlined" onClick={addOther}>
          Add
        </Button>
      </Stack>
      <Stack direction="row" spacing={1} flexWrap="wrap">
        {allergies.map((item) => (
          <Chip key={item} label={item} onDelete={() => toggleAllergy(item)} />
        ))}
      </Stack>
    </Stack>
  );
};

export default PreferencesForm;
