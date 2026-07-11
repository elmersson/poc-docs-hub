---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
---

# Service explorer

Every component in demo-shop. Use the header search for full-text search across all docs, or browse by [tag](tags.md).

<div class="grid cards" markdown>

- **[docs-hub](teams/team-platform/docs-hub/index.md)** · `documentation`

    The docs platform itself - aggregates every repo's docs, builds this site, runs the drift pipeline and the MCP server

    Team: [team-platform](teams/team-platform/index.md) · `#platform` `#docs` `#mkdocs` `#mcp` `#pipeline`

    [:material-file-document: Docs](teams/team-platform/docs-hub/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-docs-hub) · [:material-chart-line: Live site](https://elmersson.github.io/poc-docs-hub/) · [:material-google-analytics: Publish pipeline](https://github.com/elmersson/poc-docs-hub/actions/workflows/publish.yml)

- **[inventory-service](teams/team-fulfillment/inventory-service/index.md)** · `service`

    Stock levels and reservations for demo-shop

    Team: [team-fulfillment](teams/team-fulfillment/index.md) · `#api` `#inventory` `#events`

    [:material-file-document: Docs](teams/team-fulfillment/inventory-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-inventory-service) · [:material-percent: Code coverage](https://codecov.io/gh/elmersson/poc-inventory-service) · [:material-chart-line: Monitoring](https://grafana.internal.demo-shop/d/inventory-service)

- **[orders-service](teams/team-checkout/orders-service/index.md)** · `service`

    Order lifecycle - creation, payment coordination, status

    Team: [team-checkout](teams/team-checkout/index.md) · `#api` `#orders` `#events` `#webhooks`

    [:material-file-document: Docs](teams/team-checkout/orders-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-orders-service) · [:material-percent: Code coverage](https://codecov.io/gh/elmersson/poc-orders-service) · [:material-chart-line: Monitoring](https://grafana.internal.demo-shop/d/orders-service)

- **[payments-service](teams/team-payments/payments-service/index.md)** · `service`

    Payment intents and capture - dispatches PaymentCaptured webhooks to orders

    Team: [team-payments](teams/team-payments/index.md) · `#api` `#payments` `#webhooks`

    [:material-file-document: Docs](teams/team-payments/payments-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-payments-service) · [:material-percent: Code coverage](https://codecov.io/gh/elmersson/poc-payments-service) · [:material-chart-line: Monitoring](https://grafana.internal.demo-shop/d/payments-service)

- **[shared-contracts](teams/team-platform/shared-contracts/index.md)** · `library`

    Shared TypeScript API types and event schemas for every demo-shop service

    Team: [team-platform](teams/team-platform/index.md) · `#library` `#types` `#contracts` `#events`

    [:material-file-document: Docs](teams/team-platform/shared-contracts/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-shared-contracts) · [:material-percent: Code coverage](https://codecov.io/gh/elmersson/poc-shared-contracts)

- **[shop-frontend](teams/team-frontend/shop-frontend/index.md)** · `website`

    Demo Shop storefront - checkout flow and order status polling

    Team: [team-frontend](teams/team-frontend/index.md) · `#react` `#web` `#checkout`

    [:material-file-document: Docs](teams/team-frontend/shop-frontend/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-shop-frontend) · [:material-percent: Code coverage](https://codecov.io/gh/elmersson/poc-shop-frontend) · [:material-chart-line: Monitoring](https://grafana.internal.demo-shop/d/shop-frontend) · [:material-google-analytics: Product analytics](https://posthog.internal.demo-shop/shop-frontend)

</div>
