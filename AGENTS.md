# Repository Guidelines

## Project Structure & Module Organization
- `backend/` contains the FastAPI application with domain-driven folders (`api/`, `core/`, `domain/`, `integrations/`, `schemas/`). Add new endpoints under `backend/app/api/` and domain logic in `backend/app/domain/`. Place unit tests beside their target modules using the `test_*.py` naming pattern.
- `frontend/` hosts the Vite + React client. Feature code lives in `src/features/`, shared UI in `src/components/`, and API helpers under `src/lib/`.
- `infra/` holds Docker assets (`infra/docker/`) and the local compose stack (`infra/compose/docker-compose.yml`). Update infrastructure changes here.
- `workflows/n8n/` stores JSON workflow definitions synced with the n8n instance.
- `packages/shared-types/` is reserved for generated OpenAPI and Zod contracts shared across services.

## Build, Test, and Development Commands
- `make backend` — run the FastAPI dev server via Uvicorn with auto-reload.
- `make frontend` — launch the Vite dev server on port 5173.
- `make up` / `make down` — start or stop the Docker Compose stack for all services.
- `pip install -r backend/requirements.txt` and `npm install` (inside `frontend/`) — install runtime dependencies before local work.

## Coding Style & Naming Conventions
- **Python**: follow PEP 8 with 4-space indentation. Prefer type hints and pydantic models for request/response DTOs. Place shared constants in `backend/app/core/`.
- **TypeScript/React**: use functional components, PascalCase filenames for components, camelCase for hooks/utilities. Keep feature folders self-contained.
- Formatters: enable black/ruff (Python) and Prettier/ESLint (TypeScript) once configured; do not commit formatting-only churn.

## Testing Guidelines
- Every backend module must ship with unit tests; store the test file next to the implementation (for example, `backend/app/domain/services/meal_plan_service.py` pairs with `backend/app/domain/services/test_meal_plan_service.py`).
- Python tests use `pytest`. Prefer factory fixtures for complex domain objects and ensure the suite runs with `pytest`.
- Frontend unit tests use `Vitest` with React Testing Library in `frontend/src/**/*.test.tsx`. Mirror component filenames (e.g., `MealPlanPreview.test.tsx`).
- Keep tests fast and deterministic; mock external services such as n8n or Redis.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages (e.g., `Add meal plan preview mutation`). Group related changes per commit.
- Pull requests should describe scope, implementation notes, and verification steps. Link issues or tickets using `Fixes #123` syntax where applicable.
- Include screenshots or terminal output when UI or UX changes occur. Request review from the owning module’s maintainer.
