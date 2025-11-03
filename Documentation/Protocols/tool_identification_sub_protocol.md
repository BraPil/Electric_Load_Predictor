# tool_identification_sub_protocol.md — Tool Identification Sub-Protocol

Purpose: provide rules for selecting, validating, and requesting external tools, MCPs, or services used by agents.

Required metadata for any tool considered:
- name, vendor, version
- purpose and short justification
- official docs URL and license
- network/elevated permissions required (yes/no)
- security review summary (privacy, token scope)

Selection process:
1. Prefer built-in repository tools and well-known OSS tools with permissive licenses.
2. For hosted or third-party tools, verify the privacy policy and data retention practices.
3. If API keys or tokens are needed, follow the `tool_and_reference_material_request_sub_protocol.md` to request them and never commit secrets.

Approval: add the chosen tool to `Documentation/logs/` as a short entry and optionally to `Documentation/Protocols/master_log.md` if it becomes standard.
