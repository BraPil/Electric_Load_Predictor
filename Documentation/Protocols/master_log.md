# master_log.md — Protocol & Log Index

This file is the repository's canonical index of sub-protocols, logs and their last-updated timestamps. Agents must update this file when adding or modifying sub-protocols or creating new logs.

Last updated: 2025-11-03

## Format
- Each entry: `- YYYY-MM-DD: filename.md — short description — last-updated: YYYY-MM-DD — contact: @username`

## Sub-Protocol Index
- 2025-11-02: master_protocol.md — central master protocol — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: planning_sub_protocol.md — planning workflow and master_plan management — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: analysis_sub_protocol.md — analysis rules — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: research_sub_protocol.md — research rules — last-updated: TBD — contact: repo-owner
- 2025-11-02: generation_sub_protocol.md — generation rules (no emojis) — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: logging_sub_protocol.md — logging standards — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: tool_identification_sub_protocol.md — tool selection rules — last-updated: TBD — contact: repo-owner
- 2025-11-02: reference_material_identification_sub_protocol.md — reference material discovery — last-updated: TBD — contact: repo-owner
- 2025-11-02: tool_and_reference_material_request_sub_protocol.md — tool/reference requests — last-updated: TBD — contact: repo-owner

## Log Index (where to find granular logs)
- `Documentation/logs/` — chronological logs for tasks, named `YYYY-MM-DD_task-slug.md`

### Example log entries
- 2025-11-03: sample-plan-2025-11-03.md — initial plan log for master plan tasks — last-updated: 2025-11-03 — contact: @repo-owner
- 2025-11-03: phase0-phase1-review-2025-11-03.md — comprehensive review and improvements of Phase 0 and Phase 1 implementations — last-updated: 2025-11-03 — contact: @repo-owner
- 2025-11-03: phase1-phase2-implementation-2025-11-03.md — Phase 1 verification tasks and complete Phase 2 ingestion pipeline implementation — last-updated: 2025-11-03 — contact: @repo-owner
- 2025-11-03: restart-session-2025-11-03.md — comprehensive restart checkpoint for computer switch with complete file inventory and continuation plan — last-updated: 2025-11-03 — contact: @repo-owner
- 2025-11-03: phase2-completion-2025-11-03.md — Phase 2 completion log with demo results, lessons learned, and next steps — last-updated: 2025-11-03 — contact: @repo-owner
- 2025-11-03: restart-protocol-2025-11-03-final.md — final session checkpoint with complete state and continuation paths — last-updated: 2025-11-03 — contact: @repo-owner

## How to update
1. Create or update the sub-protocol file under `Documentation/Protocols/`.
2. Add or update the entry in this master_log with date, short description and contact.
3. Commit both files together and reference the change in a PR description.

## Violations & Restarts
- If a protocol violation occurs, add an entry here and create a `Documentation/logs/violation_YYYY-MM-DD.md` with details.
```markdown
# master_log.md — Protocol & Log Index

This file is the repository's canonical index of sub-protocols, logs and their last-updated timestamps. Agents must update this file when adding or modifying sub-protocols or creating new logs.

Last updated: 2025-11-02

## Format
- Each entry: `- YYYY-MM-DD: filename.md — short description — last-updated: YYYY-MM-DD — contact: @username`

## Sub-Protocol Index
- 2025-11-02: master_protocol.md — central master protocol — last-updated: 2025-11-02 — contact: repo-owner
- 2025-11-02: analysis_sub_protocol.md — analysis rules — last-updated: TBD — contact: repo-owner
- 2025-11-02: research_sub_protocol.md — research rules — last-updated: TBD — contact: repo-owner
- 2025-11-02: generation_sub_protocol.md — generation rules (no emojis) — last-updated: TBD — contact: repo-owner
- 2025-11-02: logging_sub_protocol.md — logging standards — last-updated: TBD — contact: repo-owner
- 2025-11-02: tool_identification_sub_protocol.md — tool selection rules — last-updated: TBD — contact: repo-owner

## Log Index (where to find granular logs)
- `Documentation/logs/` — chronological logs for tasks, named `YYYY-MM-DD_task-slug.md`

## How to update
1. Create or update the sub-protocol file under `Documentation/Protocols/`.
2. Add or update the entry in this master_log with date, short description and contact.
3. Commit both files together and reference the change in a PR description.

## Violations & Restarts
- If a protocol violation occurs, add an entry here and create a `Documentation/logs/violation_YYYY-MM-DD.md` with details.

``` 
