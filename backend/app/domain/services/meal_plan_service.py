from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
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
    TodayMeal,
    TodayOverviewResponse,
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
    diet_id: str = "balanced"
    culture_id: str = "global"

    def to_response(self) -> MealPlanResponse:
        return MealPlanResponse(
            id=self.id,
            user_email=self.user_email,
            week_start=self.week_start,
            diet_id=self.diet_id,
            culture_id=self.culture_id,
            meals=self.meals,
            shopping_list=self.shopping_list,
            summary=self.summary,
            warnings=self.warnings,
            status=self.status,
        )


class MealPlanService:
    """Simple in-memory service representing the design's domain service layer."""

    _MEAL_ORDER = [
        "breakfast",
        "brunch",
        "lunch",
        "snack",
        "tea",
        "dinner",
        "late-night",
    ]

    _DEFAULT_SCHEDULE: Dict[str, time] = {
        "breakfast": time(8, 0),
        "brunch": time(10, 30),
        "lunch": time(13, 0),
        "snack": time(16, 0),
        "tea": time(17, 0),
        "dinner": time(19, 0),
        "late-night": time(21, 30),
    }

    def __init__(
        self,
        storage: Dict[UUID, MealPlanRecord],
        generator: MealPlanGenerator,
        fallback_generator: MealPlanGenerator | None = None,
    ):
        self._storage = storage
        self._last_created_id: UUID | None = None
        self._generator = generator
        self._latest_by_user: Dict[str, UUID] = {}
        self._fallback_generator = fallback_generator

    @classmethod
    def create_in_memory(cls) -> "MealPlanService":
        stub = StubMealPlanGenerator()
        return cls(storage={}, generator=stub)

    @classmethod
    def create_with_generator(
        cls, generator: MealPlanGenerator, fallback: MealPlanGenerator | None = None
    ) -> "MealPlanService":
        return cls(storage={}, generator=generator, fallback_generator=fallback)

    def create_meal_plan(
        self, payload: MealPlanCreateRequest, *, preferences: UserPreferencesView | None = None
    ) -> MealPlanResponse:
        context = self._build_context(payload, preferences)

        try:
            generation = self._generator.generate(context)
        except MealPlanGenerationError as exc:
            if self._fallback_generator is not None:
                generation = self._fallback_generator.generate(context)
            else:
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
            diet_id=context.preferences.diet_id,
            culture_id=context.preferences.culture_id,
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

    def get_today_overview(
        self, email: str | None = None, *, now: datetime | None = None
    ) -> Optional[TodayOverviewResponse]:
        record = self._get_latest_record(email)
        if not record:
            return None

        current_datetime = now or datetime.now()
        today = current_datetime.date()
        weekday = today.strftime("%A").lower()
        day_meals = [meal for meal in record.meals if meal.day_of_week.lower() == weekday]
        if not day_meals:
            return None

        ordered_meals = sorted(day_meals, key=self._meal_sort_key)
        current_time = current_datetime.time()

        timeline: list[tuple[MealItem, time, str]] = []
        next_index: int | None = None
        for idx, meal in enumerate(ordered_meals):
            scheduled = self._scheduled_time_for(meal.meal_type)
            status = "upcoming"
            if scheduled <= current_time:
                status = "completed"
            timeline.append((meal, scheduled, status))
            if status == "upcoming" and next_index is None:
                next_index = idx

        if next_index is None:
            next_index = len(timeline) - 1

        meals_response: list[TodayMeal] = []
        current_meal: TodayMeal | None = None

        for idx, (meal, scheduled, status) in enumerate(timeline):
            is_current = idx == next_index
            final_status = "current" if is_current else status
            meal_label = meal.meal_type.replace("_", " ").title()
            scheduled_label = scheduled.strftime("%H:%M")
            today_meal = TodayMeal(
                meal_type=meal.meal_type,
                meal_label=meal_label,
                recipe_title=meal.recipe_title,
                instructions=meal.instructions,
                scheduled_time=scheduled_label,
                status=final_status,
                is_current=is_current,
            )
            meals_response.append(today_meal)
            if is_current:
                current_meal = today_meal

        greeting = self._greeting_for_time(current_time)

        return TodayOverviewResponse(
            date=today,
            greeting=greeting,
            diet_id=record.diet_id,
            culture_id=record.culture_id,
            plan_status=record.status,
            current_meal=current_meal,
            meals=meals_response,
        )

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

    def _get_latest_record(self, email: str | None) -> MealPlanRecord | None:
        if email:
            record_id = self._latest_by_user.get(email.lower())
            if not record_id:
                return None
            return self._storage.get(record_id)
        if not self._last_created_id:
            return None
        return self._storage.get(self._last_created_id)

    def _meal_order_index(self, meal_type: str) -> int:
        try:
            return self._MEAL_ORDER.index(meal_type.lower())
        except ValueError:
            return len(self._MEAL_ORDER)

    def _meal_sort_key(self, meal: MealItem) -> tuple[int, str]:
        return (self._meal_order_index(meal.meal_type), meal.meal_type)

    def _scheduled_time_for(self, meal_type: str) -> time:
        key = meal_type.lower()
        return self._DEFAULT_SCHEDULE.get(key, time(18, 0))

    def _greeting_for_time(self, current: time) -> str:
        if current < time(12, 0):
            return "Good morning"
        if current < time(17, 0):
            return "Good afternoon"
        if current < time(22, 0):
            return "Good evening"
        return "Good night"
