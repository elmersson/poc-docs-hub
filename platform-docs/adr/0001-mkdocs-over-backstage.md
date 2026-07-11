---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
tags: [adr, platform]
---

# ADR-0001: MkDocs + pipeline scripts instead of Backstage

**Status:** accepted · **Date:** 2026-07

## Context

We need a documentation platform for ~50 developers (doubling within a year) where docs live next to code, ownership is explicit, and AI agents are first-class consumers and producers of docs. Spotify Backstage is the reference implementation of the catalog model, and TechDocs its docs-as-code pipeline.

## Decision

Adopt Backstage's *data model* but not its runtime: `catalog-info.yaml` in every repo (Backstage-compatible, unmodified), docs aggregated by ~600 lines of Python into an MkDocs Material site, and an MCP server over the generated corpus.

## Rationale

- Backstage is a React/Node monolith that typically needs a dedicated team to operate; at our size that cost exceeds the benefit. Our entire pipeline is inspectable in an afternoon.
- The valuable part of Backstage is the convention, not the software. By keeping `catalog-info.yaml` byte-compatible, migrating to real Backstage later is an import, not a rewrite.
- AI integration is our differentiator, and it is easier against plain markdown + JSON than against Backstage's plugin API. The MCP server reads the same files the site is built from, so the site and the AI cannot disagree.

## Consequences

- We own ~600 lines of pipeline code (mitigated: pure file-in/file-out scripts, each testable alone, guarded by evals and strict builds).
- No plugin ecosystem: scorecards, templates and the like are built by hand when needed (so far: health dashboard, service explorer, dependency graph — a few days total).
- Revisit if we exceed ~300 developers or need Backstage-only features (e.g. software templates at scale).
