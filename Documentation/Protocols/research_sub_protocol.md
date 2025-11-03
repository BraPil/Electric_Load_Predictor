# research_sub_protocol.md — Research Sub-Protocol

Purpose: define how to identify, fetch, and vet external references, SDKs, APIs, and data sources needed for a task.

Contract (short):
- Inputs: research question, required languages/frameworks, constraints (license, offline availability).
- Outputs: a curated list of authoritative references (title, URL, snippet, version), a short risk note, and a recommended next action.

Core steps:
1. Document the research objective and constraints.
2. Prioritize official vendor docs, standards, and up-to-date guides (stable release docs preferred over blog posts).
3. Record the exact URLs and versions; capture a small excerpt and a short rationale for selection.
4. Check licenses and compatibility; flag anything with restrictive licensing.
5. Summarize findings and propose concrete code or infra actions.

Vetting checklist:
- Prefer official docs (e.g., PostgreSQL, MLflow, FastAPI) and stable releases.
- If using a third-party tutorial or blog, mark it as secondary and capture author and date.
- For code samples, ensure they compile or run in a minimal environment (or note steps to reproduce).

Logging: create a short `Documentation/logs/` entry that lists the references and the chosen sub-protocol(s).
