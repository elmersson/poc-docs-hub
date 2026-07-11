---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
tags: [pipeline, reference]
---

# Pipeline reference

Every build runs the same scripts in the same order, locally (`preview.ps1`) and in CI (`publish.yml`). Each stage reads only files, writes only files, and can be run alone for debugging.

| Order | Script | Reads | Writes |
|---|---|---|---|
| 1 | `aggregate.py` | every repo's `docs/` (+ this repo's `platform-docs/`), `repos.yaml` | `docs/teams/<team>/<slug>/`, ownership banners, per-service `.pages` |
| 2 | `catalog.py` | every `catalog-info.yaml`, `teams.yaml` | `catalog.md`, `catalog.json`, `services.md`, team pages, Relations panels |
| 3 | `crosslink.py` | aggregated pages, `catalog-info.yaml` | in-place: links component mentions to their service page |
| 4 | `embed.py` | aggregated pages | `embeddings.json` (semantic search index; Bedrock Titan by default) |
| 5 | `health.py` | front-matter of all pages | `health.md`, `health.json`, `health-history.jsonl` |
| 6 | `stats.py` | `query-log.jsonl` (MCP usage) | `analytics.md`, `stats-history.jsonl` |
| 7 | `llms.py` | aggregated pages | `llms.txt`, `llms-full.txt` |
| 8 | `mkdocs build --strict` | everything above | `site/` — any broken link fails the build |

Everything these scripts write is gitignored: the repo holds sources and generators, never generated output. If a generated page looks wrong, fix the generator or the source repo, not the page.

## Quality gates

Two gates run on every hub push and must pass:

- **`mkdocs build --strict`** — one broken internal link anywhere in the corpus fails the whole build.
- **`run_evals.py`** — 12 golden questions against the search index; fails below 0.7 hit@3. This catches search regressions before agents (and people) do. It has already paid for itself: it caught a self-contamination bug that had silently degraded search to 60%.

## Supporting scripts

- `mine_gaps.py` — clusters unanswered MCP queries into a docs-gap report (Haiku via Bedrock)
- `export_register.py` — DORA-oriented register of components and runbooks as CSV/JSON
- `run_evals.py --update` — never run blind; add golden questions when you add doc areas
