# analysis_sub_protocol.md — Analysis Sub-Protocol

Purpose: provide a clear, repeatable process for deep, line-by-line analysis of repository artifacts, outputs, and model behavior when requested.

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
