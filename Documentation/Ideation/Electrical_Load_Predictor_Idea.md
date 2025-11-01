# Electrical Load Predictor — End-to-End Plan (VoltEdge)

This document outlines a full, actionable plan to build **VoltEdge**: an end‑to‑end ML pipeline + RAG/agent system using Postgres/pgvector, MLflow, Docker→Kubernetes, Row‑Level Security (RLS) multi‑tenant isolation, optional LangChain/LangGraph and n8n, with CI/CD, observability, and security.

---

## Phase 0 — Groundwork & Repo Scaffolding
**Goal:** Create a clean repo skeleton that runs locally.

**Tasks**
- [T-00] Create repo `voltedge` with the folders below and MIT license.
- [T-01] Add `pyproject.toml` (uv/poetry/pip-tools); pin Python 3.11+.
- [T-02] Add base folders:
  ```
  infra/{helm,terraform}  docker/  data/{raw,processed}
  ingestion/  features/  training/  registry/  serving/
  rag/  agents/{chains,graphs,tools,schemas}  evaluations/
  observability/  security/  scripts/  ops/n8n  .github/workflows
  ```
- [T-03] Add `README.md` with a 2-minute run guide and architecture diagram.
- [T-04] Add `Makefile` with targets: `bootstrap`, `ingest`, `train`, `serve`, `eval`, `index`, `up`, `down`.

**Deliverables / Acceptance**
- Repo compiles, `make bootstrap` succeeds.
- `README` shows local quickstart steps.

---

## Phase 1 — Local Infra (Docker Compose: Postgres/pgvector, MLflow, MinIO)
**Goal:** Bring up dev infra locally.

**Tasks**
- [T-10] `docker-compose.yml` with services: `postgres(pgvector)`, `mlflow`, `minio`, `redis` (for workers), `api`, `worker`.
- [T-11] Init script to enable `vector` and `pg_trgm` extensions.
- [T-12] Create MLflow bucket in MinIO on start.
- [T-13] Add `.env` with:
  ```
  DATABASE_URL=postgresql+psycopg2://voltedge:voltedge@postgres:5432/voltedge
  MLFLOW_TRACKING_URI=http://mlflow:5000
  MLFLOW_ARTIFACT_ROOT=s3://mlflow
  REDIS_URL=redis://redis:6379/0
  ```

**Deliverables / Acceptance**
- `make up` starts all services; healthchecks pass.
- MLflow UI reachable; Postgres has `vector` extension.

---

## Phase 2 — Data Ingestion & Validation (UCI dataset)
**Goal:** Download, validate, and land clean tables.

**Tasks**
- [T-20] `ingestion/fetch_uci.py`: download/mirror dataset; compute file hash.
- [T-21] `ingestion/etl.py`: parse dates/timezone, impute gaps, resample, write to `usage_hourly` and `usage_minute` tables.
- [T-22] Add Great Expectations or pydantic checks for schema, nulls, ranges; write results to a `data_quality` table.

**Deliverables / Acceptance**
- `make ingest` loads data; row counts logged.
- Data quality report stored and visible.

---

## Phase 3 — Feature Engineering
**Goal:** Produce feature store for forecasting & classification baselines.

**Tasks**
- [T-30] `features/feature_store.py`:
  - rolling mean/std, lags, daypart, weekday, holidays
  - optional (stub) join for weather (leave toggled off for now)
- [T-31] Persist features as `features_hourly` table; record `source_commit`, `created_at`.

**Deliverables / Acceptance**
- `make features` populates `features_hourly`.
- Basic EDA notebook saved to `/notebooks` (optional).

---

## Phase 4 — Modeling (Baselines + Tree/GBM + Small NN)
**Goal:** Multiple models tracked in MLflow; pick a champion.

**Tasks**
- [T-40] Linear Regression baseline (MAE/MAPE/RMSE).
- [T-41] Logistic Regression (optional “peak hour” classifier).
- [T-42] Random Forest regressor.
- [T-43] Gradient Boosting (LightGBM or XGBoost).
- [T-44] Small MLP (sklearn MLPRegressor or PyTorch tiny MLP).
- [T-45] Backtesting utility (sliding windows); store metrics per split.
- [T-46] `registry/mlflow_client.py`: log params, metrics, artifacts; register best as `voltedge-forecaster` in `Staging`.

**Deliverables / Acceptance**
- `make train` logs all experiments to MLflow; champion chosen by MAE.
- Artifact: SHAP summary plot (for tree/GBM) stored in MLflow.

---

## Phase 5 — Serving API (FastAPI) + Explanations
**Goal:** Low-latency predictions with basic explainability.

**Tasks**
- [T-50] `serving/app.py`: endpoints
  - `GET /healthz`
  - `POST /predict` (single & batch)
  - `GET /explain/{id}` (returns SHAP summary or feature importances)
  - `POST /reload` (pull latest “Production” model)
