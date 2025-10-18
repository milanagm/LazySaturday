.PHONY: backend frontend up down backend-venv backend-test backend-logs frontend-logs

COMPOSE_FILE := infra/compose/docker-compose.yml
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := python3
FRONTEND_DIR := frontend
FRONTEND_BIN := $(FRONTEND_DIR)/node_modules/.bin

backend:
	docker compose -f $(COMPOSE_FILE) up backend -d --build

backend-logs:
	docker compose -f $(COMPOSE_FILE) logs -f backend

backend-venv: $(VENV_BIN)/uvicorn
	@echo "Virtual environment ready. Activate with: source $(VENV_BIN)/activate"

backend-test: $(VENV_BIN)/uvicorn
	$(VENV_BIN)/pytest backend/app

$(VENV_BIN)/uvicorn: backend/requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_BIN)/pip install -r backend/requirements.txt

frontend:
	docker compose -f $(COMPOSE_FILE) up frontend -d --build

frontend-logs:
	docker compose -f $(COMPOSE_FILE) logs -f frontend

$(FRONTEND_BIN)/vite: $(FRONTEND_DIR)/package.json
	npm install --prefix $(FRONTEND_DIR)

up:
	docker compose -f $(COMPOSE_FILE) up --build

down:
	docker compose -f $(COMPOSE_FILE) down
