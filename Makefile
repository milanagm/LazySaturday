.PHONY: backend frontend up down backend-venv

backend:
	uvicorn backend.app.main:app --reload

backend-venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r backend/requirements.txt
	@echo "Virtual environment ready. Activate with: source .venv/bin/activate"

frontend:
	cd frontend && npm run dev

up:
	docker compose -f infra/compose/docker-compose.yml up --build

down:
	docker compose -f infra/compose/docker-compose.yml down
