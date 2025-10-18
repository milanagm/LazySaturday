from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional
from uuid import UUID, uuid4

from ...schemas.meal import (
    MealIngredient,
    MealInstruction,
    MealItem,
    MealNutrition,
    MealPlanCreateRequest,
    MealPlanResponse,
    MealPlanSummary,
    MealPlanWarning,
    ShoppingListItem,
)
from ...schemas.user import UserPreferencesView
from ..meal_planning.contracts import (
    GeneratedMeal,
    MealPlanGenerationContext,
    MealPlanGenerationError,
    MealPlanGenerationResult,
    MealPlanGenerator,
    PreviousPlanSummary,
    ResultWarning,
    ShoppingListEntry as GeneratorShoppingListEntry,
)
from ..meal_planning.stub_generator import StubMealPlanGenerator


@dataclass
class MealPlanRecord:
    id: UUID
    user_email: str
    week_start: date
    meals: list[MealItem] = field(default_factory=list)
    shopping_list: list[ShoppingListItem] = field(default_factory=list)
    summary: MealPlanSummary | None = None
    warnings: list[MealPlanWarning] = field(default_factory=list)
    status: str = "draft"

    def to_response(self) -> MealPlanResponse:
        return MealPlanResponse(
            id=self.id,
            user_email=self.user_email,
            week_start=self.week_start,
            meals=self.meals,
            shopping_list=self.shopping_list,
            summary=self.summary,
            warnings=self.warnings,
            status=self.status,
        )


