from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "diet-planner"
    n8n_base_url: str = "http://n8n:5678"
    n8n_api_key: str | None = None
    database_url: str = "postgresql+psycopg://dp:dp@localhost:5432/dietplanner"
    access_token_expires_minutes: int = 15
    refresh_token_expires_minutes: int = 60 * 24 * 7
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        env_prefix = "DIET_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
