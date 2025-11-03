# Electric_Load_Predictor — MASTER PROTOCOL
## Canonical control file for protocol selection, anti-sampling, and launch checks

This master protocol ("the master protocol") is the authoritative, machine-readable set of rules and indexes that every AI coding agent and developer MUST consult before performing work in this repository.

Last updated: 2025-11-02
Status: ACTIVE

---

## Prime Directive

To use current and historical data to predict current/future usage and turn that into an endpoint RAG that can serve as a SaaS point for users or other agents.

This is the repository's single highest-level goal and must be referenced at the start of each task.

---

## Universal Anti-Sampling Directive

Purpose: Ensure 100% fidelity when analyzing repository contents and avoid making assumptions based on partial reads.

Rules:
- Always prefer reading the entire content of a file before making decisions that depend on it.
- Files <= 10,000 lines: read the full file; sampling is forbidden.
- Files > 10,000 lines: do not sample without explicit authorization from the repository owner; raise an alert and request permission to proceed with a sampling strategy or with resources for full ingestion.
- Configuration, schema, and integration files (e.g., DB schema, API contract, deployment manifests) must always be read in full regardless of size.
- If a tool cannot read a full file due to environment constraints (filename length, permission, etc.), log the limitation in the `Documentation/logs/` folder and request manual inspection.

Violation handling:
- Any instance of sampling without documented justification must be logged to the protocol violation log and the agent must halt related work until the violation is acknowledged and remediated.

---

## Required Launch Protocol (checked at start of every prompt/response cycle)

Before starting or continuing work, the agent must perform the following checks and record the completion in the master log:
1. Confirm the Prime Directive is understood and applicable to the current task.
2. Confirm Anti-Sampling Directive is acknowledged for any files to be read.
3. Identify and select the primary sub-protocol(s) required for the task (see Sub-Protocols section).
4. Ensure an appropriate log file exists in `Documentation/logs/` and write a short entry with timestamp, task summary, and selected protocol(s).
5. If any file to be read exceeds 10,000 lines, pause and request authorization.

---

## Sub-Protocols (index)

The master protocol references a set of sub-protocol files. Each sub-protocol is stored in `Documentation/Protocols/` and must follow the naming convention: `<name>_sub_protocol.md`.

Core sub-protocols to create/maintain:
- `analysis_sub_protocol.md` — Read every single word of outputs and inputs; produce fully comprehensive, line-by-line analyses when called.
- `research_sub_protocol.md` — Identify and fetch tools, data sources, SDKs, and references required; document gaps and request missing items.
- `generation_sub_protocol.md` — Rules for code/text generation. NOTE: special characters and emojis are strictly prohibited in repository artifacts unless explicitly authorized.
- `logging_sub_protocol.md` — Logging standards: where logs live (`Documentation/logs/`), naming conventions (`YYYY-MM-DD_taskname.md`), required fields, and rotation/retention.
- `tool_identification_sub_protocol.md` — How to select and validate external tools and MCPs for tasks.
- `reference_material_identification_sub_protocol.md` — How to select canonical reference materials and SDK docs.
- `tool_and_reference_material_request_sub_protocol.md` — How to request new access, tokens, or files from the repository owner or stakeholders.

Agents must consult the sub-protocol index in the master log before proceeding. New sub-protocols should be added via pull request and linked from the master log.

---

## Master Log Reference

The master protocol delegates runtime indexing to the `master_log.md` file (path: `Documentation/Protocols/master_log.md`). The master log tracks sub-protocols, their locations, last-updated timestamps, and the current authoritative contact.

---

## Enforcement & Compliance

- The master protocol MUST be referenced at the start of every high-level task.
- The anti-sampling directive is mandatory and non-negotiable without explicit authorization.
- All protocol violations, restarts, and major decisions must be recorded in the master log and the `Documentation/logs/` folder.

---

## Minimal Machine Checklist (to be run programmatically at task start)

1. Load `Documentation/Protocols/master_protocol.md` and `Documentation/Protocols/master_log.md` in full.
2. Verify the Prime Directive string matches the repository's expected prime directive.
3. Check whether any target files exceed the anti-sampling threshold; if so, flag for authorization.
4. Create or append an entry in the appropriate log under `Documentation/logs/` with timestamp, agent name, and selected sub-protocols.

