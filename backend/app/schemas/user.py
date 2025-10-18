from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserPreferencesRequest(BaseModel):
    email: EmailStr
    diet_id: str
    culture_id: str
    additional_cultures: list[str] = Field(default_factory=list)
    country: str
    city: str | None = None
    dietary_goals: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    meals_per_day: int = Field(default=3, ge=1, le=6)
    household_size: int = Field(default=1, ge=1, le=10)
    cooking_time_limit: int = Field(default=30, ge=10, le=120)


class UserPreferencesView(BaseModel):
    email: EmailStr
    diet_id: str
    culture_id: str
    additional_cultures: list[str]
    country: str
    city: str | None = None
    dietary_goals: list[str]
    allergies: list[str]
    disliked_ingredients: list[str]
    meals_per_day: int
    household_size: int
    cooking_time_limit: int


class UserPreferencesSaveResponse(BaseModel):
    status: str
    workflow_id: UUID
    message: str


class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool


class TokenPayload(BaseModel):
    sub: str
    exp: int
