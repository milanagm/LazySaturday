const baseUrl = '/api';

async function http<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export interface MealPlanItem {
  day_of_week: string;
  meal_type: string;
  recipe_title: string;
  instructions: string;
}

export interface ShoppingListItem {
  name: string;
  quantity: string;
}

export interface MealPlanResponse {
  id: string;
  user_email: string;
  week_start: string;
  meals: MealPlanItem[];
  shopping_list: ShoppingListItem[];
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

export const api = {
  fetchDiets: () => http<DietOption[]>(`${baseUrl}/diets`),
  fetchCultures: () => http<CultureOption[]>(`${baseUrl}/cultures`),
  savePreferences: (payload: PreferencesPayload) =>
    http<SavePreferencesResponse>(`${baseUrl}/user/preferences`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  getPreferences: (email: string) =>
    http<PreferencesPayload | null>(`${baseUrl}/user/preferences?email=${encodeURIComponent(email)}`),
  getLatestMealPlan: () => http<MealPlanResponse | null>(`${baseUrl}/plans/latest`).catch(() => null),
  generatePlan: (payload: { email: string; diet_id: string; culture_id: string }) =>
    http<MealPlanResponse>(`${baseUrl}/plans/generate`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};
