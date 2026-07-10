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

- **[System catalog](catalog.md)**

    Every component with its owner, dependencies, and API consumers. Generated, never stale.

- **[Event catalog](event-catalog.md)**

    Every event, schema version, producers and consumers.

- **[Docs health](health.md)**

    Per-team freshness scorecard and pages past the review SLA.

- **[Onboarding](onboarding.md)**

    New to the team? The day-one path.

- **[Writing docs](docs-guide.md)**

    Where docs live, the Diátaxis structure, ownership rules.

</div>

## Services

Aggregated from each repo under `services/`. Each page shows its owning team and last review date in the front-matter.

| Service | Team | Repo |
|---|---|---|
| shop-frontend | team-frontend | poc-shop-frontend |
| orders-service | team-checkout | poc-orders-service |
| payments-service | team-payments | poc-payments-service |
| inventory-service | team-fulfillment | poc-inventory-service |
| shared-contracts | team-platform | poc-shared-contracts |

## How this site stays fresh

Docs live in each service repo and change in the same PR as the code. A merge to any repo triggers a rebuild here. A Claude-powered pipeline reviews every merged PR and opens a docs-update PR when the code drifted from the docs. Humans approve everything.
