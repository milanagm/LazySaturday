from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "diet-planner"
    n8n_base_url: str = "http://n8n:5678"
    n8n_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_prefix = "DIET_"


@lru_cache
def get_settings() -> Settings:
    return Settings()
