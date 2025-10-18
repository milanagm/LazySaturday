const baseUrl = '/api';

let authToken: string | null = null;

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, message: string, data: unknown = undefined) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const setAuthToken = (token: string | null) => {
  authToken = token;
};

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(init?.headers ?? {})
  };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers
  });

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');

  if (!response.ok) {
    let errorBody: unknown;
    if (isJson) {
      try {
        errorBody = await response.json();
      } catch (error) {
        errorBody = null;
      }
    } else {
      const text = await response.text();
      errorBody = text || null;
    }

    const message =
      typeof errorBody === 'object' && errorBody && 'detail' in errorBody
        ? // eslint-disable-next-line @typescript-eslint/no-explicit-any
          (errorBody as any).detail ?? `Request failed with status ${response.status}`
        : `Request failed with status ${response.status}`;

    throw new ApiError(response.status, message, errorBody);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!isJson) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export interface MealInstruction {
  step_number: number;
  description: string;
  duration_minutes?: number | null;
}

export interface MealIngredient {
  name: string;
  quantity?: number | null;
  unit?: string | null;
  notes?: string | null;
}

export interface MealNutrition {
  calories?: number | null;
  protein_g?: number | null;
  carbs_g?: number | null;
  fats_g?: number | null;
  fiber_g?: number | null;
  micronutrients: Record<string, number>;
}

export interface MealPlanItem {
  day_of_week: string;
  meal_type: string;
  recipe_title: string;
  recipe_id?: string | null;
  instructions?: string;
  instruction_steps: MealInstruction[];
  ingredients: MealIngredient[];
  nutrition?: MealNutrition | null;
  prep_time_minutes?: number | null;
  cook_time_minutes?: number | null;
  source?: string | null;
  tags: string[];
}

export interface ShoppingListItem {
  name: string;
  quantity: string;
  category?: string | null;
  unit?: string | null;
  notes?: string | null;
  is_pantry: boolean;
}

export interface MealPlanSummary {
  overview: string;
  calorie_total?: number | null;
  macro_totals?: MealNutrition | null;
  allergy_warnings: string[];
  variety_score?: number | null;
}

export interface MealPlanWarning {
  code: string;
  message: string;
  blocking: boolean;
}

export interface MealPlanResponse {
  id: string;
  user_email: string;
  week_start: string;
  meals: MealPlanItem[];
  shopping_list: ShoppingListItem[];
  summary?: MealPlanSummary | null;
  warnings: MealPlanWarning[];
  status: string;
}

export interface DietOption {
  id: string;
  name: string;
}

export interface CultureOption {
  id: string;
  name: string;
  region_code: string;
}

export interface PreferencesPayload {
  email: string;
  diet_id: string;
  culture_id: string;
  additional_cultures: string[];
  country: string;
  city?: string | null;
  dietary_goals: string[];
  allergies: string[];
  disliked_ingredients: string[];
  meals_per_day: number;
  household_size: number;
  cooking_time_limit: number;
}

export interface SavePreferencesResponse {
  status: string;
  workflow_id: string;
  message: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: string;
  email: string;
  is_verified: boolean;
}

export interface AuthPayload {
  email: string;
  password: string;
}

export const api = {
  fetchDiets: () => http<DietOption[]>('/diets'),
  fetchCultures: () => http<CultureOption[]>('/cultures'),
  register: (payload: AuthPayload) =>
    http<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  login: (payload: AuthPayload) =>
    http<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify(payload) }),
  fetchProfile: () => http<UserProfile>('/auth/me'),
  savePreferences: (payload: PreferencesPayload) =>
    http<SavePreferencesResponse>('/user/preferences', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  getPreferences: () => http<PreferencesPayload | null>('/user/preferences'),
  getLatestMealPlan: () => http<MealPlanResponse | null>('/plans/latest').catch(() => null),
  generatePlan: (payload: { email: string; diet_id: string; culture_id: string }) =>
    http<MealPlanResponse>('/plans/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};
