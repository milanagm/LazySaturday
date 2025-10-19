import logging

from fastapi import FastAPI

from .api.routes import api_router
from .core.database import Base, engine
from .domain import entities  # noqa: F401


def create_app() -> FastAPI:
    """Application factory used by ASGI servers."""
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(
        title="Culturally Adaptive Diet Planner API",
        version="0.1.0",
        description="Minimal stub aligning with the design document architecture.",
    )
    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def startup_event() -> None:  # pragma: no cover - framework hook
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()


@app.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
