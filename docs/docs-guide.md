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

## Which repos the pipeline aggregates

`repos.yaml` at the hub root is the single source of truth for the repos the platform pulls docs from, mapping each repo to its service slug. Every pipeline script (`scripts/aggregate.py`, `scripts/catalog.py`, `scripts/crosslink.py`) reads it; when the file is absent they fall back to a built-in list. Onboarding a service = add one line to `repos.yaml` (plus that repo's own `catalog-info.yaml`). The `new-service.ps1` scaffold appends that line for you.

## Local preview

Run `.\preview.ps1` from the hub (service repos cloned alongside it) to run the full pipeline — aggregate, catalog, crosslink, health, stats, `llms.txt` — and serve the site on :8000. Pass `-Owner` / `-Source` to override the GitHub owner used for edit-at-source links and the location of the sibling repos.

The pipeline also produces machine-readable indexes the [docs MCP server](mcp.md) reads at query time: `scripts/catalog.py` emits `catalog.json` (the component catalog) and `scripts/embed.py` emits `embeddings.json` (the semantic-search index, built only when `VOYAGE_API_KEY` is set). Both are git-ignored and generated; never hand-edit them. `scripts/stats.py` closes the loop the other way, rendering `docs/analytics.md` from the MCP `query-log.jsonl` (queries per day, tool mix, top queries, zero-result and helpful-feedback rates); like `catalog.md` and `services.md` it is generated, never hand-edited.

Aggregation (`scripts/aggregate.py`) copies each repo's `docs/` into `teams/<team>/<service>/` (grouped by the owning team from `catalog-info.yaml`) and injects an ownership/freshness banner below the top heading of every aggregated page: the page's `owner`, its `last_reviewed` date, and an **edit at source** link back to the page in its home repo. The link is built from `--github-owner`; without that flag the banner still shows owner and review date, but omits the link. Edit those pages at the source, never here. Aggregation also writes a `.pages` file into each service folder so its sidebar follows a logical order (getting-started, how-to, guides, reference, testing, runbooks, adr) rather than alphabetical; the awesome-pages plugin reads it at build time.

## Front-matter (required on every page)

```yaml
---
owner: team-checkout
system: demo-shop
last_reviewed: 2026-07-01
---
```

CI flags pages whose `last_reviewed` is older than 6 months (a year fails the build). Runbooks are held to a tighter SLA — warned at 90 days, failed at 183 — since they serve as audit evidence.

## Writing for humans and agents

The same rules serve both: self-contained H2 sections (no "as mentioned above"), specific headings ("Configure webhook retries", not "Configuration"), constraints in the same paragraph as their guidance, exact error messages in troubleshooting sections, simple tables only, no screenshot-only content.

## Ownership and review

CODEOWNERS routes doc changes to the owning team. Anyone may propose a change to any team's docs; the owner approves. AI-drafted docs PRs (from the drift pipeline) follow the same review path, no exceptions.