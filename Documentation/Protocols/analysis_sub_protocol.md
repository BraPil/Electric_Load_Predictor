# analysis_sub_protocol.md — Analysis Sub-Protocol

Title: Analysis Sub-Protocol

Purpose
-------
Provide a repeatable, auditable process for performing investigative and analytical work (data exploration, root-cause analysis, experiments, metric analysis) that agents or humans follow when asked to analyze repository data, code, models, or incidents. The sub-protocol defines inputs, outputs, required readings, data shapes, step-by-step procedure, required logs and sample entries, and acceptance criteria.

Contract (inputs/outputs)
- Inputs: analysis question or hypothesis, scope constraints (time budget, tenant-impact flag), links to required artifacts (files, datasets, models).
- Outputs: a short executive summary (one paragraph), a machine-readable analysis report (YAML front-matter + markdown body) stored under `Documentation/analysis/` or `Documentation/logs/`, and precise next-step tasks (task-slug list) appended to `Documentation/Protocols/master_plan.md` when appropriate.

Success criteria
- Reproducible steps for key findings (data queries or code snippets). 
- At least one concrete next-step task with an owner and acceptance criteria, or a clearly-stated ABSTAIN with reasons when analysis is insufficient.

Edge cases
- Insufficient data: produce an ABSTAIN record with evidence and suggested data collection steps.
- Sensitive data discovered: stop analysis and create a secure incident note using `violation_YYYY-MM-DD.md` in `Documentation/logs/` and notify repo owners via the method in `master_protocol.md`.
- Long-running experiments: create an experiment run entry in `Documentation/logs/` and mark the task as `blocked` with estimated completion.

Required readings (anti-sampling)
- Always read `Documentation/Protocols/master_protocol.md` and the relevant sub-protocols listed in it in full before beginning analysis (the Universal Anti-Sampling Directive applies).
- Read any files explicitly referenced in the user's request in full if they are under 10k lines. For files >10k lines, request explicit authorization before reading in full.

Data & report format
- Store analysis outputs as a Markdown file with a YAML front-matter block. Required front-matter fields:
	- id: analysis-slug (lower-case, hyphens)
	- title: short title
	- date: YYYY-MM-DD
	- analyst: GitHub handle or agent id
	- scope: one-line description
	- files_read: list of files read (paths)
	- files_changed: list of files modified (paths) or []
	- outcome: findings | action_items | abstain
	- evidence_refs: list of file paths / query text / commit SHAs used as evidence

Procedure (step-by-step)
1) Clarify scope: restate the analysis question and any constraints in one sentence.
2) Identify evidence: list files, tables, models, and datasets to inspect. For each file, note estimated lines. Respect anti-sampling rules.
3) Create the analysis scaffold file name: `Documentation/analysis/<analysis-slug>-YYYY-MM-DD.md` and pre-populate front-matter with `analyst`, `date`, and `scope`.
4) Record a new per-analysis issue log in `Documentation/logs/` named `<analysis-slug>-YYYY-MM-DD.md` (if a per-analysis issue log is already being used for the current task, link to it instead). Ensure the per-analysis log meets `Documentation/logs/README.md` requirements.
5) Perform the analysis in small steps. After each step, append a short numbered entry to the per-analysis issue log with `timestamp`, `action` (file read, query run, model evaluated), `files_read`, and immediate observation.
6) Collect verifiable evidence: include snippets of queries, model metrics, and serialized output (small) in the analysis file or link to artifacts in an artifacts storage location. Do not commit sensitive raw data.
7) Draft executive summary and action items. If confident in results, propose 1–3 next-step tasks with owners and acceptance criteria and add them to `master_plan.md` (via a PR) and record the PR link in the analysis file and per-analysis log.
8) If uncertain or data insufficient, write ABSTAIN with explicit reasons and suggested data collection steps.

Required logs and meta-actions
- Analysis scaffold file (in `Documentation/analysis/`) with YAML front-matter as defined above.
- Per-analysis issue log in `Documentation/logs/`, updated after each step.
- Update `Documentation/Protocols/master_log.md` to list the analysis file and per-analysis issue log with a one-line description and last-updated timestamp.

Sample analysis front-matter (example)
---
id: model-drift-investigation-01
title: investigate potential model drift after retrain
date: 2025-11-03
analyst: @analyst-handle
scope: Compare model performance on recent 30-day window vs training validation set
files_read:
	- data/processed/features_hourly.csv
	- training/models/production/metrics.json
files_changed: []
outcome: action_items
evidence_refs:
	- commit: abcdef123456
	- query: "SELECT count(*) FROM features_hourly WHERE date >= '2025-10-01'"
---

Acceptance and handoff
- Create a PR for any `master_plan.md` modifications and include links to the analysis and per-analysis logs. Assign a reviewer.
- Mark the analysis file with `outcome: done` when action items are either scheduled or executed and the per-analysis log contains final verification steps.

Automation and checks
- The repository includes an automated check (`scripts/validate_logs.py`) that enforces naming conventions and that `Documentation/Protocols/master_log.md` references created logs; run it locally before opening PRs.


Contract (short):
- Inputs: list of files or outputs to analyze, task context, expected questions.
- Outputs: a numbered analysis report (observations, evidence lines, code pointers), a short summary with action items, and an entry to `Documentation/logs/` describing the analysis run.
- Error modes: missing files, truncated reads, >10k lines (trigger anti-sampling), permission errors.

Rules and expectations:
- Read each target file in full before drawing conclusions (Universal Anti-Sampling Directive).
- Quote exact lines when citing evidence; include file path and line numbers.
- When analyzing code, include probable failure modes and a minimal test or repro snippet.
- Produce a short, non-opinionated summary (3–5 bullets) followed by a detailed section organized by file.

Checklist for an analysis run:
1. Confirm the Prime Directive and log the analysis in `Documentation/logs/`.
2. Identify all target files and verify sizes; request authorization if any >10,000 lines.
3. Read each file fully and capture relevant snippets with line numbers.
4. Produce the summary + detailed report and add a recommended next action.
5. Update `Documentation/Protocols/master_log.md` if a new sub-protocol is created or modified.

Edge cases to call out:
- Generated files with nondeterministic order (sort before diffing)
- Binary or compressed artifacts (note and skip; request an alternate format)
- Large tables/CSV >10k lines (request sampling authorization or extraction of a schema + representative rows)

Example log entry (short):
```
- 2025-11-02: analysis_rapid_model_debug.md — full analysis of training logs and model.pkl — last-updated: 2025-11-02 — contact: agent
```
