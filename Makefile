PYTHON ?= python
CONDA_ENV = voltedge

.PHONY: bootstrap conda-create conda-update ingest test-ingest test-ingest-quick features train serve eval index up down logs ps clean

# Conda-based bootstrap (recommended)
conda-create:
	@echo "Creating Conda environment 'voltedge' from environment.yml..."
	conda env create -f environment.yml
	@echo "✓ Conda environment created!"
	@echo "Activate with: conda activate voltedge"

conda-update:
	@echo "Updating Conda environment from environment.yml..."
	conda env update -f environment.yml --prune
	@echo "✓ Environment updated!"

# Legacy venv bootstrap (for systems without conda)
bootstrap:
	@echo "WARNING: Using venv (legacy). Conda is recommended for this project."
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv .venv
	.venv/Scripts/pip install --upgrade pip || .venv/bin/pip install --upgrade pip
	if [ -f requirements.txt ]; then \
		.venv/Scripts/pip install -r requirements.txt || .venv/bin/pip install -r requirements.txt; \
	fi
	@echo "Bootstrap complete. Activate with: .venv\\Scripts\\Activate.ps1 (PowerShell)"
	@echo ""
	@echo "💡 TIP: Consider using Conda instead! See CONDA_SETUP_GUIDE.md"

ingest:
	@echo "Running ingestion pipeline..."
	@echo "Step 1: Downloading UCI dataset..."
	$(PYTHON) ingestion/fetch_uci.py
	@echo "Step 2: Running ETL (Extract, Transform, Load)..."
	$(PYTHON) ingestion/etl.py --input data/raw/household_power.zip
	@echo "✓ Ingestion complete! Data ready in data/processed/"

test-ingest:
	@echo "Running ingestion pipeline tests..."
	$(PYTHON) scripts/test_ingestion.py

test-ingest-quick:
	@echo "Running quick ingestion test (10k rows)..."
	$(PYTHON) scripts/test_ingestion.py --limit 10000

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
	@echo "Cleaning up..."
	@echo "Remove Conda environment? Run: conda env remove -n $(CONDA_ENV)"
	@echo "Remove venv? Delete .venv folder"
	@echo "Remove data? Delete data/raw/ and data/processed/"

