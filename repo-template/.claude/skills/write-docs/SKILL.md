---
name: write-docs
description: Create or update documentation in this repo's standard format. Use whenever asked to document a feature, endpoint, event, decision, or process, or when asked to "write docs", "add an ADR", "document this", or after implementing something user-facing that changes behavior.
---

# Writing docs in this repo

All docs live in `docs/` and follow this structure. Never create documentation anywhere else, and never skip the front-matter.

## Where the page goes (Diátaxis)

- Task the reader wants to DO ("run locally", "handle a failed payment") → `docs/how-to/<verb-phrase>.md`
- Facts about the API/behavior (endpoints, payloads, limits) → `docs/reference/api.md` (extend it, don't create parallel reference files)
- A decision and its trade-offs → `docs/adr/NNNN-<slug>.md`, next free number
- What the service is / changelog → `docs/index.md`

## Required front-matter on every page

```yaml
---
owner: <team from catalog-info.yaml spec.owner>
system: demo-shop
last_reviewed: <today, YYYY-MM-DD>
---
```

When you edit an existing page meaningfully, bump `last_reviewed` to today.

## Writing rules (docs are read by humans AND AI agents)

- Self-contained H2 sections: no "as mentioned above", no pronouns pointing at other sections.
- Specific headings: "Configure webhook retries", not "Configuration".
- Keep a constraint in the same paragraph as its guidance (e.g. TTLs, limits, retry counts).
- Quote exact error messages in troubleshooting content.
- Simple tables only. No screenshots; write numbered steps instead.
- Match the numbers in code exactly (ports, TTLs, retry counts). If code and existing docs disagree, flag it, don't guess.

## ADR rules

One decision per file. Sections: Status, Context, Decision, Consequences. ADRs are append-only: never edit an accepted ADR, write a new one that supersedes it and link both ways.

## After writing

1. If you changed API behavior docs, check whether `docs/reference/api.md` and the code agree.
2. If you documented an event schema change, note that the docs-hub event catalog (separate repo) also needs updating; mention it in your summary or PR description.
3. Update the code-to-docs mapping table in CLAUDE.md if you added a new docs file that maps to code paths.
4. New docs go in the same PR as the code change they describe whenever possible.
