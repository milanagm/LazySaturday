from pydantic import BaseModel


class DietResponse(BaseModel):
    id: str
    name: str


class CultureResponse(BaseModel):
    id: str
    name: str
    region_code: str
