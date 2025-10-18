from __future__ import annotations

from uuid import UUID, uuid4

from .contracts import (
    GeneratedMeal,
    IngredientComponent,
    InstructionStep,
    MealPlanGenerationContext,
    MealPlanGenerationResult,
    MealPlanGenerator,
    NutritionBreakdown,
    PlanSummary,
    ShoppingListEntry,
)


class StubMealPlanGenerator(MealPlanGenerator):
    """Deterministic generator used for development and unit tests."""

    def generate(self, context: MealPlanGenerationContext) -> MealPlanGenerationResult:
        culture_label = context.preferences.culture_id.replace("_", " ").title()
        base_recipe_title = f"{culture_label} inspired"
        meals: list[GeneratedMeal] = []

        for idx, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], start=1):
            meals.append(
                GeneratedMeal(
                    day_of_week=day,
                    meal_type="dinner",
                    recipe_id=f"{context.preferences.culture_id}-{idx}",
                    recipe_title=f"{base_recipe_title} {day} special",
                    ingredients=[
                        IngredientComponent(name="Chickpeas", quantity=0.5, unit="kg"),
                        IngredientComponent(name="Spinach", quantity=0.3, unit="kg"),
                    ],
                    instructions=[
                        InstructionStep(step_number=1, description="Rinse ingredients."),
                        InstructionStep(step_number=2, description="Cook thoroughly.", duration_minutes=context.preferences.cooking_time_limit),
                    ],
                    nutrition=NutritionBreakdown(
                        calories=600,
                        protein_g=25.0,
                        carbs_g=70.0,
                        fats_g=20.0,
                        fiber_g=12.0,
                        micronutrients={"iron_mg": 5.0},
                    ),
                    prep_time_minutes=15,
                    cook_time_minutes=min(context.preferences.cooking_time_limit, 45),
                    source="stub",
                    tags=[context.preferences.diet_id, culture_label.lower()],
                )
            )

        shopping_list = [
            ShoppingListEntry(category="pantry", name="Chickpeas", quantity=2.0, unit="cans"),
            ShoppingListEntry(category="produce", name="Spinach", quantity=0.5, unit="kg"),
        ]

        summary = PlanSummary(
            overview=f"Stub meal plan for {context.user_email} with {culture_label} flair.",
            calorie_total=sum(meal.nutrition.calories for meal in meals if meal.nutrition),
            macro_totals=NutritionBreakdown(
                calories=sum(meal.nutrition.calories for meal in meals if meal.nutrition),
                protein_g=sum(meal.nutrition.protein_g for meal in meals if meal.nutrition),
                carbs_g=sum(meal.nutrition.carbs_g for meal in meals if meal.nutrition),
                fats_g=sum(meal.nutrition.fats_g for meal in meals if meal.nutrition),
                fiber_g=sum(meal.nutrition.fiber_g or 0.0 for meal in meals if meal.nutrition),
            ),
            allergy_warnings=[],
            variety_score=0.5,
        )

        # Deterministic plan identifier when input metadata requests it; fallback to generated UUID.
        plan_identifier = context.metadata.get("plan_id_override")
        plan_uuid = uuid4()
        if isinstance(plan_identifier, UUID):
            plan_uuid = plan_identifier
        elif isinstance(plan_identifier, str):
            try:
                plan_uuid = UUID(plan_identifier)
            except ValueError:
                plan_uuid = uuid4()

        return MealPlanGenerationResult(
            plan_id=plan_uuid,
            meals=meals,
            shopping_list=shopping_list,
            summary=summary,
            status="ready",
        )