---
```markdown
# Electric_Load_Predictor — MASTER PROTOCOL
## Canonical control file for protocol selection, anti-sampling, and launch checks

This master protocol ("the master protocol") is the authoritative, machine-readable set of rules and indexes that every AI coding agent and developer MUST consult before performing work in this repository.

Last updated: 2025-11-02
Status: ACTIVE

---

## Prime Directive

To use current and historical data to predict current/future usage and turn that into an endpoint RAG that can serve as a SaaS point for users or other agents.

This is the repository's single highest-level goal and must be referenced at the start of each task.

---

## Universal Anti-Sampling Directive

Purpose: Ensure 100% fidelity when analyzing repository contents and avoid making assumptions based on partial reads.

Rules:
- Always prefer reading the entire content of a file before making decisions that depend on it.
- Files <= 10,000 lines: read the full file; sampling is forbidden.
- Files > 10,000 lines: do not sample without explicit authorization from the repository owner; raise an alert and request permission to proceed with a sampling strategy or with resources for full ingestion.
- Configuration, schema, and integration files (e.g., DB schema, API contract, deployment manifests) must always be read in full regardless of size.
- If a tool cannot read a full file due to environment constraints (filename length, permission, etc.), log the limitation in the `Documentation/logs/` folder and request manual inspection.

Violation handling:
- Any instance of sampling without documented justification must be logged to the protocol violation log and the agent must halt related work until the violation is acknowledged and remediated.

---

## Required Launch Protocol (checked at start of every prompt/response cycle)

Before starting or continuing work, the agent must perform the following checks and record the completion in the master log:
1. Confirm the Prime Directive is understood and applicable to the current task.
2. Confirm Anti-Sampling Directive is acknowledged for any files to be read.
3. Identify and select the primary sub-protocol(s) required for the task (see Sub-Protocols section).
4. Ensure an appropriate log file exists in `Documentation/logs/` and write a short entry with timestamp, task summary, and selected protocol(s).
5. If any file to be read exceeds 10,000 lines, pause and request authorization.

---

## Sub-Protocols (index)

The master protocol references a set of sub-protocol files. Each sub-protocol is stored in `Documentation/Protocols/` and must follow the naming convention: `<name>_sub_protocol.md`.

Core sub-protocols to create/maintain:
- `analysis_sub_protocol.md` — Read every single word of outputs and inputs; produce fully comprehensive, line-by-line analyses when called.
- `research_sub_protocol.md` — Identify and fetch tools, data sources, SDKs, and references required; document gaps and request missing items.
- `generation_sub_protocol.md` — Rules for code/text generation. NOTE: special characters and emojis are strictly prohibited in repository artifacts unless explicitly authorized.
- `logging_sub_protocol.md` — Logging standards: where logs live (`Documentation/logs/`), naming conventions (`YYYY-MM-DD_taskname.md`), required fields, and rotation/retention.
- `tool_identification_sub_protocol.md` — How to select and validate external tools and MCPs for tasks.
- `reference_material_identification_sub_protocol.md` — How to select canonical reference materials and SDK docs.
- `tool_and_reference_material_request_sub_protocol.md` — How to request new access, tokens, or files from the repository owner or stakeholders.

Agents must consult the sub-protocol index in the master log before proceeding. New sub-protocols should be added via pull request and linked from the master log.

---

## Master Log Reference

The master protocol delegates runtime indexing to the `master_log.md` file (path: `Documentation/Protocols/master_log.md`). The master log tracks sub-protocols, their locations, last-updated timestamps, and the current authoritative contact.

---

## Enforcement & Compliance

- The master protocol MUST be referenced at the start of every high-level task.
- The anti-sampling directive is mandatory and non-negotiable without explicit authorization.
- All protocol violations, restarts, and major decisions must be recorded in the master log and the `Documentation/logs/` folder.

---

## Minimal Machine Checklist (to be run programmatically at task start)

1. Load `Documentation/Protocols/master_protocol.md` and `Documentation/Protocols/master_log.md` in full.
2. Verify the Prime Directive string matches the repository's expected prime directive.
3. Check whether any target files exceed the anti-sampling threshold; if so, flag for authorization.
4. Create or append an entry in the appropriate log under `Documentation/logs/` with timestamp, agent name, and selected sub-protocols.

---
```
