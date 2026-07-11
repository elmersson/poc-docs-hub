---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-01
---

# Demo Shop Engineering Docs

One searchable site for everything in the demo-shop system. Service docs are pulled from each repo's `docs/` folder on every publish, so what you read here is what lives next to the code.

## Start here

<div class="grid cards" markdown>

- **[Architecture overview](architecture.md)**

    The system map: how services couple, the order flow, change impact rules.

- **[Service explorer](services.md)**

    Card view of every service: team, tags, docs and GitHub links.

- **[System catalog](catalog.md)**

    Every component with its owner, dependencies, and API consumers. Generated, never stale.

- **[Interactive dependency graph](graph.html)**

    Pan, zoom and drag through the whole system. Click a service to open its docs.

- **[Event catalog](event-catalog.md)**

    Every event, schema version, producers and consumers.

- **[Docs health](health.md)**

    Per-team freshness scorecard and pages past the review SLA.

- **[Docs MCP server](mcp.md)**

    How Claude searches these docs and queries the catalog, and how to connect it.

- **[Onboarding](onboarding.md)**

    New to the team? The day-one path.

- **[Writing docs](docs-guide.md)**

    Where docs live, the Diátaxis structure, ownership rules.

</div>

## Teams and their services

Docs are organized by owning team under `teams/`. Each team page lists its services; each service page shows owne