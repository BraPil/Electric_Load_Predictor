# tool_and_reference_material_request_sub_protocol.md — Request Sub-Protocol

Purpose: standard template and workflow for requesting new tools, credentials, or reference materials from repository owners or stakeholders.

Request template (minimum fields):
- requester: agent or username
- date: ISO timestamp
- item_type: tool | token | dataset | reference
- name: human-readable name
- purpose: 1–2 sentence justification
- scope: what the tool will access and why
- urgency: high | medium | low
- retention_and_security: where tokens will be stored and retention policy

Approval flow:
1. Create a `Documentation/logs/` entry describing the request using the template.
2. Notify the repository owner (contact in `master_log.md`) and await explicit approval.
3. If approved, secrets must be stored in a proper secret store (not in the repo) and the log updated with the location and scope.
4. Denied requests must include a short reason in the log.

Expected SLAs: respond within 72 hours for non-urgent requests; faster for emergency/local infra needs.
