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

## Three-fold operational responsibilities (ENFORCED)

The logging protocol has three required responsibilities which must be executed at the start of every prompt/response cycle and recorded in the logs:

1) Master log tracking (indexing):
  - Update `Documentation/Protocols/master_log.md` to ensure it lists every logging document and sub-protocol with a one-line description, date of last update, and contact.
  - When adding a new log file (for a new issue or process), append an index line to `master_log.md` in the format used by the file.

2) Two-layer documentation updates per prompt cycle:
  - Every high-level task MUST update two documents per prompt cycle:
    a) `Documentation/Protocols/master_log.md` (the index of logs and sub-protocols), and
    b) the current issue/process log located in `Documentation/logs/` (for example `database_connection_issue_2025-11-03.md`).
  - If the current task does not yet have an issue log, create one using the naming and content rules in `Documentation/logs/README.md` and link it in `master_log.md`.

3) Ensure a current issue log exists and meets naming/content rules:
  - If the current process has no issue log, create it before making changes that would otherwise be untracked.
  - Issue log filenames must be lower-case, use hyphens for separators, and avoid special characters and emojis.
  - Every issue log must contain the minimum required fields (timestamp, agent, task_summary, sub_protocols, files_read, files_changed, outcome, notes).

## Minimal automated checks (suggested)

- When running an agent, perform these automated checks at start:
  1. Does `Documentation/Protocols/master_log.md` contain an entry for the current issue? If not, append it.
  2. Does `Documentation/logs/<current-issue>.md` exist and follow naming rules? If not, create a scaffold file with required fields.
  3. Ensure no emojis or decorative characters are used in filenames or the YAML fields of logs.

Additions and maintenance:
- Use `Documentation/logs/README.md` as the canonical template for creating new issue logs. When automation creates a scaffold, it must populate `timestamp`, `agent`, and `task_summary` and leave other fields blank for the operator/agent to fill in.

