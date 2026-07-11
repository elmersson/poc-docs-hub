---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
---

# Writing docs

Rules for documentation across demo-shop. Short version: docs live next to code, are owned by the team that owns the code, and change in the same PR as the code.

## Where docs live

Each repo has a `docs/` folder following Diátaxis:

- `how-to/`: task-oriented guides ("run locally", "handle a failed payment"). Most valuable, write these first.
- `reference/`: neutral facts, primarily `api.md`. Must match the code exactly.
- `adr/`: architecture decision records. Append-only; supersede, never edit accepted records.
- `index.md`: what the service does, who owns it, changelog.

The hub itself carries generated org-level pages you never hand-edit: `catalog.md` (the system catalog) and `services.md` (the service explorer), both built by `scripts/catalog.py` from each repo's `catalog-info.yaml`. That step also injects each service's `tags` and a **Relations** section into every aggregated service `index.md`, so tags, ownership, and coupling on those pages come from the pipeline, not the source repo. Team landing pages (`teams/<team>/index.md`) are generated the same way; their description and contact line (Slack channel, CODEOWNERS) come from a hub-level `teams.yaml`.

The pipeline also produces machine-readable indexes the [docs MCP server](mcp.md) reads at query time: `scripts/catalog.py` emits `catalog.