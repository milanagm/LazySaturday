from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class MealItem(BaseModel):
    day_of_week: str
    meal_type: str
    recipe_title: str
    instructions: str


class ShoppingListItem(BaseModel):
    name: str
    quantity: str


class MealPlanResponse(BaseModel):
    id: UUID
    user_email: str
    week_start: date
    meals: list[MealItem] = Field(default_factory=list)
    shopping_list: list[ShoppingListItem] = Field(default_factory=list)
    status: str = "draft"


class MealPlanCreateRequest(BaseModel):
    email: EmailStr
    diet_id: str
    culture_id: str
