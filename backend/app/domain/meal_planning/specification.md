# Meal Plan Generator Interface

This document defines the contract that an external meal plan generation service must implement to integrate with the Diet Planner backend. The `MealPlanService` builds a `MealPlanGenerationContext`, invokes the configured generator, and translates the returned `MealPlanGenerationResult` into the public `MealPlanResponse`.

## Input: `MealPlanGenerationContext`

The backend constructs the context per request. Generators must treat the payload as immutable.

```json
{
  "request_id": "c6ea9077-179e-4c18-8c9f-8d43b3ecc472",
  "user_email": "user@example.com",
  "week_start": "2024-05-06",
  "preferences": {
    "email": "user@example.com",
    "diet_id": "balanced",
    "culture_id": "indian",
    "additional_cultures": ["ethiopian"],
    "country": "US",
    "city": "New York",
    "dietary_goals": ["high_protein"],
    "allergies": ["peanut"],
    "disliked_ingredients": ["okra"],
    "meals_per_day": 3,
    "household_size": 2,
    "cooking_time_limit": 45
  },
  "previous_plan": {
    "plan_id": "0b4cd330-20ba-4bd5-932f-6db9118dad61",
    "generated_at": "2024-04-29T09:00:00Z",
    "review_notes": "User skipped Tuesday dinner",
    "satisfaction_score": 4.2
  },
  "skipped_recipes": ["ethiopian-3"],
  "manual_adjustments": ["Prefer lentils twice this week"],
  "target_calories_per_day": 2100,
  "macro_split": {
    "protein_percentage": 30.0,
    "fat_percentage": 25.0,
    "carb_percentage": 45.0
  },
  "budget_per_week": 120.0,
  "budget_currency": "USD",
  "cooking_skill": "intermediate",
  "delivery_mode": "fresh",
  "pantry_items": ["olive oil", "basmati rice"],
  "timezone": "America/New_York",
  "locale": "en-US",
  "season": "spring",
  "ingredients_availability": "farmer_market_focus",
  "metadata": {
    "feature_flag": "generator_v2",
    "experiment_bucket": "B"
  }
}
```

- `preferences` is the canonical snapshot gathered from the `UserPreferenceService`.
- `previous_plan` is omitted when unavailable.
- Generators may extend `metadata` with additional diagnostic keys when returning the result, but must not mutate the incoming object.

## Output: `MealPlanGenerationResult`

The generator must return a single `MealPlanGenerationResult`. Throw `MealPlanGenerationError` when the input cannot be fulfilled.

```json
{
  "plan_id": "6e3e5b63-5e7c-4bbe-8fdc-43b8a37f07cd",
  "meals": [
    {
      "day_of_week": "Monday",
      "meal_type": "dinner",
      "recipe_id": "indian-1",
      "recipe_title": "Indian inspired Monday special",
      "ingredients": [
        {"name": "Chickpeas", "quantity": 0.5, "unit": "kg"},
        {"name": "Spinach", "quantity": 0.3, "unit": "kg"}
      ],
      "instructions": [
        {"step_number": 1, "description": "Rinse ingredients."},
        {"step_number": 2, "description": "Simmer for 20 minutes.", "duration_minutes": 20}
      ],
      "nutrition": {
        "calories": 600,
        "protein_g": 25.0,
        "carbs_g": 70.0,
        "fats_g": 20.0,
        "fiber_g": 12.0,
        "micronutrients": {"iron_mg": 5.0}
      },
      "prep_time_minutes": 15,
      "cook_time_minutes": 30,
      "source": "generator_v2",
      "tags": ["balanced", "vegetarian"]
    }
  ],
  "shopping_list": [
    {
      "category": "pantry",
      "name": "Chickpeas",
      "quantity": 2.0,
      "unit": "cans",
      "notes": "Prefer low sodium",
      "is_pantry": false
    }
  ],
  "summary": {
    "overview": "High-protein vegetarian week with gentle prep times.",
    "calorie_total": 4200,
    "macro_totals": {
      "calories": 4200,
      "protein_g": 210.0,
      "carbs_g": 390.0,
      "fats_g": 140.0,
      "fiber_g": 55.0,
      "micronutrients": {}
    },
    "allergy_warnings": ["Peanut-free menu"],
    "variety_score": 0.82
  },
  "warnings": [
    {"code": "LIMITED_INGREDIENT", "message": "Spinach availability is low.", "blocking": false}
  ],
  "diagnostics": {
    "prompt_versions": ["mealplan:2.1.0"],
    "rule_hits": ["balanced_macro_constraints"],
    "raw_context": {"upstream_latency_ms": 850}
  },
  "status": "ready"
}
```

### Error Contract

When generation fails, raise `MealPlanGenerationError` with:

```json
{
  "code": "MISSING_INGREDIENTS",
  "message": "Unable to satisfy allergy constraints with available recipes.",
  "retryable": false,
  "details": {"missing": ["gluten-free naan"]}
}
```

The backend converts the error into a `400/500` HTTP response and marks the stored record as `"failed"`.

## Implementation Notes

- Register your generator implementation with `MealPlanService` by providing a `MealPlanGenerator` instance (see `backend/app/domain/meal_planning/stub_generator.py` for a reference).
- Keep the method side-effect free; persistence, logging, and workflow orchestration stay in the backend.
- Use the `metadata` field for feature flags or tracing identifiers that should accompany downstream logging.
