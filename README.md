# VoltEdge — Electric Load Predictor

Quickstart (2-minute)

1. Bootstrap a local Python virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) If you prefer Makefile on Unix/macOS with make installed:

```bash
make bootstrap
```

3. Start development server (after you implement `serving/app.py`):

```powershell
uvicorn serving.app:app --reload
```

What we scaffolded
- `pyproject.toml` and `requirements.txt` — minimal dependencies for Phase 0.
- `Makefile` — bootstrap and placeholder targets for common tasks.
- Base folder structure (empty folders tracked with `.gitkeep`) for infra, ingestion, features, training, serving, rag, agents, evaluations, observability, security, scripts, ops/n8n.

Next steps
- Implement `docker/docker-compose.yml` for local infra (Postgres+pgvector, MLflow, MinIO, Redis).
- Add ingestion scripts in `ingestion/` and a minimal `serving/app.py` to exercise the pipeline.

If you want, I can implement Phase 1 (docker compose) next.
# Electric_Load_Predictor
Predicts electric loads on given grids 
