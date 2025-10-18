.PHONY: backend frontend up down backend-venv backend-test

VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := python3
FRONTEND_DIR := frontend
FRONTEND_BIN := $(FRONTEND_DIR)/node_modules/.bin

backend: $(VENV_BIN)/uvicorn
	@if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then \
		echo "Starting backend dependencies with docker compose..."; \
		docker compose -f infra/compose/docker-compose.yml up -d postgres redis n8n; \
	else \
		echo "⚠️  Docker unavailable or daemon not running. Skipping dependency containers."; \
		echo "   Start postgres/redis/n8n manually if required."; \
	fi
	$(VENV_BIN)/uvicorn backend.app.main:app --reload

backend-venv: $(VENV_BIN)/uvicorn
	@echo "Virtual environment ready. Activate with: source $(VENV_BIN)/activate"

backend-test: $(VENV_BIN)/uvicorn
	$(VENV_BIN)/pytest backend/app

$(VENV_BIN)/uvicorn: backend/requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_BIN)/pip install -r backend/requirements.txt

frontend: $(FRONTEND_BIN)/vite
	cd $(FRONTEND_DIR) && npm run dev

$(FRONTEND_BIN)/vite: $(FRONTEND_DIR)/package.json
	npm install --prefix $(FRONTEND_DIR)

up:
	docker compose -f infra/compose/docker-compose.yml up --build

down:
	docker compose -f infra/compose/docker-compose.yml down
