from contextlib import contextmanager
from datetime import date, datetime, time
from uuid import UUID, uuid4

import pytest

from ..meal_planning.stub_generator import StubMealPlanGenerator

from . import meal_plan_service as meal_plan_module
from .meal_plan_service import MealPlanService
from ...schemas.meal import MealItem, MealPlanCreateRequest, MealPlanResponse, ShoppingListItem
from ...schemas.workflow import WorkflowPlanCallback, WorkflowPlanDetails


class MockMealPlanRepository:
    def __init__(
        self,
        *,
        plan: MealPlanResponse | None = None,
        latest: MealPlanResponse | None = None,
        most_recent: MealPlanResponse | None = None,
    ) -> None:
        self.plan = plan
        self.latest = latest
        self.most_recent = most_recent
        self.calls: list[tuple[str, object | None]] = []
        self.persisted: list[MealPlanResponse] = []

    def upsert_plan(self, session, plan: MealPlanResponse) -> None:  # type: ignore[no-untyped-def]
        self.calls.append(("upsert_plan", plan.id))
        self.persisted.append(plan)

    def get_plan(self, session, plan_id: UUID):  # type: ignore[no-untyped-def]
        self.calls.append(("get_plan", plan_id))
        if self.plan and self.plan.id == plan_id:
            return self.plan
        return None

    def get_latest_for_user(self, session, email: str):  # type: ignore[no-untyped-def]
        self.calls.append(("get_latest_for_user", email))
        if self.latest and self.latest.user_email == email:
            return self.latest
        return None

    def get_most_recent(self, session):  # type: ignore[no-untyped-def]
        self.calls.append(("get_most_recent", None))
        return self.most_recent


@contextmanager
def stub_session_scope():
    yield object()


def make_plan_response(*, email: str = "user@example.com", plan_id: UUID | None = None) -> MealPlanResponse:
    return MealPlanResponse(
        id=plan_id or uuid4(),
        user_email=email,
        week_start=date.today(),
        diet_id="balanced",
        culture_id="global",
        meals=[
            MealItem(day_of_week="monday", meal_type="dinner", recipe_title="Test Meal", instructions="Enjoy")
        ],
        shopping_list=[ShoppingListItem(name="Ingredient", quantity="1 unit")],
        summary=None,
        warnings=[],
        status="ready",
    )


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


def test_get_latest_returns_last_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_repo = MockMealPlanRepository()
    service = MealPlanService.create_in_memory()
    
    monkeypatch.setattr(meal_plan_module, "meal_plan_repository", mock_repo)
    monkeypatch.setattr(meal_plan_module, "session_scope", stub_session_scope)

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


def test_get_meal_plan_fetches_from_repository_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = make_plan_response()
    mock_repo = MockMealPlanRepository(plan=plan)
    service = MealPlanService.create_in_memory()

    monkeypatch.setattr(meal_plan_module, "meal_plan_repository", mock_repo)
    monkeypatch.setattr(meal_plan_module, "session_scope", stub_session_scope)

    fetched = service.get_meal_plan(str(plan.id))

    assert fetched is not None
    assert fetched.id == plan.id
    assert ("get_plan", plan.id) in mock_repo.calls

    call_count = len(mock_repo.calls)
    cached = service.get_meal_plan(str(plan.id))
    assert cached is not None
    assert cached.id == plan.id
    assert len(mock_repo.calls) == call_count


def test_get_latest_for_user_fetches_via_repository_when_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = make_plan_response(email="fresh@example.com")
    mock_repo = MockMealPlanRepository(latest=plan)
    service = MealPlanService.create_in_memory()

    monkeypatch.setattr(meal_plan_module, "meal_plan_repository", mock_repo)
    monkeypatch.setattr(meal_plan_module, "session_scope", stub_session_scope)

    latest = service.get_latest(plan.user_email)

    assert latest is not None
    assert latest.id == plan.id
    assert ("get_latest_for_user", plan.user_email) in mock_repo.calls

    get_latest_calls = [call for call in mock_repo.calls if call[0] == "get_latest_for_user"]
    assert len(get_latest_calls) == 1

    cached = service.get_latest(plan.user_email)

    assert cached is not None
    assert cached.id == plan.id
    get_latest_calls = [call for call in mock_repo.calls if call[0] == "get_latest_for_user"]
    assert len(get_latest_calls) == 1


def test_get_latest_without_email_fetches_most_recent(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = make_plan_response(email="anyone@example.com")
    mock_repo = MockMealPlanRepository(most_recent=plan)
    service = MealPlanService.create_in_memory()

    monkeypatch.setattr(meal_plan_module, "meal_plan_repository", mock_repo)
    monkeypatch.setattr(meal_plan_module, "session_scope", stub_session_scope)

    result = service.get_latest()

    assert result is not None
    assert result.id == plan.id
    assert any(call for call in mock_repo.calls if call[0] == "get_most_recent")

    most_recent_calls = [call for call in mock_repo.calls if call[0] == "get_most_recent"]
    assert len(most_recent_calls) == 1

    cached = service.get_latest()

    assert cached is not None
    assert cached.id == plan.id
    most_recent_calls = [call for call in mock_repo.calls if call[0] == "get_most_recent"]
    assert len(most_recent_calls) == 1


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
