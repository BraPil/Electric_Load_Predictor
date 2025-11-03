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

Change control
--------------
- All changes to `master_plan.md` require a PR with at least one reviewer. Security-impacting tasks require a security reviewer before merge.
