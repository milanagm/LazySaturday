.PHONY: backend frontend up down

backend:
	uvicorn backend.app.main:app --reload

frontend:
	cd frontend && npm run dev

up:
	docker compose -f infra/compose/docker-compose.yml up --build

down:
	docker compose -f infra/compose/docker-compose.yml down
