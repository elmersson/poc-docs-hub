#!/usr/bin/env node
// Docs MCP server for demo-shop: search (keyword + semantic), fetch pages/sections,
// query the component catalog, and log queries + feedback for analytics.
//
// Stdio:  node server.mjs [docsDir]
// HTTP:   node server.mjs --http [port] [docsDir]   (MCP_TOKEN enables bearer auth)
// Query log: JSONL appended to MCP_LOG_FILE (default <hub>/query-log.jsonl).
// Semantic search requires docs/embeddings.json (scripts/embed.py) + VOYAGE_API_KEY.
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import { readFileSync, readdirSync, statSync, existsSync, appendFileSync } from "node:fs";
import { createServer } from "node:http";
import { join, relative, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const argv = process.argv.slice(2);
const httpMode = argv.includes("--http");
const positional = argv.filter((a) => a !== "--http");
const port = httpMode && /^\d+$/.test(positional[0] ?? "") ? Number(positional.shift()) : 3333;
const docsDir = resolve(positional[0] ?? join(dirname(fileURLToPath(import.meta.url)), "..", "docs"));
const logFile = process.env.MCP_LOG_FILE ?? join(docsDir, "..", "query-log.jsonl");

function logEvent(event) {
  try {
    appendFileSync(logFile, JSON.stringify({ ts: new Date().toISOString(), ...event }) + "\n");
  } catch { /* logging must never break serving */ }
}

function allPages(dir = docsDir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) allPages(p, out);
    else if (name.endsWith(".md")) out.push(p);
  }
  return out;
}

function frontMatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  const fm = {};
  if (m) for (const line of m[1].split("\n")) {
    const i = line.indexOf(":");
    if (i > 0) fm[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return fm;
}

const loadJson = (name) => {
  const f = join(docsDir, name);
  return existsSync(f) ? JSON.parse(readFileSync(f, "utf-8")) : null;
};

async function embedQuery(text, model) {
  const key = process.env.VOYAGE_API_KEY;
  if (!key) return null;
  const r = await fetch("https://api.voyageai.com/v1/embeddings", {
    method: "POST",
    headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
    body: JSON.stringify({ model, input: [text] }),
  });
  if (!r.ok) throw new Error("Voyage API " + r.status);
  return (await r.json()).data[0].embedding;
}

const cosine = (a, b) => {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
};

export function keywordSearch(query) {
  const stop = new Set(["the","a","an","and","or","of","to","in","for","on","is","are",
    "do","does","how","what","when","why","who","this","that","we","our","it"]);
  const stem = (w) => {
    for (const suf of ["ing", "ed", "es", "s"]) if (w.length > 4 && w.endsWith(suf)) return w.slice(0, -suf.length);
    return w;
  };
  const terms = (query.toLowerCase().match(/[a-z0-9]+/g) || []).filter((t) => !stop.has(t) && t.length > 2).map(stem);
  if (!terms.length) return [];
  const pages = [];
  for (const file of allPages()) {
    const rel0 = relative(docsDir, file).replaceAll("\\", "/");
    if (rel0 === "analytics.md") continue; // generated from queries; would self-contaminate search
    const text = readFileSync(file, "utf-8");
    const tokens = (text.toLowerCase().match(/[a-z0-9]+/g) || []).map(stem);
    const counts = new Map();
    for (const tok of tokens) counts.set(tok, (counts.get(tok) || 0) + 1);
    const headings = new Set((((text.match(/^#{1,3} .*$/gm) || []).join(" ").toLowerCase().match(/[a-z0-9]+/g)) || []).map(stem));
    pages.push({ file, text, counts, headings });
  }
  const nPages = pages.length;
  const df = new Map(terms.map((t) => [t, pages.filter((p) => p.counts.has(t)).length]));
  const need = Math.ceil(terms.length / 2);
  const hits = [];
  for (const p of pages) {
    let matched = 0, score = 0;
    for (const t of terms) {
      const tf = p.counts.get(t) || 0;
      if (!tf) continue;
      matched++;
      const idf = Math.log(1 + nPages / (1 + (df.get(t) || 0)));
      score += (1 + Math.log(tf)) * idf * (p.headings.has(t) ? 2 : 1);
    }
    if (matched >= need && score > 0) {
      const idx = p.text.toLowerCase().indexOf(terms[0]);
      hits.push({
        page: relative(docsDir, p.file).replaceAll("\\", "/"),
        owner: frontMatter(p.text).owner ?? null,
        score: Number(score.toFixed(2)),
        snippet: p.text.slice(Math.max(0, idx - 80), idx + 240).replace(/\n+/g, " "),
      });
    }
  }
  hits.sort((a, b) => b.score - a.score);
  return hits.slice(0, 8);
}

function buildServer() {
  const server = new McpServer({ name: "demo-shop-docs", version: "3.1.0" });

  server.tool(
    "search_docs",
    "Keyword search over all demo-shop documentation. Returns ranked pages with owner, snippet and path. Title/heading matches rank higher. For conceptual questions where exact words may not appear, prefer semantic_search.",
    { query: z.string().describe("search terms, e.g. 'reservation ttl'") },
    async ({ query }) => {
      const hits = keywordSearch(query);
      logEvent({ tool: "search_docs", query, results: hits.length, top: hits[0]?.page ?? null });
      return { content: [{ type: "text", text: hits.length ? JSON.stringify(hits, null, 2) : "No matches." }] };
    },
  );

  server.tool(
    "semantic_search",
    "Semantic (embeddings) search over the docs: finds relevant sections even when the exact words differ. Falls back with guidance if the semantic index is not configured.",
    { query: z.string().describe("natural-language question or topic") },
    async ({ query }) => {
      const index = loadJson("embeddings.json");
      if (!index) return { content: [{ type: "text", text: "Semantic index not built (run scripts/embed.py with VOYAGE_API_KEY). Use search_docs instead." }] };
      let qv;
      try { qv = await embedQuery(query, index.model); }
      catch (e) { return { content: [{ type: "text", text: "Embedding API error: " + e.message + ". Use search_docs instead." }] }; }
      if (!qv) return { content: [{ type: "text", text: "VOYAGE_API_KEY not set on the server. Use search_docs instead." }] };
      const scored = index.chunks
        .map((c) => ({ page: c.page, section: c.section, score: cosine(qv, c.vector) }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 8)
        .map((h) => ({ ...h, score: Number(h.score.toFixed(4)), hint: "fetch with get_page(path='" + h.page + "', section='" + h.section + "')" }));
      logEvent({ tool: "semantic_search", query, results: scored.length, top: scored[0]?.page ?? null, top_score: scored[0]?.score ?? 0 });
      return { content: [{ type: "text", text: JSON.stringify(scored, null, 2) }] };
    },
  );

  server.tool(
    "get_page",
    "Fetch a documentation page by path (from search results). Pass 'section' (an H2 heading) to get only that section and save context.",
    {
      path: z.string().describe("page path relative to docs root"),
      section: z.string().optional().describe("optional H2 heading, e.g. 'Relations'"),
    },
    async ({ path, section }) => {
      const full = resolve(join(docsDir, path));
      if (!full.startsWith(docsDir)) throw new Error("path escapes docs root");
      let text = readFileSync(full, "utf-8");
      if (section && section !== "(intro)") {
        const re = new RegExp("^## +" + section.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\s*$", "mi");
        const m = re.exec(text);
        if (m) {
          const rest = text.slice(m.index + m[0].length);
          const next = rest.search(/^## /m);
          text = m[0] + (next === -1 ? rest : rest.slice(0, next));
        } else {
          text = "Section not found. Available H2 sections:\n" + (text.match(/^## .*$/gm) || []).join("\n");
        }
      }
      logEvent({ tool: "get_page", path, section: section ?? null });
      return { content: [{ type: "text", text }] };
    },
  );

  server.tool(
    "list_components",
    "List every component in the demo-shop catalog with team, type, tags, provided and consumed APIs.",
    {},
    async () => {
      const cat = loadJson("catalog.json");
      if (!cat) return { content: [{ type: "text", text: "catalog.json not generated; run scripts/catalog.py" }] };
      const rows = Object.entries(cat.components).map(([name, c]) => ({
        name, team: c.owner, type: c.type, tags: c.tags, provides: c.provides, consumes: c.consumes,
      }));
      logEvent({ tool: "list_components" });
      return { content: [{ type: "text", text: JSON.stringify(rows, null, 2) }] };
    },
  );

  server.tool(
    "get_component",
    "One component's full catalog record: owner, repo, dependencies both directions, APIs with consumers/providers, docs path. Ideal for impact analysis.",
    { name: z.string().describe("component name, e.g. payments-service") },
    async ({ name }) => {
      const cat = loadJson("catalog.json");
      if (!cat) return { content: [{ type: "text", text: "catalog.json not generated; run scripts/catalog.py" }] };
      const c = cat.components[name];
      if (!c) {
        logEvent({ tool: "get_component", name, found: false });
        return { content: [{ type: "text", text: "Unknown component. Known: " + Object.keys(cat.components).join(", ") }] };
      }
      const result = {
        name, ...c,
        depended_on_by: cat.depended_on_by[name] ?? [],
        provides_detail: Object.fromEntries(c.provides.map((a) => [a, { consumers: cat.api_consumers[a] ?? [] }])),
        consumes_detail: Object.fromEntries(c.consumes.map((a) => [a, { providers: cat.api_providers[a] ?? [] }])),
        docs_path: "teams/" + c.owner + "/" + c.slug + "/index.md",
      };
      logEvent({ tool: "get_component", name, found: true });
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    },
  );

  server.tool(
    "give_feedback",
    "Record whether the docs answered the question. ALWAYS call this at the end of a docs-research task: helpful=true if the docs contained the answer, helpful=false if they were missing, stale or wrong (include what was missing in 'note'). This feedback drives the docs improvement backlog.",
    {
      query: z.string().describe("the original question or topic"),
      helpful: z.boolean().describe("did the docs answer it?"),
      note: z.string().optional().describe("if not helpful: what was missing or wrong"),
    },
    async ({ query, helpful, note }) => {
      logEvent({ tool: "give_feedback", query, helpful, note: note ?? null });
      return { content: [{ type: "text", text: "Feedback recorded. Thank you." }] };
    },
  );

  return server;
}

const isMain = process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain && httpMode) {
  const token = process.env.MCP_TOKEN ?? "";
  const httpServer = createServer(async (req, res) => {
    if (!req.url?.startsWith("/mcp")) { res.writeHead(404); res.end(); return; }
    if (req.url === "/mcp/health") { res.writeHead(200); res.end("ok"); return; }
    if (token && req.headers.authorization !== "Bearer " + token) {
      res.writeHead(401, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "unauthorized" }));
      return;
    }
    let body = "";
    for await (const chunk of req) body += chunk;
    const server = buildServer();
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    res.on("close", () => { transport.close(); server.close(); });
    await server.connect(transport);
    await transport.handleRequest(req, res, body ? JSON.parse(body) : undefined);
  });
  httpServer.listen(port, () => {
    console.log("demo-shop-docs MCP on http://0.0.0.0:" + port + "/mcp" + (token ? " (bearer auth on)" : " (no auth)") + ", log: " + logFile);
  });
} else if (isMain) {
  await buildServer().connect(new StdioServerTransport());
}
