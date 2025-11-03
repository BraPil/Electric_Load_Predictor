# VoltEdge Electric Load Predictor - AI Coding Agent Instructions

## Project Overview
**VoltEdge** is an end-to-end ML pipeline + RAG/agent system for electric load prediction using Postgres/pgvector, MLflow, Docker→Kubernetes, Row-Level Security (RLS) multi-tenant isolation, optional LangChain/LangGraph and n8n, with CI/CD, observability, and security. Based on the comprehensive plan in `Documentation/Ideation/Electrical_Load_Predictor_Idea.md`.

## Architecture Overview (16-Phase Implementation)
This system follows a production-grade, enterprise-ready architecture with specific folder structure:

### VoltEdge Folder Structure
```
infra/{helm,terraform}  docker/  data/{raw,processed}
ingestion/  features/  training/  registry/  serving/
rag/  agents/{chains,graphs,tools,schemas}  evaluations/
observability/  security/  scripts/  ops/n8n  .github/workflows
```

### Core Components & Protocols
- **Data Pipeline** (`ingestion/`): UCI dataset ingestion with Great Expectations validation, hash verification
- **Feature Engineering** (`features/`): Time-series features with `source_commit` tracking in `features_hourly` table
- **Models** (`training/`, `registry/`): MLflow-tracked models (Linear, RF, GBM, MLP) with backtesting and SHAP artifacts
- **API/Service** (`serving/`): FastAPI with `/predict`, `/explain`, `/reload` endpoints, Redis caching, <200ms p95
- **RAG System** (`rag/`): Hybrid FTS+ANN retrieval on pgvector with citation-based answers or ABSTAIN
- **Agents** (`agents/`): LangChain/LangGraph with tool-calling (PR, Jira, eval tools), configurable backend
- **Multi-tenant Isolation**: Row-Level Security (RLS) with `tenant_id` columns and API key scoping

### Critical Protocol Patterns
- **Database**: PostgreSQL with pgvector extension, RLS policies, `SET app.tenant_id` middleware pattern
- **MLflow Integration**: Model versioning (Staging→Production), artifact storage in MinIO S3
- **Security**: Tenant isolation, PII redaction, audit logs, threat model documentation
- **Observability**: OTel tracing, Prometheus metrics, structured logs with `request_id`/`tenant_id`

## Development Protocols & Workflows

### Phase-Based Development Protocol
Follow the 16-phase implementation plan from `Documentation/Ideation/Electrical_Load_Predictor_Idea.md`:
1. **Phase 0-1**: Local infra (docker-compose), repo scaffolding with Makefile targets
2. **Phase 2-3**: UCI data ingestion + feature engineering with quality checks
3. **Phase 4-5**: MLflow model training (5 algorithms) + FastAPI serving with explanations
4. **Phase 6**: RLS multi-tenant isolation with `tenant_id` policies
5. **Phase 7-8**: Hybrid retrieval + LangChain/LangGraph agents
# VoltEdge Electric Load Predictor - AI Coding Agent Instructions

## Project Overview
**VoltEdge** is an end-to-end ML pipeline + RAG/agent system for electric load prediction using Postgres/pgvector, MLflow, Docker→Kubernetes, Row-Level Security (RLS) multi-tenant isolation, optional LangChain/LangGraph and n8n, with CI/CD, observability, and security. Based on the comprehensive plan in `Documentation/Ideation/Electrical_Load_Predictor_Idea.md`.

## Architecture Overview (16-Phase Implementation)
This system follows a production-grade, enterprise-ready architecture with specific folder structure:

### VoltEdge Folder Structure
```
infra/{helm,terraform}  docker/  data/{raw,processed}
ingestion/  features/  training/  registry/  serving/
rag/  agents/{chains,graphs,tools,schemas}  evaluations/
observability/  security/  scripts/  ops/n8n  .github/workflows
```

