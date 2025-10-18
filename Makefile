.PHONY: backend frontend up down backend-venv

VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := python3

backend: $(VENV_BIN)/uvicorn
	$(VENV_BIN)/uvicorn backend.app.main:app --reload

backend-venv: $(VENV_BIN)/uvicorn
	@echo "Virtual environment ready. Activate with: source $(VENV_BIN)/activate"

$(VENV_BIN)/uvicorn: backend/requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_BIN)/pip install -r backend/requirements.txt

frontend:
	cd frontend && npm run dev

up:
	docker compose -f infra/compose/docker-compose.yml up --build

down:
	docker compose -f infra/compose/docker-compose.yml down
