from datetime import date, datetime, time

import pytest

from ..meal_planning.stub_generator import StubMealPlanGenerator

from .meal_plan_service import MealPlanService
from ...schemas.meal import MealItem, MealPlanCreateRequest, ShoppingListItem
from ...schemas.workflow import WorkflowPlanCallback, WorkflowPlanDetails


def test_create_meal_plan_generates_week() -> None:
    service = MealPlanService.create_in_memory()
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")

    response = service.create_meal_plan(payload)

    assert response.user_email == "user@example.com"
    assert response.status == "ready"
    assert response.diet_id == "balanced"
    assert response.culture_id == "indian"
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


class FailingGenerator:
    def generate(self, context):  # type: ignore[override]
        from ..meal_planning.contracts import MealPlanGenerationError

        raise MealPlanGenerationError(code="boom", message="fail", retryable=False)


def test_fallback_generator_is_used() -> None:
    service = MealPlanService.create_with_generator(FailingGenerator(), fallback=StubMealPlanGenerator())
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")

    response = service.create_meal_plan(payload)

    assert response.status == "ready"


def test_today_overview_highlights_current_meal() -> None:
    service = MealPlanService.create_in_memory()
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")
    service.create_meal_plan(payload)

    midday = datetime.combine(datetime.today().date(), time(12, 0))
    overview = service.get_today_overview("user@example.com", now=midday)

    assert overview is not None
    assert overview.date == midday.date()
    assert overview.current_meal is not None
    assert overview.current_meal.status == "current"
    assert overview.current_meal.meal_type == "dinner"


class AsyncOnlyGenerator:
    def __init__(self) -> None:
        self.enqueued = False

    def enqueue(self, context):  # type: ignore[no-untyped-def]
        self.enqueued = True

    def generate(self, context):  # type: ignore[no-untyped-def]
        raise AssertionError("generate should not be called when enqueue is available")


def test_trigger_plan_generation_creates_pending_record_when_enqueue_available() -> None:
    service = MealPlanService.create_with_generator(AsyncOnlyGenerator())
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")

    response = service.trigger_plan_generation(payload)

    assert response.status == "pending"
    assert response.meals == []
    latest = service.get_latest("user@example.com")
    assert latest is not None
    assert latest.status == "pending"


def test_finalize_plan_from_callback_replaces_pending_plan() -> None:
    service = MealPlanService.create_with_generator(AsyncOnlyGenerator())
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")
    pending = service.trigger_plan_generation(payload)

    callback = WorkflowPlanCallback(
        request_id=pending.id,
        workflow_name="diet-plan-start",
        status="completed",
        user_email="user@example.com",
        plan=WorkflowPlanDetails(
            plan_id=pending.id,
            week_start=date.today(),
            diet_id="balanced",
            culture_id="indian",
            meals=[
                MealItem(day_of_week="monday", meal_type="dinner", recipe_title="Test Meal")
            ],
            shopping_list=[ShoppingListItem(name="Test", quantity="1 item")],
            summary=None,
            warnings=[],
            status="ready",
        ),
    )

    stored = service.finalize_plan_from_callback(callback)

    assert stored.status == "ready"
    assert len(stored.meals) == 1
    latest = service.get_latest("user@example.com")
    assert latest is not None
    assert latest.status == "ready"
    assert latest.id == stored.id


def test_mark_plan_failed_updates_placeholder() -> None:
    service = MealPlanService.create_with_generator(AsyncOnlyGenerator())
    payload = MealPlanCreateRequest(email="user@example.com", diet_id="balanced", culture_id="indian")
    pending = service.trigger_plan_generation(payload)

    callback = WorkflowPlanCallback(
        request_id=pending.id,
        workflow_name="diet-plan-start",
        status="failed",
        user_email="user@example.com",
        plan=None,
        error={"message": "timeout"},
    )

    service.mark_plan_failed(callback)

    latest = service.get_latest("user@example.com")
    assert latest is not None
    assert latest.status == "failed"
