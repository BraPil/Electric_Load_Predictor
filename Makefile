PYTHON ?= python
VENV_DIR = .venv

.PHONY: bootstrap ingest features train serve eval index up down logs ps clean

bootstrap:
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/Scripts/pip install --upgrade pip || $(VENV_DIR)/bin/pip install --upgrade pip
	if [ -f requirements.txt ]; then \
		$(VENV_DIR)/Scripts/pip install -r requirements.txt || $(VENV_DIR)/bin/pip install -r requirements.txt; \
	fi
	@echo "Bootstrap complete. Activate with: source $(VENV_DIR)/bin/activate (UNIX) or $(VENV_DIR)\\Scripts\\Activate.ps1 (PowerShell)"

ingest:
	@echo "Running ingestion pipeline..."
	@echo "Step 1: Downloading UCI dataset..."
	$(PYTHON) ingestion/fetch_uci.py
	@echo "Step 2: Running ETL (Extract, Transform, Load)..."
	$(PYTHON) ingestion/etl.py --input data/raw/household_power.zip
	@echo "✓ Ingestion complete! Data ready in data/processed/"

features:
	@echo "Stub: run feature engineering (implement features/feature_store.py)"

train:
	@echo "Stub: run training (implement training scripts)"

serve:
	@echo "Stub: start FastAPI serving: uvicorn serving.app:app --reload"

eval:
	@echo "Stub: run evaluation suite"

index:
	@echo "Stub: build RAG embedding index"

up:
	@echo "Starting local infra via docker-compose..."
	docker compose -f docker/docker-compose.yml up -d --remove-orphans

down:
	@echo "Stopping local infra via docker-compose..."
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

ps:
	docker compose -f docker/docker-compose.yml ps

clean:
	rm -rf $(VENV_DIR)
