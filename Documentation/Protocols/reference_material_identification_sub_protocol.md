# reference_material_identification_sub_protocol.md — Reference Material Identification

Purpose: guidance for choosing canonical documentation, SDKs, and reference materials that agents should cite and use.

Rules:
- Prefer official vendor documentation, RFCs, and stable release notes.
- Capture exact URLs and a short excerpt (2–4 lines) to avoid drift; include version identifiers when present.
- When using community content (blogs, Q&A), mark it as secondary and verify against official docs.

Format for references delivered:
- title — URL — version/date — short rationale (1–2 sentences)

Caching and snapshotting:
- If a reference is critical to reproducibility, store a minimal snapshot in `Documentation/references/` (small excerpt and metadata), and log the snapshot in `Documentation/logs/`.
