---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
tags: [how-to, local-dev]
---

# Run the site locally

Prerequisites: Python 3.11+, the service repos cloned as siblings of `poc-docs-hub`.

## The short way

```powershell
cd poc-docs-hub
.\preview.ps1
```

This installs requirements, runs the full pipeline (aggregate → catalog → crosslink → health → stats → llms), and serves the site at `http://127.0.0.1:8000` with live reload.

## Stage by stage

When debugging one stage, run it alone:

```powershell
python scripts/aggregate.py --source .. --github-owner <owner>
python scripts/catalog.py --source .. --github-owner <owner>
python scripts/crosslink.py --source ..
python scripts/health.py
python -m mkdocs serve
```

## Before you push

The same two gates CI enforces:

```powershell
python -m mkdocs build --strict   # zero broken links
python scripts/run_evals.py       # search quality >= 0.7 hit@3
```

## MCP server

```powershell
cd mcp && npm install
claude mcp add demo-shop-docs -- node <absolute-path>/mcp/server.mjs
```

Full tool documentation on the [MCP page](../../../../mcp.md).
