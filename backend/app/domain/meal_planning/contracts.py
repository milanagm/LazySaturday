from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from ...schemas.user import UserPreferencesView


class MacroSplit(BaseModel):
    protein_percentage: float = Field(ge=0.0, le=100.0)
    fat_percentage: float = Field(ge=0.0, le=100.0)
    carb_percentage: float = Field(ge=0.0, le=100.0)

    class Config:
        extra = "forbid"


class NutritionBreakdown(BaseModel):
    calories: int = Field(ge=0)
    protein_g: float = Field(ge=0.0)
    carbs_g: float = Field(ge=0.0)
    fats_g: float = Field(ge=0.0)
    fiber_g: Optional[float] = Field(default=None, ge=0.0)
    micronutrients: Dict[str, float] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class InstructionStep(BaseModel):
    step_number: int = Field(ge=1)
    description: str
    duration_minutes: Optional[int] = Field(default=None, ge=0)

    class Config:
        extra = "forbid"


class IngredientComponent(BaseModel):
    name: str
    quantity: float = Field(ge=0.0)
    unit: str
    notes: Optional[str] = None

    class Config:
        extra = "forbid"


class GeneratedMeal(BaseModel):
    day_of_week: str
    meal_type: str
    recipe_id: Optional[str] = None
    recipe_title: str
    ingredients: List[IngredientComponent] = Field(default_factory=list)
    instructions: List[InstructionStep] = Field(default_factory=list)
    nutrition: Optional[NutritionBreakdown] = None
    prep_time_minutes: Optional[int] = Field(default=None, ge=0)
    cook_time_minutes: Optional[int] = Field(default=None, ge=0)
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class ShoppingListEntry(BaseModel):
    category: Optional[str] = None
    name: str
    quantity: float = Field(ge=0.0)
    unit: str
    notes: Optional[str] = None
    is_pantry: bool = False

    class Config:
        extra = "forbid"


class PlanSummary(BaseModel):
    overview: str
    calorie_total: Optional[int] = Field(default=None, ge=0)
    macro_totals: Optional[NutritionBreakdown] = None
    allergy_warnings: List[str] = Field(default_factory=list)
    variety_score: Optional[float] = Field(default=None, ge=0.0)

    class Config:
        extra = "forbid"


class ResultWarning(BaseModel):
    code: str
    message: str
    blocking: bool = False

    class Config:
        extra = "forbid"


class DiagnosticsPayload(BaseModel):
    prompt_versions: List[str] = Field(default_factory=list)
    rule_hits: List[str] = Field(default_factory=list)
    raw_context: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class PreviousPlanSummary(BaseModel):
    plan_id: UUID
    generated_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    satisfaction_score: Optional[float] = Field(default=None, ge=0.0, le=5.0)

    class Config:
        extra = "forbid"


class MealPlanGenerationContext(BaseModel):
    request_id: UUID
    user_email: EmailStr
    week_start: date
    preferences: UserPreferencesView
    previous_plan: Optional[PreviousPlanSummary] = None
    skipped_recipes: List[str] = Field(default_factory=list)
    manual_adjustments: List[str] = Field(default_factory=list)
    target_calories_per_day: Optional[int] = Field(default=None, ge=1200, le=5000)
    macro_split: Optional[MacroSplit] = None
    budget_per_week: Optional[float] = Field(default=None, ge=0.0)
    budget_currency: Optional[str] = None
    cooking_skill: Optional[str] = None
    delivery_mode: Optional[str] = None
    pantry_items: List[str] = Field(default_factory=list)
    timezone: Optional[str] = None
    locale: Optional[str] = None
    season: Optional[str] = None
    ingredients_availability: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "forbid"
        allow_mutation = False


class MealPlanGenerationResult(BaseModel):
    plan_id: Optional[UUID] = None
    meals: List[GeneratedMeal]
    shopping_list: List[ShoppingListEntry]
    summary: Optional[PlanSummary] = None
    warnings: List[ResultWarning] = Field(default_factory=list)
    diagnostics: Optional[DiagnosticsPayload] = None
    status: str = Field(default="ready")

    class Config:
        extra = "forbid"


class MealPlanGenerationError(Exception):
    """Raised when the generator cannot produce a valid meal plan."""

    def __init__(self, code: str, message: str, *, retryable: bool, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.details = details or {}


class MealPlanGenerator(Protocol):
    def generate(self, context: MealPlanGenerationContext) -> MealPlanGenerationResult:
        ...
