# Onboard a repo to the docs platform (about 10 minutes)

Copy this template's contents into your repo and fill in the placeholders. A dev should only ever need to do this once per repo.

## The fast path (one command)

From the platform root: `.\new-service.ps1 -Repo <repo> -Name <service> -Team <team> -Port <port>` copies this template, fills the placeholders, and registers the repo in the hub's `repos.yaml`. Then only steps 2-4 below remain (links, secrets, push).

## Steps (manual path)

1. Copy these into your repo root:
   - `.github/workflows/docs-drift.yml` (as is, no edits)
   - `.github/workflows/freshness-check.yml` (as is)
   - `.claude/skills/write-docs/SKILL.md` (as is)
   - `catalog-info.yaml`, `CLAUDE.md`, `AGENTS.md`, `CODEOWNERS`, `mkdocs.yml`, `docs/` (fill in placeholders marked `<LIKE-THIS>`)
2. Fill the placeholders: service name, owning team, port, what it calls and what calls it, the code-to-docs mapping table in CLAUDE.md, and the metadata.links (code coverage, monitoring dashboard, product analytics) so they render on your service page and in the MCP catalog. If your team is new, also add it to teams.yaml in the docs hub (Slack channel + CODEOWNERS handle).
3. Write `docs/index.md` (one paragraph) and `docs/reference/api.md` (your endpoints). Skip how-to pages for now; add them when someone asks a question twice.
4. Repo settings: add secret `ANTHROPIC_API_KEY`; add `REPO_DISPATCH_TOKEN` (fine-grained PAT with contents:read+write on the docs hub) if your repo emits shared events; Settings → Actions → General → allow Actions to create pull requests. Install the Claude GitHub App on the repo.
5. Add your repo to `repos.yaml` in the docs hub (one line) so your docs appear on the site. The scaffolding script does this for you.

## What you get

- Your docs render on the central docs site, searchable, with your team as owner.
- Every merged PR is checked for doc drift; Claude opens a docs PR when your docs went stale.
- Monthly freshness check warns on pages past the review SLA.
- Claude Code in your repo knows the docs format: just say "document this" and the write-docs skill produces pages in the right place and format.

## Day-to-day for devs (the actual effort)

Write code. If you changed behavior, tell Claude Code "document this change" (or just let the drift pipeline catch it after merge and review its PR). Bump `last_reviewed` when you touch a doc. That's it.
