# Master Plan

Purpose
-------
The `master_plan.md` contains the active, prioritized plan for achieving the repository's Prime Directive. It is a living document that is updated via the Planning Sub-Protocol and must always be accompanied by a per-plan issue log in `Documentation/logs/`.

Schema / Structure
------------------
- meta:
  - last_updated: YYYY-MM-DD
  - owner: @repo-owner
  - prime_directive: short statement or link to `master_protocol.md`

- tasks: (ordered list of atomic tasks)
  - id: task-slug
    title: short title
    description: 1-2 lines
    owner: @handle
    estimate: 4h
    dependencies: []
    acceptance_criteria:
      - criterion 1
      - criterion 2
    status: todo | in-progress | blocked | done
    notes: optional

How to use
----------
1. Open this file when starting a planning session. Follow `Documentation/Protocols/planning_sub_protocol.md` to break goals into tasks.
2. Each modification must be accompanied by a per-plan issue log in `Documentation/logs/` and an update to `Documentation/Protocols/master_log.md`.
3. Keep tasks small. If a task is estimated > 8h, decompose further.

Example
-------
- meta:
  - last_updated: 2025-11-03
  - owner: @repo-owner
  - prime_directive: Deliver a reliable, multi-tenant electric load predictor with RAG-based explainability.

