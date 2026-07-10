# Shared docs MCP server. Build from the repo root AFTER generating the corpus:
#   python scripts/aggregate.py --source ./checkout --github-owner OWNER
#   python scripts/catalog.py --source ./checkout --github-owner OWNER
#   python scripts/crosslink.py --source ./checkout
#   python scripts/embed.py            (optional, needs VOYAGE_API_KEY)
#   docker build -f mcp/Dockerfile -t demo-shop-docs-mcp .
# Run:  docker run -p 3333:3333 -e MCP_TOKEN=... -e VOYAGE_API_KEY=... demo-shop-docs-mcp
FROM node:22-slim
WORKDIR /app
COPY mcp/package.json mcp/
RUN cd mcp && npm install --omit=dev --no-audit --no-fund
COPY mcp/server.mjs mcp/
COPY docs/ docs/
EXPOSE 3333
CMD ["node", "mcp/server.mjs", "--http", "3333", "/app/docs"]
