from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest

from ...integrations.n8n_client import N8NClient
from ..meal_planning.contracts import MealPlanGenerationContext, MealPlanGenerationError
from ..meal_planning.n8n_generator import N8NMealPlanGenerator
from ...schemas.user import UserPreferencesView


def build_context() -> MealPlanGenerationContext:
    return MealPlanGenerationContext(
        request_id=uuid4(),
        user_email="user@example.com",
        week_start=date(2024, 5, 6),
        preferences=UserPreferencesView(
            email="user@example.com",
            diet_id="balanced",
            culture_id="indian",
            additional_cultures=["ethiopian"],
            country="US",
            city="New York",
            dietary_goals=["protein"],
            allergies=["peanut"],
            disliked_ingredients=["okra"],
            meals_per_day=3,
            household_size=2,
            cooking_time_limit=45,
        ),
    )


def sample_response() -> dict:
    return {
        "plan_id": str(uuid4()),
        "meals": [
            {
                "day_of_week": "Monday",
                "meal_type": "dinner",
                "recipe_title": "Sample Meal",
                "recipe_id": "sample-1",
                "ingredients": [],
                "instructions": [],
                "tags": [],
            }
        ],
        "shopping_list": [
            {"name": "Example", "quantity": 2.0, "unit": "cans", "is_pantry": False},
        ],
        "status": "ready",
        "warnings": [],
    }


def test_n8n_generator_invokes_client(monkeypatch):
    client = N8NClient(base_url="http://n8n:5678")
    generator = N8NMealPlanGenerator(client=client, workflow_path="testpath")
    captured = {}

    def fake_trigger(path: str, payload: dict) -> dict:
        captured["path"] = path
        captured["payload"] = payload
        return sample_response()

    monkeypatch.setattr(client, "trigger_webhook", fake_trigger)

    context = build_context()
    result = generator.generate(context)

    assert captured["path"] == "testpath"
    assert captured["payload"]["context"]["preferences"]["email"] == "user@example.com"
    assert isinstance(result.plan_id, UUID)
    assert result.status == "ready"


def test_n8n_generator_enqueue(monkeypatch):
    client = N8NClient(base_url="http://n8n:5678")
    generator = N8NMealPlanGenerator(client=client, workflow_path="testpath")
    captured = {}

    def fake_trigger(path: str, payload: dict) -> dict:
        captured["path"] = path
        captured["payload"] = payload
        return {}

    monkeypatch.setattr(client, "trigger_webhook", fake_trigger)

    context = build_context()
    generator.enqueue(context)

    assert captured["path"] == "testpath"
    assert captured["payload"]["request_id"] == str(context.request_id)


def test_n8n_generator_raises_for_empty_response(monkeypatch):
    client = N8NClient(base_url="http://n8n:5678")
    generator = N8NMealPlanGenerator(client=client, workflow_path="testpath")

    monkeypatch.setattr(client, "trigger_webhook", lambda path, payload: {})

    with pytest.raises(MealPlanGenerationError) as exc_info:
        generator.generate(build_context())
    assert exc_info.value.code == "n8n_empty_response"


def test_n8n_generator_enriches_minimal_response(monkeypatch):
    client = N8NClient(base_url="http://n8n:5678")
    generator = N8NMealPlanGenerator(client=client, workflow_path="testpath")

    minimal_response = {
        "meals": [
            {
                "day_of_week": "Monday",
                "meal_type": "Lunch",
                "recipe_id": "moroccan-halloumi-salad-001",
                "recipe_title": "Moroccan Spiced Lentil & Halloumi Salad",
                "ingredients": [
                    {"name": "Cooked Lentils", "quantity": 200, "unit": "g"},
                    {"name": "Halloumi Cheese", "quantity": 150, "unit": "g"},
                    {"name": "Cucumber", "quantity": 1, "unit": "medium"},
                    {"name": "Tomatoes", "quantity": 2, "unit": "medium"},
                    {"name": "Bell Pepper", "quantity": 1, "unit": "medium"},
                    {"name": "Fresh Mint", "quantity": 0.25, "unit": "cup"},
                    {"name": "Lemon Juice", "quantity": 2, "unit": "tbsp"},
                    {"name": "Olive Oil", "quantity": 3, "unit": "tbsp"},
                    {"name": "Cumin", "quantity": 1, "unit": "tsp"},
                    {"name": "Paprika", "quantity": 1, "unit": "tsp"},
                    {"name": "Garlic", "quantity": 1, "unit": "clove"},
                ],
                "tags": ["vegetarian", "quick_meal", "fusion", "healthy", "lunch"],
                "instructions": [
                    {
                        "step_number": 1,
                        "description": "Chop the cucumber, tomatoes, and bell pepper into bite-sized pieces. Mince the garlic and chop the fresh mint.",
                        "duration_minutes": 10,
                    },
                    {
                        "step_number": 2,
                        "description": "Whisk together the lemon juice, olive oil, cumin, paprika, and minced garlic to create the dressing.",
                        "duration_minutes": 5,
                    },
                    {
                        "step_number": 3,
                        "description": "Fry the halloumi slices until golden brown on each side.",
                        "duration_minutes": 8,
                    },
                    {
                        "step_number": 4,
                        "description": "Combine lentils, vegetables, halloumi, and dressing. Toss gently with fresh mint.",
                        "duration_minutes": 2,
                    },
                    {
                        "step_number": 5,
                        "description": "Serve immediately.",
                        "duration_minutes": 0,
                    },
                ],
                "prep_time_minutes": 15,
                "cook_time_minutes": 10,
            }
        ]
    }

    monkeypatch.setattr(client, "trigger_webhook", lambda path, payload: minimal_response)

    result = generator.generate(build_context())

    assert result.status == "ready"
    assert result.summary is not None
    assert "Moroccan Spiced Lentil & Halloumi Salad" in result.meals[0].recipe_title
    assert result.meals[0].prep_time_minutes == 15
    assert result.meals[0].cook_time_minutes == 10
    assert result.meals[0].tags == ["vegetarian", "quick_meal", "fusion", "healthy", "lunch"]
    assert result.shopping_list, "shopping list should be auto-generated from ingredients"
    shopping_names = sorted(item.name for item in result.shopping_list)
    assert "Cooked Lentils" in shopping_names
    assert result.summary.overview.startswith("Generated 1 meals for the week")