- tasks:
  - id: dataset-ingest-01
    title: ingest UCI power dataset
    description: download, validate and store raw UCI dataset in `data/raw/`
    owner: @repo-owner
    estimate: 6h
    dependencies: []
    acceptance_criteria:
      - raw files exist in `data/raw/` with checksum
      - GE expectations tests pass
    status: todo

  ## Phase 0 — Repo scaffold (derived from Ideation)

  - id: phase0-repo-scaffold
    title: repository scaffold and developer quickstart
    description: create pyproject, requirements, folder structure, Makefile targets and README quickstart
    owner: @repo-owner
    estimate: 3h
    dependencies: []
    acceptance_criteria:
      - `pyproject.toml` or `requirements.txt` present
      - base folders created and tracked
      - `Makefile` with bootstrap target present
      - `README.md` contains a 2-minute quickstart
    status: in-progress

  ### Phase 0 tasks (suggested atomic tasks)
  - id: phase0-create-deps
    title: add pyproject and requirements
    description: add pyproject.toml and requirements.txt for Python 3.11+
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria: [pyproject.toml exists, requirements.txt exists]
    status: done

  ## Phase 1 — Local dev infra (docker compose)

  - id: phase1-local-infra
    title: local dev infra (docker-compose)
    description: bring up Postgres (pgvector), MLflow, MinIO, Redis, API and worker in docker-compose for local development
    owner: @repo-owner
    estimate: 6h
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria:
      - `docker/docker-compose.yml` present and documented
      - Postgres has `vector` extension enabled on init
      - MLflow reachable at configured port
      - `.env.example` present
    status: in-progress

  ### Phase 1 tasks (atomic)
  - id: phase1-docker-compose
    title: add docker/docker-compose.yml
    description: compose file with postgres (pgvector), mlflow, minio, redis, api, worker
    owner: @repo-owner
    estimate: 2h
    dependencies: [phase1-local-infra]
    acceptance_criteria:
      - `docker/docker-compose.yml` exists
      - compose brings up services (manual validation)
    status: done

  - id: phase1-init-extensions
    title: init DB and enable extensions
    description: add SQL scripts to enable pgvector and pg_trgm on first run
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase1-docker-compose]
    acceptance_criteria: `docker/postgres/initdb/init_extensions.sql` exists and extensions are created on fresh DB
    status: done

  - id: phase1-mlflow-bucket
    title: create MLflow artifact bucket in MinIO
    description: ensure MLflow stores artifacts to a MinIO bucket on start (or document manual creation)
    owner: @repo-owner
    estimate: 1h
    dependencies: [phase1-docker-compose]
    acceptance_criteria: a bucket exists in MinIO used by MLflow
    status: blocked
    notes: Requires Docker Desktop installation on Windows

  - id: phase1-env
    title: add .env example
    description: provide .env.example with connection strings and creds for local stack
    owner: @repo-owner
    estimate: 15m
    dependencies: [phase1-local-infra]
    acceptance_criteria: `.env.example` present
    status: done

  - id: phase1-healthchecks
    title: define simple healthchecks
    description: ensure each service has a basic healthcheck (postgres pg_isready, mlflow reachable)
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase1-docker-compose]
    acceptance_criteria: docker-compose healthchecks pass locally
    status: blocked
    notes: Requires Docker Desktop installation on Windows

  ## Phase 2 — Ingestion pipeline scaffold

  - id: phase2-ingestion-scaffold
    title: ingestion pipeline scaffold
    description: create ingestion module with UCI dataset fetcher and ETL pipeline
    owner: @repo-owner
    estimate: 4h
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria:
      - `ingestion/fetch_uci.py` downloads UCI dataset
      - `ingestion/etl.py` processes and loads data
      - data quality checks implemented
      - README documentation complete
    status: done

  ### Phase 2 tasks (atomic)
  - id: phase2-fetch-script
    title: create fetch_uci.py
    description: script to download UCI Individual Household Electric Power Consumption dataset
    owner: @repo-owner
    estimate: 1h
    dependencies: [phase2-ingestion-scaffold]
    acceptance_criteria:
      - downloads dataset from UCI repository
      - verifies file integrity (SHA256)
      - saves to data/raw/
      - CLI with --force and --output options
    status: done

  - id: phase2-etl-script
    title: create etl.py (Extract, Transform, Load)
    description: ETL pipeline to clean, transform, and load UCI dataset
    owner: @repo-owner
    estimate: 2h
    dependencies: [phase2-fetch-script]
    acceptance_criteria:
      - extracts data from ZIP file
      - handles missing values (marked as '?')
      - resamples 1-minute → hourly intervals
      - adds derived features (hour, day, weekend)
      - validates data quality
      - loads to Postgres and/or parquet file
      - CLI with --limit and --skip-db options
    status: done

  - id: phase2-data-quality
    title: create data_quality.py (pydantic validation)
    description: pydantic schemas for data validation
    owner: @repo-owner
    estimate: 45m
    dependencies: [phase2-ingestion-scaffold]
    acceptance_criteria:
      - PowerMeasurement schema with field validators
      - range checks (power 0-20kW, voltage 200-260V)
      - DataQualityReport model
      - validate_dataframe() function
    status: done

  - id: phase2-makefile-integration
    title: wire Makefile ingest target
    description: update Makefile to run fetch + ETL pipeline
    owner: @repo-owner
    estimate: 15m
    dependencies: [phase2-etl-script]
    acceptance_criteria: `make ingest` runs complete pipeline
    status: done

  - id: phase2-documentation
    title: create ingestion README
    description: comprehensive documentation for ingestion module
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase2-ingestion-scaffold]
    acceptance_criteria:
      - explains dataset and measurements
      - quick start guide
      - explains each script in detail
      - troubleshooting section
    status: done


  - id: phase0-create-structure
    title: create base folders
    description: create folders infra,docker,data,ingestion,features,training,registry,serving,rag,agents,evaluations,observability,security,scripts,ops/n8n
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria: [folders exist in repo]
    status: done

  - id: phase0-create-makefile
    title: add Makefile with bootstrap/ingest/etc targets
    description: create simple Makefile with placeholder targets
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria: [Makefile exists and `make bootstrap` creates venv]
    status: done

  - id: phase0-readme
    title: add README quickstart
    description: add README.md with 2-minute quickstart and next steps
    owner: @repo-owner
    estimate: 30m
    dependencies: [phase0-repo-scaffold]
    acceptance_criteria: [README.md contains quickstart and next steps]
    status: done

Change control
--------------
- All changes to `master_plan.md` require a PR with at least one reviewer. Security-impacting tasks require a security reviewer before merge.
