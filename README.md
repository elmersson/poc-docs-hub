# poc-docs-hub

The documentation hub for the demo-shop PoC: one MkDocs Material site aggregating `docs/` from every service repo, plus llms.txt generation and a thin MCP server so Claude can search the corpus.

## Local demo (no GitHub needed)

Clone all poc-* repos side by side, then:

```bash
pip install -r requirements.txt
python scripts/aggregate.py --source ..
python scripts/generate_llms_txt.py
mkdocs serve   # http://localhost:8000
```

## Claude integration

```bash
cd mcp && npm install
claude mcp add demo-shop-docs -- node <absolute-path>/mcp/server.mjs
```

Then ask Claude Code things like "which services consume OrderPlaced and do any ignore fields?" or "is the payment retry window consistent with the reservation TTL?" (spoiler: it is not, that inconsistency is a planted demo hook).

## CI publish

`.github/workflows/publish.yml` checks out all service repos (needs a fine-grained PAT in secret `REPO_READ_TOKEN`), aggregates, builds and deploys to GitHub Pages. Note: Pages on private repos requires a paid GitHub plan; for the stakeholder demo, `mkdocs serve` locally works just as well.

See CODEOWNERS, catalog-info.yaml and CLAUDE.md for ownership and conventions.