- [T-51] Cache short-horizon predictions (in-memory/Redis).
- [T-52] Pydantic models for requests/responses; OpenAPI docs.

**Deliverables / Acceptance**
- p95 `< 200ms` for cached recent horizons; correctness tests pass.
- `/reload` switches to latest MLflow Production version.

---

## Phase 6 — RLS Multi-Tenant Isolation
**Goal:** Hard isolation in Postgres with API-level scoping.

**Tasks**
- [T-60] Add `tenant_id` columns to all tables (data, features, chunks, logs).
- [T-61] RLS policies (SQL):
  ```sql
  ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;
  CREATE POLICY tenant_isolation ON rag_chunks
    USING (tenant_id = current_setting('app.tenant_id')::text);
  ```
- [T-62] In API middleware, set `SET app.tenant_id = :tenant` for each connection from tenant API key.
- [T-63] Add tests proving tenant A cannot read tenant B data.

**Deliverables / Acceptance**
- Requests require tenant API key; cross-tenant reads fail by policy.
- All structured logs include `tenant_id`.

---

## Phase 7 — Retrieval (Hybrid FTS + ANN on pgvector)
**Goal:** Code/docs/data retrieval with hybrid ranking & re-ranking.

**Tasks**
- [T-70] `rag/index_builder.py`: chunk repo docs, README, data dictionary, `feature_store.py`, and pipeline comments; store:
  - `content`, `fts`, `embedding`, `doc_path`, `revision`, `tenant_id`.
- [T-71] SQL hybrid query: FTS (tsvector) + ANN (`ivfflat`), normalize scores, blend (e.g., 0.5/0.5).
- [T-72] Optional cross-encoder re-rank (top-K) step; timebox it.
- [T-73] Add `rag/retriever_pgvector.py` interface (`search(query, tenant_id) -> chunks`).

**Deliverables / Acceptance**
- `make index` builds index; `search` returns K chunks with doc path & rev.
- Regression tests for ranking relevance on a small golden set.

---

## Phase 8 — Agents & Orchestration (LangChain + LangGraph, optional)
**Goal:** Q&A with citations + tool-calling (open PR, file issue, run eval).

**Tasks**
- [T-80] `agents/tools/search_tool.py` wraps pgvector retriever.
- [T-81] LCEL chain `agents/chains/rag_chain.py`: retriever → prompt → LLM → JSON schema; answers **only** from chunks; **ABSTAIN** if insufficient.
- [T-82] LangGraph `agents/graphs/support_graph.py`: planner → retrieve → solve → critic → (abstain|HIL).
- [T-83] Tools: `pr_tool.py`, `jira_tool.py`, `eval_tool.py` (stub integration).
- [T-84] Config toggle `AGENT_BACKEND=langgraph|langchain|minimal`.

**Deliverables / Acceptance**
- `/ask` endpoint returns grounded answers with citations or ABSTAIN.
- Graph can be paused/resumed; traces visible in logs/OTel.

---

## Phase 9 — Workers & Jobs
**Goal:** Offload long tasks & scheduled ops.

**Tasks**
- [T-90] `serving/workers.py` (Celery/RQ):
  - build embeddings, rebuild index
  - nightly eval run
  - batch scoring (optional)
  - retraining trigger (optional)
- [T-91] Retry policy (jitter, backoff), dedupe keys, dead-letter queue metrics.

**Deliverables / Acceptance**
- Queue depth metrics exposed; failed tasks retried per policy.
- `make eval` triggers worker job; results stored and reported.

---

## Phase 10 — Evals, SLOs, Drift & Auto-Rollback
**Goal:** Quantify quality; protect prod with canary + rollback.

**Tasks**
- [T-100] `evaluations/llm_evals.py`: grounding rate, citation correctness, abstain rate; golden sets per tenant.
- [T-101] Forecast evals: MAE/MAPE vs backtests; thresholds per stage.
- [T-102] Store eval results (per model version) to `model_eval_results`.
- [T-103] Define SLOs: p95 latency, grounding ≥ 90%, hallucination < 1%, cost/request budget.
- [T-104] If SLO breach during canary → auto-rollback via CD pipeline.

**Deliverables / Acceptance**
- Nightly eval job runs and posts summary to logs (and Slack via n8n).
- Canary rollback verified in a simulated failure.

---

## Phase 11 — Observability (OTel, Prometheus, Grafana)
**Goal:** Measure everything needed for reliability & cost control.

**Tasks**
- [T-110] Structured logs include: `request_id`, `tenant_id`, `route`, `latency_ms`, `token_count`, `model_version`, `doc_refs`.
- [T-111] OTel tracing around: retriever, LLM call, re-rank, DB queries.
- [T-112] Prom metrics: p95 latency (API), cache hit rate, queue depth, ANN recall %, Postgres query time, cost/req estimate.
- [T-113] Grafana dashboards JSON committed to `observability/dashboards/`.

