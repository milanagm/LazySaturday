import pytest

from .meal_plan_service import MealPlanService
from ...schemas.meal import MealPlanCreateRequest


def test_create_meal_plan_generates_week() -> None:
    service = MealPlanService.create_in_memory()
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")

    response = service.create_meal_plan(payload)

    assert response.user_email == "user@example.com"
    assert response.status == "ready"
    assert len(response.meals) == 7
    assert all(meal.day_of_week for meal in response.meals)
    assert "Indian" in response.meals[0].recipe_title
    assert response.meals[0].instruction_steps, "expected structured instructions"
    assert response.summary is not None
    assert response.summary.calorie_total is not None


def test_get_latest_returns_last_plan() -> None:
    service = MealPlanService.create_in_memory()

    assert service.get_latest() is None

    payload = MealPlanCreateRequest(email="user@example.com", diet_id="vegan", culture_id="ethiopian")
    created = service.create_meal_plan(payload)

    latest = service.get_latest("user@example.com")
    assert latest is not None
    assert latest.id == created.id
    assert latest.user_email == "user@example.com"
    assert latest.summary is not None

    retrieved = service.get_meal_plan(str(created.id))
    assert retrieved is not None
    assert retrieved.id == created.id

    assert service.get_latest("someoneelse@example.com") is None
    assert service.get_latest() is not None


@pytest.mark.parametrize("plan_id", ["", "abc", "1234"])
def test_get_meal_plan_invalid_uuid_returns_none(plan_id: str) -> None:
    service = MealPlanService.create_in_memory()

    assert service.get_meal_plan(plan_id) is None
