# generation_sub_protocol.md — Generation Sub-Protocol

Purpose: rules and expectations for generating code, configuration, and textual artifacts in the repository.

Contract (short):
- Inputs: task prompt, required languages, API/contract constraints, target files.
- Outputs: new/modified files, tests (where applicable), a summary of behavior, and an entry in `Documentation/logs/`.

Hard rules:
- Do not include secrets, credentials, or personal data in generated artifacts.
- No emojis or decorative special characters in repository files unless explicitly authorized.
- Prefer small, focused changes with clear commit messages and a test that demonstrates the change.

Coding conventions (high level):
- Follow repository style where it exists (e.g., docstrings, typing); add types and basic input validation for public functions.
- Include minimal unit tests for any new public behavior (pytest or repository testing framework).
- Add a short CHANGELOG/commit note explaining the reason and potential regressions.

Generation checklist:
1. Confirm the relevant sub-protocols (analysis/research) were consulted.
2. Create minimal, well-tested code and include type hints and docstrings.
3. Run quick lint/type checks locally (if available) and include the result in the log.
4. Add a `Documentation/logs/` entry describing files changed and tests added.