**Deliverables / Acceptance**
- Dashboards show live metrics; alerts configured for SLOs.

---

## Phase 12 — CI/CD (GitHub Actions + Helm canary)
**Goal:** Automated test→build→deploy with gates.

**Tasks**
- [T-120] `ci.yml`: unit tests, lint, offline evals; build/push images; register MLflow model to `Staging`.
- [T-121] `cd.yml`: Helm deploy to `staging`; smoke tests; canary 5% in `prod`; SLO checks; promote MLflow model to `Production` if pass; else rollback.
- [T-122] Store SBOM and image digests; sign images (cosign, optional).

**Deliverables / Acceptance**
- Green CI → staged deployment → canary promotion observable in logs.
- Rollback path exercised.

---

## Phase 13 — Kubernetes (Helm + HPA)
**Goal:** Production-style deployment with autoscaling.

**Tasks**
- [T-130] Helm charts: `infra/helm/api`, `worker`, `mlflow`, `postgres` (local demo), `minio` (local).
- [T-131] Liveness/readiness probes; Resource requests/limits.
- [T-132] **HPA**:
  - API: scale on CPU and custom metric (p95 latency via adapter).
  - Worker: scale on queue depth.
- [T-133] NetworkPolicy to isolate pods; Pod Disruption Budgets.
- [T-134] Secrets & ConfigMaps; optional Key Vault CSI in cloud.

**Deliverables / Acceptance**
- `helm upgrade` deploys; HPA reacts under artificial load; NP blocks disallowed traffic.

---

## Phase 14 — Security & Governance
**Goal:** Minimal, strong defaults suitable for regulated environments.

**Tasks**
- [T-140] `security/policy.md` (data handling, masking/PII redaction, no raw prompts in logs).
- [T-141] Redaction pre-prompt & post-output filters.
- [T-142] Audit log table: immutable append of approvals & promotions (user, time, model_version, commit SHA).
- [T-143] Threat model (`security/threat_model.md`): prompt injection, tool abuse, data exfiltration; mitigations listed.

**Deliverables / Acceptance**
- Security docs present and referenced in README; basic redaction unit tests pass.

---

## Phase 15 — n8n (Optional Glue)
**Goal:** Operator-friendly automations that are non-critical.

**Tasks**
- [T-150] Flow: nightly eval → Slack/Teams summary.
- [T-151] Flow: on model promotion → announce + release notes.
- [T-152] Flow: post-merge in `main` → trigger index rebuild.

**Deliverables / Acceptance**
- Flows exportable/importable (JSON) and documented; disabling n8n does not break core system.

---

## Phase 16 — Docs & Demo Script
**Goal:** Make it easy to show and discuss in interviews.

**Tasks**
- [T-160] `README` sections:
  - Why: Unblocked & LivaNova alignment (one paragraph each)
  - Quickstart (local), Overview diagram, Architecture choices
  - Multi-tenant (RLS) explainer
  - Hybrid FTS+ANN explainer
  - K8s & HPA explainer
  - Evals & rollback explainer
- [T-161] `DEMO.md`: a 7-step demo flow (ingest→train→serve→ask→eval→canary→rollback).
- [T-162] `OPERATIONS.md`: runbooks for common ops (index rebuild, drift event, rollback).

**Deliverables / Acceptance**
- You can follow `DEMO.md` start-to-finish without guessing.
- Interview “why” answers trace directly to docs.

---

## Stretch Goals
- Swap retriever to **Azure AI Search** or **Pinecone** via feature flag; document trade-offs.
- Add **routing** to small local model for easy intents; log cost savings.
- Add **fine-tuning** or adapters for the LLM; compare eval deltas.
- Azure cloudization: AKS, Azure Database for PostgreSQL (pgvector), Blob, Key Vault, Private Endpoints.

---

## Risks & Mitigations
- **Scope creep:** Lock Phase 0–12 first; LangGraph/n8n are optional toggles.
- **RLS footguns:** Integration tests that prove isolation; never bypass `SET app.tenant_id`.
- **ANN recall issues:** Keep re-rank optional and measured; tune `ivfflat` lists; monitor ANN recall metric.
- **Cost/latency:** Cache hot paths; set token budgets; HPA on queue depth; nightly cost report.

---

## Definition of Done
- Local `docker-compose up` gives a working stack with predictions, RAG answers (with citations or ABSTAIN), MLflow registry, and dashboards.
- CI passes, CD canaries & promotes with SLO gates; rollback verified.
- K8s deploy scales with HPA; RLS isolation proven; logs & metrics complete.
- Docs enable a clean 5–10 minute live demo + deep technical Q&A.
