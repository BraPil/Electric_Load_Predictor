PYTHON ?= python
VENV_DIR = .venv

.PHONY: bootstrap ingest features train serve eval index up down clean

bootstrap:
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_DIR)/Scripts/pip install --upgrade pip || $(VENV_DIR)/bin/pip install --upgrade pip
	if [ -f requirements.txt ]; then \
		$(VENV_DIR)/Scripts/pip install -r requirements.txt || $(VENV_DIR)/bin/pip install -r requirements.txt; \
	fi
	@echo "Bootstrap complete. Activate with: source $(VENV_DIR)/bin/activate (UNIX) or $(VENV_DIR)\\Scripts\\Activate.ps1 (PowerShell)"

ingest:
	@echo "Stub: run ingestion pipeline (implement ingestion/fetch_uci.py and ingestion/etl.py)"

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
	@echo "Start local infra (implement docker-compose in docker/docker-compose.yml)"

down:
	@echo "Stop local infra"

clean:
	rm -rf $(VENV_DIR)
