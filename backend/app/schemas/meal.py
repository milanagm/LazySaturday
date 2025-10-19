from datetime import date
from uuid import UUID

from typing import Any

from pydantic import BaseModel, EmailStr, Field

from .user import UserPreferencesView


class MealInstruction(BaseModel):
    step_number: int = Field(ge=1)
    description: str
    duration_minutes: int | None = Field(default=None, ge=0)


class MealIngredient(BaseModel):
    name: str
    quantity: float | None = Field(default=None, ge=0.0)
    unit: str | None = None
    notes: str | None = None


class MealNutrition(BaseModel):
    calories: int | None = Field(default=None, ge=0)
    protein_g: float | None = Field(default=None, ge=0.0)
    carbs_g: float | None = Field(default=None, ge=0.0)
    fats_g: float | None = Field(default=None, ge=0.0)
    fiber_g: float | None = Field(default=None, ge=0.0)
    micronutrients: dict[str, float] = Field(default_factory=dict)


class MealItem(BaseModel):
    day_of_week: str
    meal_type: str
    recipe_title: str
    instructions: str = ""
    recipe_id: str | None = None
    ingredients: list[MealIngredient] = Field(default_factory=list)
    instruction_steps: list[MealInstruction] = Field(default_factory=list)
    nutrition: MealNutrition | None = None
    prep_time_minutes: int | None = Field(default=None, ge=0)
    cook_time_minutes: int | None = Field(default=None, ge=0)
    source: str | None = None
    tags: list[str] = Field(default_factory=list)


class ShoppingListItem(BaseModel):
    name: str
    quantity: str
    category: str | None = None
    unit: str | None = None
    notes: str | None = None
    is_pantry: bool = False


class MealPlanSummary(BaseModel):
    overview: str
    calorie_total: int | None = Field(default=None, ge=0)
    macro_totals: MealNutrition | None = None
    allergy_warnings: list[str] = Field(default_factory=list)
    variety_score: float | None = Field(default=None, ge=0.0)


class MealPlanWarning(BaseModel):
    code: str
    message: str
    blocking: bool = False


class MealPlanResponse(BaseModel):
    id: UUID
    user_email: str
    week_start: date
    diet_id: str
    culture_id: str
    meals: list[MealItem] = Field(default_factory=list)
    shopping_list: list[ShoppingListItem] = Field(default_factory=list)
    summary: MealPlanSummary | None = None
    warnings: list[MealPlanWarning] = Field(default_factory=list)
    status: str = "draft"


class MealPlanCreateRequest(BaseModel):
    email: EmailStr
    diet_id: str
    culture_id: str
    request_id: UUID | None = None
    preferences_override: UserPreferencesView | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TodayMeal(BaseModel):
    meal_type: str
    meal_label: str
    recipe_title: str
    instructions: str
    scheduled_time: str
    status: str
    is_current: bool


class TodayOverviewResponse(BaseModel):
    date: date
    greeting: str
    diet_id: str
    culture_id: str
    plan_status: str
    current_meal: TodayMeal | None
    meals: list[TodayMeal]
    tomorrow_preview: TodayMeal | None = None
    upcoming_days: list[dict[str, Any]] = Field(default_factory=list)
