from pydantic import BaseModel


class DietResponse(BaseModel):
    id: int
    name: str


class CultureResponse(BaseModel):
    id: int
    name: str
    region_code: str
