#!/usr/bin/env node
// Thin MCP server over the aggregated docs corpus. Two tools: search_docs, get_page.
// Usage: node mcp/server.mjs [docsDir]   (defaults to ../docs relative to this file)
// Register in Claude Code: claude mcp add demo-shop-docs -- node <abs-path>/mcp/server.mjs
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const docsDir = process.argv[2] ?? join(dirname(fileURLToPath(import.meta.url)), "..", "docs");

function allPages(dir = docsDir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) allPages(p, out);
    else if (name.endsWith(".md")) out.push(p);
  }
  return out;
}

const server = new McpServer({ name: "demo-shop-docs", version: "1.0.0" });

server.tool(
  "search_docs",
  "Full-text search over the demo-shop documentation. Returns matching pages with snippets.",
  { query: z.string().describe("search terms") },
  async ({ query }) => {
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    const hits = [];
    for (const file of allPages()) {
      const text = readFileSync(file, "utf-8");
      const lower = text.toLowerCase();
      const score = terms.reduce((s, t) => s + (lower.split(t).length - 1), 0);
      if (score > 0) {
        const idx = lower.indexOf(terms[0]);
        const snippet = text.slice(Math.max(0, idx - 80), idx + 240).replace(/\n+/g, " ");
        hits.push({ page: relative(docsDir, file).replaceAll("\\", "/"), score, snippet });
      }
    }
    hits.sort((a, b) => b.score - a.score);
    const top = hits.slice(0, 8);
    return { content: [{ type: "text", text: top.length ? JSON.stringify(top, null, 2) : "No matches." }] };
  },
);

server.tool(
  "get_page",
  "Fetch the full markdown of a documentation page by its path (as returned by search_docs).",
  { path: z.string().describe("page path relative to docs root, e.g. services/orders-service/reference/api.md") },
  async ({ path }) => {
    const full = join(docsDir, path);
    if (!full.startsWith(docsDir)) throw new Error("path escapes docs root");
    return { content: [{ type: "text", text: readFileSync(full, "utf-8") }] };
  },
);

await server.connect(new StdioServerTransport());
