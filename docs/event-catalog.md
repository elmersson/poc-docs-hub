---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-01
---

# Event catalog

Every asynchronous message in demo-shop, with schema version, producer and consumers. Schemas live in `@demo-shop/contracts` under `src/events/`. Additive-only: breaking changes require a new version and a deprecation window for the old one.

## OrderPlaced (v2, current)

Produced by orders-service after successful order creation.

| Field | Type | Notes |
|---|---|---|
| eventId | string | UUID, idempotency key |
| eventType | 'OrderPlaced' | |
| version | 2 | v1 deprecated 2025-11 (lacked `channel`) |
| orderId | string | |
| customerId | string | |
| items | array of {sku, quantity} | |
| channel | 'web' or 'mobile' | added in v2 |
| occurredAt | string | ISO 8601 |

Consumers: inventory-service (stock decrement; uses `orderId` and `items` only).

## PaymentCaptured (v1, current)

Produced by payments-service on capture, delivered as a webhook to orders-service `/webhooks/payment-events`. Delivery: 3 attempts, exponential backoff, then dead-letter log.

| Field | Type | Notes |
|---|---|---|
| eventId | string | UUID, consumers must dedupe on this |
| eventType | 'PaymentCaptured' | |
| version | 1 | |
| paymentIntentId | string | |
| orderId | string | |
| amountMinor | number | integer minor units, never floats |
| currency | string | ISO 4217 |
| occurredAt | string | ISO 8601 |

Consumers: orders-service (transitions order to `paid`, idempotent by `eventId`).

## Adding or changing an event

Read shared-contracts ADR 0002 first. Then: add the type in contracts, bump the package version, update this catalog in the same change, and notify consuming teams via the PR (CODEOWNERS routes it automatically).
