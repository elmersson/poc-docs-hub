---
owner: team-platform
system: demo-shop
last_reviewed: 2026-07-11
type: runbook
criticality: high
last_tested: 2026-07-11
rto: 60m
tags: [runbook, pipeline]
---

# Runbook: docs site build failure

The publish pipeline is red or the site is stale. The site keeps serving the last successful deploy, so this is never customer-facing — but drift checks and MCP freshness degrade until fixed.

## 1. Find the failing stage

Open the [publish workflow](https://github.com/elmersson/poc-docs-hub/actions/workflows/publish.yml) and read the first failed step. The pipeline is strictly ordered, so the first failure is the cause; later failures are noise.

## 2. Common causes, in order of likelihood

| Symptom in log | Cause | Fix |
|---|---|---|
| `mkdocs build --strict` broken-link error | A service repo merged docs with a bad relative link | Fix the link in the *source repo*, not the hub |
| `run_evals.py` below threshold | Search scoring regression or renamed pages | Run evals locally, inspect which golden question fails |
| `unacceptable character #x0000` | Corrupted file (sync tooling writing null bytes) | Truncate at first null byte, recommit |
| `checkout` step 404 on a repo | `REPO_READ_TOKEN` missing the repo in its access list | Edit the fine-grained PAT, add the repo, re-run |
| `Invalid workflow file` | Truncated YAML committed | Restore the workflow from the repo template |

## 3. Reproduce locally

```powershell
.\preview.ps1        # runs the identical pipeline
python -m mkdocs build --strict
python scripts/run_evals.py
```

If it passes locally but fails in CI, the difference is almost always secrets/tokens or a repo missing from the checkout list.

## 4. Rollback

There is no rollback step: GitHub Pages keeps serving the previous deploy until a new one succeeds. Never fix a red build by deleting content from `docs/` in the hub — it is generated and will be overwritten.

## Escalation

Owner: team-platform (#platform on Slack). If the failure is in a service repo's docs, ping that repo's CODEOWNERS instead.
