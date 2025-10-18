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
                "instruction_steps": [],
                "tags": [],
            }
        ],
        "shopping_list": [
            {"name": "Example", "quantity": "2 cans", "is_pantry": False},
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


def test_n8n_generator_raises_for_empty_response(monkeypatch):
    client = N8NClient(base_url="http://n8n:5678")
    generator = N8NMealPlanGenerator(client=client, workflow_path="testpath")

    monkeypatch.setattr(client, "trigger_webhook", lambda path, payload: {})

    with pytest.raises(MealPlanGenerationError) as exc_info:
        generator.generate(build_context())
    assert exc_info.value.code == "n8n_empty_response"
