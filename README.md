# Culturally Adaptive Diet Planner (Minimal Implementation)

This repository contains a lightweight, working skeleton that mirrors the architecture described in the design document. It provides a FastAPI backend, a Vite + React frontend, placeholder n8n workflows, and Docker Compose infrastructure for local development.

## Repository Layout

```
diet-planner/
  backend/
    app/
      api/
      core/
      domain/
      integrations/
      schemas/
    requirements.txt
  frontend/
    src/
      app/
      components/
      features/
      lib/
    package.json
    tsconfig.json
    vite.config.ts
  workflows/
    n8n/
  packages/
    shared-types/
  infra/
    docker/
    compose/
  scripts/
  Makefile
```

## Getting Started

1. **Create & activate backend virtualenv**
   ```bash
   make backend-venv
   source .venv/bin/activate
   ```

2. **Start the backend**
   ```bash
   make backend
   ```

3. **Start the frontend**
   ```bash
   make frontend
   ```

4. **Open the app**
   Visit `http://localhost:5173` and use the form to trigger the stubbed meal plan generation workflow.

5. **Run backend tests**
   ```bash
   make backend-test
   ```

## Docker Compose

A minimal containerized setup lives in `infra/compose/docker-compose.yml` and wires together the frontend, backend, n8n, Postgres, and Redis services.

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

## Next Steps

- Replace in-memory services with PostgreSQL persistence via SQLAlchemy and Alembic.
- Generate OpenAPI-derived shared types inside `packages/shared-types/`.
- Flesh out real n8n workflows under `workflows/n8n/` and wire secrets via environment.
- Extend CI/CD automation (GitHub Actions) and add automated tests (pytest, Vitest).