### Core Components & Protocols
- **Data Pipeline** (`ingestion/`): UCI dataset ingestion with Great Expectations validation, hash verification
- **Feature Engineering** (`features/`): Time-series features with `source_commit` tracking in `features_hourly` table
- **Models** (`training/`, `registry/`): MLflow-tracked models (Linear, RF, GBM, MLP) with backtesting and SHAP artifacts
- **API/Service** (`serving/`): FastAPI with `/predict`, `/explain`, `/reload` endpoints, Redis caching, <200ms p95
- **RAG System** (`rag/`): Hybrid FTS+ANN retrieval on pgvector with citation-based answers or ABSTAIN
- **Agents** (`agents/`): LangChain/LangGraph with tool-calling (PR, Jira, eval tools), configurable backend
- **Multi-tenant Isolation**: Row-Level Security (RLS) with `tenant_id` columns and API key scoping

### Critical Protocol Patterns
- **Database**: PostgreSQL with pgvector extension, RLS policies, `SET app.tenant_id` middleware pattern
- **MLflow Integration**: Model versioning (Staging→Production), artifact storage in MinIO S3
- **Security**: Tenant isolation, PII redaction, audit logs, threat model documentation
- **Observability**: OTel tracing, Prometheus metrics, structured logs with `request_id`/`tenant_id`

## Development Protocols & Workflows

### Phase-Based Development Protocol
Follow the 16-phase implementation plan from `Documentation/Ideation/Electrical_Load_Predictor_Idea.md`:
1. **Phase 0-1**: Local infra (docker-compose), repo scaffolding with Makefile targets
2. **Phase 2-3**: UCI data ingestion + feature engineering with quality checks
3. **Phase 4-5**: MLflow model training (5 algorithms) + FastAPI serving with explanations
4. **Phase 6**: RLS multi-tenant isolation with `tenant_id` policies
5. **Phase 7-8**: Hybrid retrieval + LangChain/LangGraph agents
6. **Phase 9-16**: Workers, evals, observability, K8s, security, docs

### Critical Makefile Targets
```bash
make bootstrap  # Initial setup
make ingest     # Load UCI dataset with validation
make features   # Generate features_hourly table
make train      # Run all 5 models, register champion
make serve      # Start FastAPI with cached predictions
make eval       # Run evaluation pipeline
make index      # Build RAG embeddings index
make up/down    # Docker compose lifecycle
```

### Database Protocols
#### RLS Multi-Tenant Pattern
```sql
-- Add tenant_id to all tables
ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON rag_chunks 
  USING (tenant_id = current_setting('app.tenant_id')::text);
```
#### Required in API middleware:
```python
# Set tenant context per request
await conn.execute("SET app.tenant_id = %s", tenant_id)
```

### MLflow Model Registry Protocol
- **Staging**: New models automatically registered after training
- **Production**: Promoted only after canary deployment + SLO validation
- **Artifacts**: Include SHAP plots, backtesting results, model metadata
- **Rollback**: Automatic on SLO breach during canary (Phase 10-12)

### API Endpoint Protocols
#### Required Endpoints:
- `GET /healthz` - Health check
- `POST /predict` - Single & batch predictions (cached, <200ms p95)
- `GET /explain/{id}` - SHAP/feature importance explanations
- `POST /reload` - Hot-swap latest Production model
- `POST /ask` - RAG Q&A with citations or ABSTAIN

#### Request/Response Patterns:
- Pydantic models for validation
- Include `tenant_id` in headers
- Log `request_id`, `latency_ms`, `model_version`, `doc_refs`

### RAG & Agent Protocols
#### Hybrid Retrieval Pattern:
- **Storage**: PostgreSQL pgvector with `content`, `fts`, `embedding`, `doc_path`, `revision`, `tenant_id`
- **Query**: Blend FTS (tsvector) + ANN (ivfflat) with normalized scores (0.5/0.5)
- **Re-ranking**: Optional cross-encoder step for top-K results
- **Responses**: Citation-based answers ONLY from chunks, or ABSTAIN if insufficient

#### Agent Architecture:
```python
# LangChain LCEL: retriever → prompt → LLM → JSON schema
# LangGraph: planner → retrieve → solve → critic → (abstain|HIL)
# Tool calling: pr_tool.py, jira_tool.py, eval_tool.py
# Config: AGENT_BACKEND=langgraph|langchain|minimal
```