class MealPlanService:
    """Simple in-memory service representing the design's domain service layer."""

    def __init__(self, storage: Dict[UUID, MealPlanRecord], generator: MealPlanGenerator):
        self._storage = storage
        self._last_created_id: UUID | None = None
        self._generator = generator
        self._latest_by_user: Dict[str, UUID] = {}

    @classmethod
    def create_in_memory(cls) -> "MealPlanService":
        return cls(storage={}, generator=StubMealPlanGenerator())

    def create_meal_plan(
        self, payload: MealPlanCreateRequest, *, preferences: UserPreferencesView | None = None
    ) -> MealPlanResponse:
        context = self._build_context(payload, preferences)

        try:
            generation = self._generator.generate(context)
        except MealPlanGenerationError as exc:
            raise ValueError(f"Unable to generate meal plan: {exc.code}") from exc

        plan_id = generation.plan_id or uuid4()
        meals = [self._map_generated_meal(meal) for meal in generation.meals]
        shopping_list = [self._map_shopping_list_entry(entry) for entry in generation.shopping_list]
        summary = self._map_summary(generation)
        warnings = [self._map_warning(warning) for warning in generation.warnings]

        record = MealPlanRecord(
            id=plan_id,
            user_email=context.user_email,
            week_start=context.week_start,
            meals=meals,
            shopping_list=shopping_list,
            summary=summary,
            warnings=warnings,
            status=generation.status,
        )
        self._storage[plan_id] = record
        self._last_created_id = plan_id
        self._latest_by_user[record.user_email.lower()] = plan_id
        return record.to_response()

    def get_meal_plan(self, plan_id: str) -> Optional[MealPlanResponse]:
        try:
            uid = UUID(plan_id)
        except ValueError:
            return None
        record = self._storage.get(uid)
        return record.to_response() if record else None

    def get_latest(self, email: str | None = None) -> Optional[MealPlanResponse]:
        if email:
            record_id = self._latest_by_user.get(email.lower())
            if not record_id:
                return None
            record = self._storage.get(record_id)
            return record.to_response() if record else None
        if not self._last_created_id:
            return None
        record = self._storage.get(self._last_created_id)
        return record.to_response() if record else None

    def _build_context(
        self, payload: MealPlanCreateRequest, preferences: UserPreferencesView | None
    ) -> MealPlanGenerationContext:
        email = payload.email.lower()
        pref_snapshot = preferences or self._build_default_preferences(payload)
        previous_summary: PreviousPlanSummary | None = None
        previous_id = self._latest_by_user.get(email)
        if previous_id:
            previous_record = self._storage.get(previous_id)
            if previous_record:
                previous_summary = PreviousPlanSummary(
                    plan_id=previous_record.id,
                    generated_at=None,
                    review_notes=None,
                    satisfaction_score=None,
                )

        request_id = payload.request_id or uuid4()
        return MealPlanGenerationContext(
            request_id=request_id,
            user_email=email,
            week_start=date.today(),
            preferences=pref_snapshot,
            previous_plan=previous_summary,
            metadata=dict(payload.metadata),
        )

    def _build_default_preferences(self, payload: MealPlanCreateRequest) -> UserPreferencesView:
        return UserPreferencesView(
            email=payload.email.lower(),
            diet_id=payload.diet_id,
            culture_id=payload.culture_id,
            additional_cultures=[],
            country="unknown",
            city=None,
            dietary_goals=[],
            allergies=[],
            disliked_ingredients=[],
            meals_per_day=3,
            household_size=1,
            cooking_time_limit=30,
        )

    def _map_generated_meal(self, meal: GeneratedMeal) -> MealItem:
        instructions = "\n".join(step.description for step in meal.instructions) if meal.instructions else ""
        nutrition = None
        if meal.nutrition:
            nutrition = MealNutrition(
                calories=meal.nutrition.calories,
                protein_g=meal.nutrition.protein_g,
                carbs_g=meal.nutrition.carbs_g,
                fats_g=meal.nutrition.fats_g,
                fiber_g=meal.nutrition.fiber_g,
                micronutrients=meal.nutrition.micronutrients,
            )

        return MealItem(
            day_of_week=meal.day_of_week,
            meal_type=meal.meal_type,
            recipe_title=meal.recipe_title,
            instructions=instructions,
            recipe_id=meal.recipe_id,
            ingredients=[
                MealIngredient(name=component.name, quantity=component.quantity, unit=component.unit, notes=component.notes)
                for component in meal.ingredients
            ],
            instruction_steps=[
                MealInstruction(
                    step_number=step.step_number,
                    description=step.description,
                    duration_minutes=step.duration_minutes,
                )
                for step in meal.instructions
            ],
            nutrition=nutrition,
            prep_time_minutes=meal.prep_time_minutes,
            cook_time_minutes=meal.cook_time_minutes,
            source=meal.source,
            tags=meal.tags,
        )

    def _map_shopping_list_entry(
        self, entry: GeneratorShoppingListEntry
    ) -> ShoppingListItem:
        quantity_value = float(entry.quantity)
        quantity_repr = f"{quantity_value:g}"
        if entry.unit:
            quantity_repr = f"{quantity_repr} {entry.unit}"
        return ShoppingListItem(
            name=entry.name,
            quantity=quantity_repr,
            category=entry.category,
            unit=entry.unit,
            notes=entry.notes,
            is_pantry=entry.is_pantry,
        )

    def _map_summary(self, generation: MealPlanGenerationResult) -> MealPlanSummary | None:
        if not generation.summary:
            return None
        macro_totals = None
        if generation.summary.macro_totals:
            macro_totals = MealNutrition(
                calories=generation.summary.macro_totals.calories,
                protein_g=generation.summary.macro_totals.protein_g,
                carbs_g=generation.summary.macro_totals.carbs_g,
                fats_g=generation.summary.macro_totals.fats_g,
                fiber_g=generation.summary.macro_totals.fiber_g,
                micronutrients=generation.summary.macro_totals.micronutrients,
            )

        return MealPlanSummary(
            overview=generation.summary.overview,
            calorie_total=generation.summary.calorie_total,
            macro_totals=macro_totals,
            allergy_warnings=generation.summary.allergy_warnings,
            variety_score=generation.summary.variety_score,
        )

    def _map_warning(self, warning: ResultWarning) -> MealPlanWarning:
        return MealPlanWarning(code=warning.code, message=warning.message, blocking=warning.blocking)
