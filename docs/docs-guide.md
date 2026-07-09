---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-01
---

# Writing docs

Rules for documentation across demo-shop. Short version: docs live next to code, are owned by the team that owns the code, and change in the same PR as the code.

## Where docs live

Each repo has a `docs/` folder following Diátaxis:

- `how-to/`: task-oriented guides ("run locally", "handle a failed payment"). Most valuable, write these first.
- `reference/`: neutral facts, primarily `api.md`. Must match the code exactly.
- `adr/`: architecture decision records. Append-only; supersede, never edit accepted records.
- `index.md`: what the service does, who owns it, changelog.

## Front-matter (required on every page)

```yaml
---
owner: team-checkout
system: demo-shop
last_reviewed: 2026-07-01
---
```

CI flags pages whose `last_reviewed` is older than 6 months.

## Writing for humans and agents

The same rules serve both: self-contained H2 sections (no "as mentioned above"), specific headings ("Configure webhook retries", not "Configuration"), constraints in the same paragraph as their guidance, exact error messages in troubleshooting sections, simple tables only, no screenshot-only content.

## Ownership and review

CODEOWNERS routes doc changes to the owning team. Anyone may propose a change to any team's docs; the owner approves. AI-drafted docs PRs (from the drift pipeline) follow the same review path, no exceptions.