### Security & Compliance Protocols
- **PII Redaction**: Pre-prompt & post-output filters
- **Audit Logs**: Immutable append table (user, time, model_version, commit SHA)
- **Threat Model**: Document prompt injection, tool abuse, data exfiltration mitigations
- **RLS Testing**: Integration tests proving tenant A cannot read tenant B data

### Observability Protocols
#### Required Structured Logs:
- `request_id`, `tenant_id`, `route`, `latency_ms`, `token_count`, `model_version`, `doc_refs`

#### Required Metrics (Prometheus):
- p95 latency (API), cache hit rate, queue depth
- ANN recall %, Postgres query time, cost/req estimate

#### OTel Tracing Around:
- Retriever calls, LLM requests, re-ranking, DB queries

### Testing Protocols
- **Unit**: Feature engineering functions, tenant isolation
- **Integration**: Full prediction pipeline, RAG retrieval
- **Model Performance**: Backtesting with historical validation
- **API**: Realistic load scenarios with tenant scoping
- **Security**: Cross-tenant access attempts (must fail)

## Environment Configuration

### Required Services (.env):
```
DATABASE_URL=postgresql+psycopg2://voltedge:voltedge@postgres:5432/voltedge
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_ARTIFACT_ROOT=s3://mlflow
REDIS_URL=redis://redis:6379/0
```

### Docker Compose Stack:
- postgres (pgvector), mlflow, minio, redis, api, worker

## Key Dependencies (Typical)
- **pandas, numpy**: Data manipulation
- **scikit-learn**: Traditional ML models
- **tensorflow/pytorch**: Deep learning for complex patterns
- **fastapi/flask**: API development
- **pytest**: Testing framework
- **mlflow**: Model tracking and deployment

## Critical Workflows
- **Model Training**: `python scripts/train_model.py --config config/training.yaml`
- **Data Pipeline**: `python scripts/process_data.py --start-date YYYY-MM-DD`
- **API Server**: `uvicorn src.api.main:app --reload` (for FastAPI)
- **Evaluation**: `python scripts/evaluate_model.py --model-version v1.0`

## Domain-Specific Considerations
- Handle seasonal patterns (daily, weekly, yearly cycles)
- Account for weather dependencies (temperature, humidity impact on AC/heating loads)
- Consider special events and holidays that affect consumption patterns
- Implement real-time data validation for sensor anomalies
- Design for grid-specific characteristics (residential vs industrial loads)

## Performance & Monitoring
- Track prediction accuracy metrics (MAPE, RMSE) by time horizon
- Monitor data drift in input features
- Implement alerts for prediction confidence drops
- Log model inference times for API performance

This is a living document - update as the project architecture evolves.

## Master Protocol & Master Log (required)

All agents MUST consult the repository master protocol and master log before starting work.

- Master protocol: `Documentation/Protocols/master_protocol.md` (contains the Prime Directive, Anti-Sampling Directive, launch checklist, and sub-protocol index).
- Master log: `Documentation/Protocols/master_log.md` (tracks sub-protocols, logs and last-updated timestamps).

Enforcement rules (for each prompt/response cycle):
1. Load and acknowledge `Documentation/Protocols/master_protocol.md` and `Documentation/Protocols/master_log.md` in full before performing high-level tasks.
2. Apply the Universal Anti-Sampling Directive: files <= 10,000 lines must be read in full; files > 10,000 lines require explicit authorization (log and request approval).
3. Create or append a short log entry in `Documentation/logs/` with timestamp, task summary, and chosen sub-protocol(s) before starting work. Use `logging_sub_protocol.md` conventions.
4. If a violation or limitation is encountered (e.g., filename-too-long, checkout failure, missing permissions), immediately write a `violation_YYYY-MM-DD.md` note in `Documentation/logs/` and pause.

Paths and naming conventions:
- Sub-protocol files: `Documentation/Protocols/<name>_sub_protocol.md`
- Operational logs: `Documentation/logs/YYYY-MM-DD_task-slug.md`

If you want, I can now produce initial stub files for each core sub-protocol listed in `Documentation/Protocols/` and create an empty `Documentation/logs/README.md` to document logging conventions. Say "create stubs" to proceed.