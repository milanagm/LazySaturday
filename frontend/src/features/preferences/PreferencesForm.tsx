import { useMemo } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button, MenuItem, Stack, TextField, Typography } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../../lib/api/client';

const schema = z.object({
  email: z.string().email(),
  dietId: z.number({ invalid_type_error: 'Select a diet' }),
  cultureId: z.number({ invalid_type_error: 'Select a culture' })
});

export type PreferencesFormValues = z.infer<typeof schema>;

const PreferencesForm = () => {
  const queryClient = useQueryClient();
  const { control, handleSubmit } = useForm<PreferencesFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', cultureId: 1, dietId: 1 }
  });

  const { data: diets = [] } = useQuery({ queryKey: ['diets'], queryFn: api.fetchDiets });
  const { data: cultures = [] } = useQuery({ queryKey: ['cultures'], queryFn: api.fetchCultures });

  const mutation = useMutation({
    mutationFn: api.savePreferences,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['meal-plan'] })
  });

  const selectProps = useMemo(
    () => ({ fullWidth: true, select: true, size: 'small' as const }),
    []
  );

  const onSubmit = (values: PreferencesFormValues) => {
    mutation.mutate(values);
  };

  return (
    <Stack component="form" spacing={2} onSubmit={handleSubmit(onSubmit)}>
      <Typography variant="h6">Set Preferences</Typography>
      <Controller
        control={control}
        name="email"
        render={({ field, fieldState }) => (
          <TextField
            label="Email"
            {...field}
            error={!!fieldState.error}
            helperText={fieldState.error?.message}
            fullWidth
            size="small"
            type="email"
          />
        )}
      />
      <Controller
        control={control}
        name="dietId"
        render={({ field, fieldState }) => (
          <TextField
            label="Diet"
            {...field}
            {...selectProps}
            value={field.value}
            onChange={(event) => field.onChange(Number(event.target.value))}
            error={!!fieldState.error}
          >
            {diets.map((diet) => (
              <MenuItem key={diet.id} value={diet.id}>
                {diet.name}
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <Controller
        control={control}
        name="cultureId"
        render={({ field, fieldState }) => (
          <TextField
            label="Culture"
            {...field}
            {...selectProps}
            value={field.value}
            onChange={(event) => field.onChange(Number(event.target.value))}
            error={!!fieldState.error}
          >
            {cultures.map((culture) => (
              <MenuItem key={culture.id} value={culture.id}>
                {culture.name}
              </MenuItem>
            ))}
          </TextField>
        )}
      />
      <Button variant="contained" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Saving…' : 'Save Preferences'}
      </Button>
    </Stack>
  );
};

export default PreferencesForm;
