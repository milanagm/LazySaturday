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
   Visit `http://localhost:5173` to explore the landing page. Use “Start Your Cultural Plan” to open the preferences wizard. Saving preferences now invokes the `create_dietaryplan` n8n workflow running at `http://localhost:5678`.

5. **Review today’s plan**
   After generating a plan, click “Today’s plan” in the header to see the current meal, upcoming dishes, and quick prep notes.

6. **Run backend tests**
   ```bash
   make backend-test
   ```

## Docker Compose

A minimal containerized setup lives in `infra/compose/docker-compose.yml` and wires together the frontend, backend, n8n, Postgres, and Redis services.

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

The Postgres container persists data in the named volume `postgres-data`, so your generated meal plans and preferences survive restarts. Prune that volume if you need a clean database.

The backend container reads the following n8n-related environment variables:

- `DIET_N8N_BASE_URL` — Base URL for the n8n instance (`http://n8n:5678` within the compose network).
- `DIET_N8N_MEAL_PLAN_PATH` — The webhook path the workflow exposes. Defaults to `webhook-test/testpath`; adjust to your active workflow URL (without the host).
- `DIET_N8N_BASIC_AUTH_USER` / `DIET_N8N_BASIC_AUTH_PASSWORD` — Credentials passed as HTTP basic auth when invoking the webhook. Match them with the `N8N_BASIC_AUTH_*` values on the n8n service.
- `DIET_N8N_API_KEY` (optional) — When set, sent as a bearer token header for additional security.

### n8n Workflow

- The meal plan generator posts to the n8n webhook configured by `DIET_N8N_MEAL_PLAN_PATH` (default `testpath`). Leaving the variable empty falls back to the in-process stub generator.
- Import `workflows/n8n/create_dietaryplan.json` into your local n8n instance or let the synced volume populate it, then activate the workflow.
- Provide a Gemini / PaLM API credential inside n8n named `Google Gemini(PaLM) Api account` to satisfy the workflow nodes, or swap the LLM node for an available provider.
- When developing without n8n, set `DIET_N8N_MEAL_PLAN_PATH=` (empty) and swap the generator back to the stub inside `backend/app/api/routes.py`.

## Next Steps

- Replace in-memory services with PostgreSQL persistence via SQLAlchemy and Alembic.
- Generate OpenAPI-derived shared types inside `packages/shared-types/`.
- Flesh out real n8n workflows under `workflows/n8n/` and wire secrets via environment.
- Extend CI/CD automation (GitHub Actions) and add automated tests (pytest, Vitest).
