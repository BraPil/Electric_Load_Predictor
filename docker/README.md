Docker Compose local development stack
=====================================

This directory contains a minimal `docker-compose.yml` to run a local development stack for VoltEdge. It is intentionally small and intended for development and testing only.

Services included
- `postgres` (Postgres 15 with pgvector enabled) — exposes 5432
- `mlflow` (mlflow server) — exposes 5000
- `minio` (S3-compatible object store) — exposes 9000 (API) and 9001 (console)
- `redis` — exposes 6379
- `api` — placeholder service that runs the FastAPI app on port 8000
- `worker` — placeholder for background workers (Celery/RQ)

Notes
- The Postgres service uses an init script in `docker/postgres/initdb/init_extensions.sql` which creates the `voltedge` user/db and enables the `vector` and `pg_trgm` extensions. That script runs only on first container startup.
- MLflow in this compose runs a simple MLflow server with a local SQLite backend and a volume for artifacts. For production, point MLflow to a proper tracking server and object storage.
- MinIO runs with default credentials from `.env.example` (minioadmin/minioadmin). Change these in production and do not commit secrets.

Running locally
----------------
1. Copy `.env.example` to `.env` and edit values if needed.

```powershell
copy .env.example .env
```

2. Start the stack (uses Docker Compose v2+ syntax):

```powershell
docker compose -f docker/docker-compose.yml up -d
```

3. Check health:

```powershell
docker compose -f docker/docker-compose.yml ps
```

4. Stop the stack:

```powershell
docker compose -f docker/docker-compose.yml down
```

Troubleshooting
- If Postgres fails to start because the volume contains a previous non-pgvector init, remove the `pgdata` volume and restart (data will be lost):

```powershell
docker volume rm <repo_folder>_pgdata
```

Security
- Do NOT commit `.env` with secrets. Use `.env.example` as a template only.
