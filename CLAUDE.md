# poc-docs-hub

Aggregated docs site for the demo-shop system. Owner: team-platform. Pulls `docs/` from every poc-* repo, builds one MkDocs Material site, generates llms.txt, and ships a thin MCP server over the corpus.

## Commands
- `pip install -r requirements.txt`
- `python scripts/aggregate.py --source ..` (local: repos cloned side by side)
- `python scripts/generate_llms_txt.py`
- `mkdocs serve` (local preview on :8000) / `mkdocs build`
- MCP server: `cd mcp && npm install && node server.mjs`

## Conventions
- Org-level docs (architecture, event catalog, onboarding, docs guide) live here. Service docs live in their own repos; never edit `docs/services/**` here, it is generated.
- Every page carries front-matter: owner, system, last_reviewed.
- Event catalog must be updated in the same change as any contracts event change.

## Code-to-docs mapping (used by the docs-drift pipeline)
| Code path | Docs to update |
|---|---|
| scripts/*.py | docs/docs-guide.md |
| mcp/** | docs/docs-guide.md |

## Deeper docs
- docs/index.md, docs/architecture.md, docs/event-catalog.md
