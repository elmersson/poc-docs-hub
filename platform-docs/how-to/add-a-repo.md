---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
tags: [onboarding, how-to]
---

# Add a repo to the docs platform

Budget 10 minutes. One command does most of it; you fill in what only you know.

## 1. Scaffold

From the platform root:

```powershell
.\new-service.ps1 -Repo <repo-name> -Name <service-name> -Team <team> -Port <port>
```

This copies the repo template (workflows, `catalog-info.yaml`, `CLAUDE.md`, docs skeleton, write-docs skill), fills the placeholders, and registers the repo in the hub's `repos.yaml`.

## 2. Fill in what the template cannot know

- `catalog-info.yaml`: what your service calls (`dependsOn`, `consumesApis`), what it provides (`providesApis`), and `metadata.links` (coverage, monitoring, analytics) so they render on your service page.
- `CLAUDE.md`: the code-to-docs mapping table — this is what makes the drift check precise.
- If your team is new: add it to `teams.yaml` in the hub (Slack channel + CODEOWNERS handle).

## 3. Write two pages

`docs/index.md` (one paragraph: what the service does) and `docs/reference/api.md` (your endpoints). Stop there — add how-to pages when someone asks the same question twice, not before.

## 4. Repo settings

Add the `ANTHROPIC_API_KEY` secret (or use the Bedrock workflow variant), allow Actions to create pull requests, and install the Claude GitHub App. If your repo emits shared events, also add `REPO_DISPATCH_TOKEN`.

## What you get

Your docs on this site within minutes of merging, drift-checked on every PR, freshness-checked monthly, and queryable by every AI agent in the company through the MCP server. After setup there is no step 5 — the platform maintains itself.
