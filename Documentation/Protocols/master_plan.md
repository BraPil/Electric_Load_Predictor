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
