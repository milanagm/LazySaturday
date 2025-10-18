from fastapi import FastAPI

from .api.routes import api_router


def create_app() -> FastAPI:
    """Application factory used by ASGI servers."""
    app = FastAPI(
        title="Culturally Adaptive Diet Planner API",
        version="0.1.0",
        description="Minimal stub aligning with the design document architecture.",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()


@app.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
