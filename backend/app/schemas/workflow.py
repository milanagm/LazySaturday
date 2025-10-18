from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from .meal import MealItem, MealPlanSummary, MealPlanWarning, ShoppingListItem


class WorkflowPlanDetails(BaseModel):
    plan_id: UUID | None = None
    week_start: date
    diet_id: str
    culture_id: str
    meals: list[MealItem] = Field(default_factory=list)
    shopping_list: list[ShoppingListItem] = Field(default_factory=list)
    summary: MealPlanSummary | None = None
    warnings: list[MealPlanWarning] = Field(default_factory=list)
    status: str = "ready"


class WorkflowPlanCallback(BaseModel):
    request_id: UUID
    workflow_name: str
    status: str
    user_email: EmailStr
    plan: WorkflowPlanDetails | None = None
    error: dict[str, Any] | None = None
