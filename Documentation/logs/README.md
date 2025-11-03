# Documentation/logs/ README

Purpose: describe logging conventions, examples, and where to place operational logs for agents and humans.

Directory: `Documentation/logs/`

File naming:
- `YYYY-MM-DD_task-slug.md` (lower-case, hyphens, no spaces)
- Violation files: `violation_YYYY-MM-DD.md`

Minimum fields for each log (YAML-like or plain text):
- timestamp: ISO 8601 UTC
- agent: username/agent-id
- task_summary: one-line description
- sub_protocols: list
- files_read: list of files and sizes
- files_changed: list of files
- outcome: PASS | FAIL | ABORTED | NEEDS_AUTH
- notes: free text

Examples:
```
timestamp: 2025-11-02T15:04:05Z
agent: ai-agent-42
task_summary: "update master protocol to remove ADDS references"
sub_protocols: [research_sub_protocol, generation_sub_protocol]
files_read:
  - .github/copilot-instructions.md (180 lines)
files_changed:
  - .github/copilot-instructions.md
outcome: PASS
notes: "All ADDS references removed from repo-level files; external_repos/ADDS2025 left intact"
```

Storage and retention:
- Logs are committed when they are summary-level and non-sensitive.
- Do not commit secrets, raw traces, or PII to the repo. If such logging is necessary, store in a secure external store and add a short summary here.

Maintainers should periodically (annual) audit `Documentation/logs/` for stale or irrelevant entries and archive old logs into `Documentation/logs/archive/` via a maintenance PR.
 
Automation
----------
- This repository includes an automated validation script at `scripts/validate_logs.py` which enforces:
  - per-issue log filename conventions (`<slug>-YYYY-MM-DD.md`),
  - forbidden emojis/pictographs in log & protocol files,
  - and that `Documentation/Protocols/master_log.md` contains references to per-issue logs.
- A GitHub Actions workflow `.github/workflows/validate-logs.yml` runs this check on pull requests and pushes to `main`.

Sample
------
- See `Documentation/logs/sample-plan-2025-11-03.md` for a minimal per-plan issue log example.
