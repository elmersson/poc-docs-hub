---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-10
---

# Service explorer

Every component in demo-shop. Use the header search for full-text search across all docs, or browse by [tag](tags.md).

<div class="grid cards" markdown>

- **[inventory-service](teams/team-fulfillment/inventory-service/index.md)** · `service`

    Stock levels and reservations for demo-shop

    Team: [team-fulfillment](teams/team-fulfillment/index.md) · `#api` `#inventory` `#events`

    [:material-file-document: Docs](teams/team-fulfillment/inventory-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-inventory-service)

- **[orders-service](teams/team-checkout/orders-service/index.md)** · `service`

    Order lifecycle - creation, payment coordination, status

    Team: [team-checkout](teams/team-checkout/index.md) · `#api` `#orders` `#events` `#webhooks`

    [:material-file-document: Docs](teams/team-checkout/orders-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-orders-service)

- **[payments-service](teams/team-payments/payments-service/index.md)** · `service`

    Payment intents and capture - dispatches PaymentCaptured webhooks to orders

    Team: [team-payments](teams/team-payments/index.md) · `#api` `#payments` `#webhooks`

    [:material-file-document: Docs](teams/team-payments/payments-service/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-payments-service)

- **[shared-contracts](teams/team-platform/shared-contracts/index.md)** · `library`

    Shared TypeScript API types and event schemas for every demo-shop service

    Team: [team-platform](teams/team-platform/index.md) · `#library` `#types` `#contracts` `#events`

    [:material-file-document: Docs](teams/team-platform/shared-contracts/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-shared-contracts)

- **[shop-frontend](teams/team-frontend/shop-frontend/index.md)** · `website`

    Demo Shop storefront - checkout flow and order status polling

    Team: [team-frontend](teams/team-frontend/index.md) · `#react` `#web` `#checkout`

    [:material-file-document: Docs](teams/team-frontend/shop-frontend/index.md) · [:material-github: GitHub](https://github.com/elmersson/poc-shop-frontend)

</div>
