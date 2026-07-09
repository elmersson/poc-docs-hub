---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-01
---

# Onboarding

Day-one path for a new engineer on any demo-shop team.

## Get oriented

1. Read the [architecture overview](architecture.md). Ten minutes, covers the whole system.
2. Open your team's repo and read its `docs/index.md`, then `CLAUDE.md`. The CLAUDE.md is short on purpose: commands, conventions, gotchas.
3. Skim the ADRs in your repo's `docs/adr/`. They explain why things are the way they are.

## Set up your tools

1. Clone your team's repo plus `poc-shared-contracts` (everything imports it).
2. `npm install`, `npm run dev`. Each service's `docs/how-to/run-locally.md` has the exact steps and known error messages.
3. Claude Code picks up `CLAUDE.md` automatically. Ask it "what does this service do and what depends on it?" as a smoke test; it should answer from the docs and `catalog-info.yaml`.

## Your first change

Make a small PR that touches code and docs together. If your change alters behavior documented under `docs/`, update the page in the same PR. If you forget, the docs-drift pipeline will open a follow-up PR and gently embarrass you.
