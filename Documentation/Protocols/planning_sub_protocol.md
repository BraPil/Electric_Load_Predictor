Title: Planning Sub-Protocol

Purpose
-------
Provide a short, repeatable process that agents and humans must follow to create, consult, and modify the repository Master Plan (`Documentation/Protocols/master_plan.md`). The planning sub-protocol enforces small-task decomposition, iterative progress, and logging so that the Prime Directive is achieved with observable steps.

When to run
-----------
- At the start of a new feature/phase.
- When the Prime Directive or scope changes.
- When the current plan stalls (no progress for >3 working days).

Contract (2–4 bullets)
- Input: a high-level goal (problem statement) and any required constraints (time, infra, tenant safety).
- Output: an updated `master_plan.md` with a prioritized list of atomic tasks (each task name, owner, estimate, acceptance criteria) and links to any required sub-protocols.
- Success criteria: at least one atomic task marked as "in-progress" or "done" within the next iteration.

Procedure (breakdown loop)
-------------------------
1) Read the Prime Directive and `Documentation/Protocols/master_protocol.md` in full (anti-sampling rules apply).
2) Create or open `Documentation/Protocols/master_plan.md`.
3) Decompose the high-level goal into atomic tasks using the following template for each task:
   - id: unique short-slug (lower-case, hyphens)
   - title: single-sentence title
   - description: 1–2 lines
   - owner: GitHub handle or team
   - estimate: small (<= 8 hours) preferred; if larger, further decompose
   - dependencies: other task ids
   - acceptance_criteria: list of verifiable checks
   - status: todo | in-progress | blocked | done

4) Prioritize tasks (use risk/impact/effort or a simple MoSCoW if uncertain).
5) For the first iteration, pick 1–3 tasks to start (favor shortest path to measurable progress).
6) Create or update a per-plan issue log in `Documentation/logs/` named `<plan-slug>-YYYY-MM-DD.md` with the required fields and link it from `master_log.md`.
7) Start executing the first task(s). On each work cycle (every prompt/response):
   - Update the per-plan issue log with files read/changed, actions taken, and outcome.
   - Update `Documentation/Protocols/master_log.md` to reflect the per-plan issue log and the `master_plan.md` update timestamp.
8) At task completion, mark status=done and add the commit/PR reference to the task.

Governance and review
---------------------
- Every plan must include at least one reviewer who is not the task owner.
- Plans with security/tenant implications require an explicit security reviewer check before merges.

Automation hooks (recommended)
-----------------------------
- Small scripts or CI jobs may be added later to validate that `master_plan.md` uses the atomic-task schema and that every in-progress task has an associated per-plan issue log.

Notes and minimal examples
-------------------------
- Example task entry in `master_plan.md`:

  - id: dataset-ingest-01
    title: ingest UCI power dataset
    description: download, validate and store raw UCI dataset in `data/raw/`
    owner: @repo-owner
    estimate: 6h
    dependencies: []
    acceptance_criteria:
      - raw files exist in `data/raw/` with checksum
      - GE expectations tests pass
    status: todo

Compliance
----------
- All planning actions must obey the repository's anti-sampling and logging protocols. No plan modifications are final until a corresponding per-plan issue log and `master_log.md` update exist.
