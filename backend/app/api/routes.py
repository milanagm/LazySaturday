from fastapi import APIRouter, Depends, HTTPException

from ..domain.services.meal_plan_service import MealPlanService
from ..schemas.meal import MealPlanCreateRequest, MealPlanResponse
from ..schemas.metadata import CultureResponse, DietResponse
from ..schemas.user import LoginRequest, LoginResponse, RegisterRequest, UserPreferencesRequest
from ..schemas.workflow import WorkflowCallback

api_router = APIRouter()
_meal_plan_service = MealPlanService.create_in_memory()


def get_meal_plan_service() -> MealPlanService:
    return _meal_plan_service


@api_router.post("/auth/register", response_model=LoginResponse, tags=["auth"])
async def register_user(payload: RegisterRequest) -> LoginResponse:
    # In-memory token minting for minimal implementation
    token = f"demo-token-{payload.email}"
    return LoginResponse(access_token=token)


@api_router.post("/auth/login", response_model=LoginResponse, tags=["auth"])
async def login(payload: LoginRequest) -> LoginResponse:
    token = f"demo-token-{payload.email}"
    return LoginResponse(access_token=token)


@api_router.get("/diets", response_model=list[DietResponse], tags=["metadata"])
async def list_diets() -> list[DietResponse]:
    return [
        DietResponse(id=1, name="Vegan"),
        DietResponse(id=2, name="Halal"),
        DietResponse(id=3, name="Mediterranean"),
    ]


@api_router.get("/cultures", response_model=list[CultureResponse], tags=["metadata"])
async def list_cultures() -> list[CultureResponse]:
    return [
        CultureResponse(id=1, name="Indian", region_code="IN"),
        CultureResponse(id=2, name="Italian", region_code="IT"),
    ]


@api_router.post("/user/preferences", tags=["users"])
async def save_preferences(payload: UserPreferencesRequest) -> dict[str, str]:
    return {"status": "stored", "email": payload.email}


@api_router.post(
    "/plans/generate",
    response_model=MealPlanResponse,
    tags=["meal-plans"],
)
async def generate_plan(
    request: MealPlanCreateRequest, service: MealPlanService = Depends(get_meal_plan_service)
) -> MealPlanResponse:
    try:
        return service.create_meal_plan(request)
    except ValueError as exc:  # pragma: no cover - simple example
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/plans/{plan_id}", response_model=MealPlanResponse, tags=["meal-plans"])
async def get_plan(plan_id: str, service: MealPlanService = Depends(get_meal_plan_service)) -> MealPlanResponse:
    plan = service.get_meal_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@api_router.get("/plans/latest", response_model=MealPlanResponse | None, tags=["meal-plans"])
async def get_latest_plan(service: MealPlanService = Depends(get_meal_plan_service)) -> MealPlanResponse | None:
    return service.get_latest()


@api_router.post("/workflows/plan-complete", tags=["workflows"])
async def workflow_callback(callback: WorkflowCallback) -> dict[str, str]:
    # Placeholder for workflow status reconciliation
    return {"workflow": callback.workflow_name, "status": callback.status}
