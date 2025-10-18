from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import get_settings
from ..domain.services.auth_service import AuthService
from ..domain.services.meal_plan_service import MealPlanService
from ..domain.services.user_preference_service import UserPreferenceService
from ..integrations.n8n_client import N8NClient
from ..schemas.meal import MealPlanCreateRequest, MealPlanResponse, TodayOverviewResponse
from ..schemas.metadata import CultureResponse, DietResponse
from ..schemas.user import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserPreferencesRequest,
    UserPreferencesSaveResponse,
    UserPreferencesView,
    UserProfileResponse,
)
from ..schemas.workflow import WorkflowCallback
from ..domain.meal_planning.n8n_generator import N8NMealPlanGenerator
from ..domain.meal_planning.stub_generator import StubMealPlanGenerator

api_router = APIRouter()
_settings = get_settings()
if _settings.n8n_meal_plan_path:
    _n8n_client = N8NClient(
        base_url=_settings.n8n_base_url,
        api_key=_settings.n8n_api_key,
        basic_auth_user=_settings.n8n_basic_auth_user,
        basic_auth_password=_settings.n8n_basic_auth_password,
    )
    _meal_plan_generator = N8NMealPlanGenerator(client=_n8n_client, workflow_path=_settings.n8n_meal_plan_path)
    _fallback_generator = StubMealPlanGenerator()
    _meal_plan_service = MealPlanService.create_with_generator(
        _meal_plan_generator,
        fallback=_fallback_generator,
    )
else:  # pragma: no cover - local override without n8n
    _meal_plan_generator = StubMealPlanGenerator()
    _meal_plan_service = MealPlanService.create_with_generator(_meal_plan_generator)
_user_preference_service = UserPreferenceService()


def get_meal_plan_service() -> MealPlanService:
    return _meal_plan_service


def get_user_preference_service() -> UserPreferenceService:
    return _user_preference_service


def get_auth_service(session: Session = Depends(get_db)) -> AuthService:
    return AuthService(session)


@api_router.post("/auth/register", response_model=LoginResponse, tags=["auth"])
async def register_user(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    result = auth_service.register(payload)
    return result.response


@api_router.post("/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    result = auth_service.login(payload)
    return result.response


@api_router.get("/auth/me", response_model=UserProfileResponse, tags=["auth"])
async def read_profile(
    current_user=Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)
) -> UserProfileResponse:
    return auth_service.build_profile(current_user)


@api_router.get("/diets", response_model=list[DietResponse], tags=["metadata"])
async def list_diets() -> list[DietResponse]:
    return [
        DietResponse(id="vegan", name="Vegan"),
        DietResponse(id="vegetarian", name="Vegetarian"),
        DietResponse(id="halal", name="Halal"),
        DietResponse(id="kosher", name="Kosher"),
        DietResponse(id="low_carb", name="Low-Carb"),
        DietResponse(id="balanced", name="Balanced"),
        DietResponse(id="pescatarian", name="Pescatarian"),
        DietResponse(id="mediterranean", name="Mediterranean"),
        DietResponse(id="custom", name="Custom"),
    ]


@api_router.get("/cultures", response_model=list[CultureResponse], tags=["metadata"])
async def list_cultures() -> list[CultureResponse]:
    return [
        CultureResponse(id="indian", name="Indian", region_code="IN"),
        CultureResponse(id="ethiopian", name="Ethiopian", region_code="ET"),
        CultureResponse(id="italian", name="Italian", region_code="IT"),
        CultureResponse(id="turkish", name="Turkish", region_code="TR"),
        CultureResponse(id="mexican", name="Mexican", region_code="MX"),
        CultureResponse(id="korean", name="Korean", region_code="KR"),
        CultureResponse(id="nigerian", name="Nigerian", region_code="NG"),
        CultureResponse(id="peruvian", name="Peruvian", region_code="PE"),
    ]


@api_router.post(
    "/user/preferences",
    response_model=UserPreferencesSaveResponse,
    tags=["users"],
    status_code=202,
)
async def save_preferences(
    payload: UserPreferencesRequest,
    preferences_service: UserPreferenceService = Depends(get_user_preference_service),
    meal_plan_service: MealPlanService = Depends(get_meal_plan_service),
    current_user=Depends(get_current_user),
) -> UserPreferencesSaveResponse:
    if payload.email.lower() != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify another user's preferences")

    response = preferences_service.save_preferences(payload)
    preferences_snapshot = preferences_service.get_preferences(payload.email)
    meal_plan_service.create_meal_plan(
        MealPlanCreateRequest(email=payload.email, diet_id=payload.diet_id, culture_id=payload.culture_id),
        preferences=preferences_snapshot,
    )
    return response


@api_router.get("/user/preferences", response_model=UserPreferencesView | None, tags=["users"])
async def fetch_preferences(
    email: EmailStr | None = None,
    preferences_service: UserPreferenceService = Depends(get_user_preference_service),
    current_user=Depends(get_current_user),
) -> UserPreferencesView | None:
    target_email = (email or current_user.email).lower()
    if target_email != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another user's preferences")
    return preferences_service.get_preferences(current_user.email)


@api_router.post(
    "/plans/generate",
    response_model=MealPlanResponse,
    tags=["meal-plans"],
)
async def generate_plan(
    request: MealPlanCreateRequest,
    service: MealPlanService = Depends(get_meal_plan_service),
    preferences_service: UserPreferenceService = Depends(get_user_preference_service),
    current_user=Depends(get_current_user),
) -> MealPlanResponse:
    if request.email.lower() != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot generate plan for another user")

    preferences_snapshot = request.preferences_override or preferences_service.get_preferences(request.email)
    if request.preferences_override and request.preferences_override.email.lower() != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Preferences override must match authenticated user"
        )
    try:
        return service.create_meal_plan(request, preferences=preferences_snapshot)
    except ValueError as exc:  # pragma: no cover - simple example
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/plans/{plan_id}", response_model=MealPlanResponse, tags=["meal-plans"])
async def get_plan(
    plan_id: str,
    service: MealPlanService = Depends(get_meal_plan_service),
    current_user=Depends(get_current_user),
) -> MealPlanResponse:
    plan = service.get_meal_plan(plan_id)
    if not plan or plan.user_email.lower() != current_user.email:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@api_router.get("/plans/latest", response_model=MealPlanResponse | None, tags=["meal-plans"])
async def get_latest_plan(
    service: MealPlanService = Depends(get_meal_plan_service),
    current_user=Depends(get_current_user),
) -> MealPlanResponse | None:
    latest = service.get_latest(current_user.email)
    if latest and latest.user_email.lower() != current_user.email:
        return None
    return latest


@api_router.get("/plans/today", response_model=TodayOverviewResponse | None, tags=["meal-plans"])
async def get_today_plan(
    service: MealPlanService = Depends(get_meal_plan_service),
    current_user=Depends(get_current_user),
) -> TodayOverviewResponse | None:
    return service.get_today_overview(current_user.email)


@api_router.post("/workflows/plan-complete", tags=["workflows"])
async def workflow_callback(callback: WorkflowCallback) -> dict[str, str]:
    # Placeholder for workflow status reconciliation
    return {"workflow": callback.workflow_name, "status": callback.status}
