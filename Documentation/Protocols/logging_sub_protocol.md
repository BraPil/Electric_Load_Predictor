# logging_sub_protocol.md — Logging Sub-Protocol

Purpose: define log file locations, naming, required fields, and retention for human and agent activity logs.

Location and naming:
- All operational logs live under `Documentation/logs/`.
- File naming convention: `YYYY-MM-DD_task-slug.md` (use lower-case, hyphens, no spaces).

Required fields for every log entry (minimum):
- timestamp: ISO 8601 format
- agent: agent id or username performing the task
- task_summary: one-line summary of intent
- sub_protocols: list of sub-protocols used
- files_read: list of file paths read (include sizes and line ranges when relevant)
- files_changed: list of files modified (if any)
- outcome: PASS | FAIL | ABORTED | NEEDS_AUTH
- notes: short free-text field for observations, errors, or required follow-up

Example log (minimal):
```
timestamp: 2025-11-02T15:04:05Z
agent: ai-agent-42
task_summary: update master protocol to remove ADDS references
sub_protocols: [research_sub_protocol, generation_sub_protocol]
files_read:
  - Documentation/Ideation/Electrical_Load_Predictor_Idea.md (312 lines)
files_changed:
  - .github/copilot-instructions.md
outcome: PASS
notes: all ADDS wording removed from repo-level instructions; external_repos/ADDS2025 left untouched
```

Retention and housekeeping:
- Logs are version-controlled. Keep high-level logs in repo; large or sensitive logs (raw traces, credentials) must not be committed.
- Rotate or archive logs older than 2 years via a maintenance PR.

Violation files:
- If a protocol violation occurs, create `Documentation/logs/violation_YYYY-MM-DD.md` containing a detailed timeline and remediation steps.
