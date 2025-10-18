import type { PreferencesFormValues } from '../../features/preferences/PreferencesForm';

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

export const api = {
  fetchDiets: () => http<Array<{ id: number; name: string }>>(`${baseUrl}/diets`),
  fetchCultures: () => http<Array<{ id: number; name: string }>>(`${baseUrl}/cultures`),
  savePreferences: (payload: PreferencesFormValues) =>
    http(`${baseUrl}/user/preferences`, {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email,
        diet_id: payload.dietId,
        culture_id: payload.cultureId
      })
    }),
  getLatestMealPlan: () => http<MealPlanResponse | null>(`${baseUrl}/plans/latest`).catch(() => null),
  generatePlan: () =>
    http<MealPlanResponse>(`${baseUrl}/plans/generate`, {
      method: 'POST',
      body: JSON.stringify({ email: 'demo@example.com', diet_id: 1, culture_id: 1 })
    })
};
