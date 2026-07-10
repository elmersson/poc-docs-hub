---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-10
---

# System catalog

Generated from each repo's `catalog-info.yaml`. This page, not a wiki, is the source of truth for ownership and coupling.

## Components

| Component | Type | Team | Depends on | Provides | Consumes |
|---|---|---|---|---|---|
| [inventory-service](services/inventory-service/index.md) | service | team-fulfillment | [shared-contracts](services/shared-contracts/index.md) | `inventory-api` | - |
| [orders-service](services/orders-service/index.md) | service | team-checkout | [payments-service](services/payments-service/index.md), [inventory-service](services/inventory-service/index.md), [shared-contracts](services/shared-contracts/index.md) | `orders-api` | `payments-api`, `inventory-api` |
| [payments-service](services/payments-service/index.md) | service | team-payments | [shared-contracts](services/shared-contracts/index.md) | `payments-api` | - |
| [shared-contracts](services/shared-contracts/index.md) | library | team-platform | - | - | - |
| [shop-frontend](services/shop-frontend/index.md) | website | team-frontend | [orders-service](services/orders-service/index.md), [shared-contracts](services/shared-contracts/index.md) | - | `orders-api` |

## Dependency graph

```mermaid
graph LR
  shop_frontend["shop-frontend<br/><i>team-frontend</i>"]
  orders_service["orders-service<br/><i>team-checkout</i>"]
  payments_service["payments-service<br/><i>team-payments</i>"]
  inventory_service["inventory-service<br/><i>team-fulfillment</i>"]
  shared_contracts["shared-contracts<br/><i>team-platform</i>"]
  shop_frontend --> orders_service
  shop_frontend --> shared_contracts
  orders_service --> payments_service
  orders_service --> inventory_service
  orders_service --> shared_contracts
  payments_service --> shared_contracts
  inventory_service --> shared_contracts
```

## APIs and their consumers

- `inventory-api`: provided by [inventory-service](services/inventory-service/index.md); consumed by [orders-service](services/orders-service/index.md)
- `orders-api`: provided by [orders-service](services/orders-service/index.md); consumed by [shop-frontend](services/shop-frontend/index.md)
- `payments-api`: provided by [payments-service](services/payments-service/index.md); consumed by [orders-service](services/orders-service/index.md)
