#!/usr/bin/env python3
"""Build a semantic-search index over the aggregated docs.

Chunks every page by H2 section, embeds via the Voyage AI API, and writes
docs/embeddings.json for the MCP server's semantic_search tool.

Requires env VOYAGE_API_KEY. Without it, prints a notice and exits 0.
Rate-limit aware: waits and retries on HTTP 429 (Voyage free tier is ~3 req/min),
so a full run on the free tier takes a few minutes. Set EMBED_BATCH to tune.

Run AFTER aggregate.py + catalog.py:
    python scripts/embed.py
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "voyage-3-lite"
BATCH = int(os.environ.get("EMBED_BATCH", "32"))
MAX_CHARS = 6000
MAX_RETRIES = 8
RETRY_WAIT = 25  # seconds, matches ~3 requests/min free tier

def chunk_page(path, rel):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^---\n[\s\S]*?\n---\n", "", text)
    parts = re.split(r"(?m)^(## .+)$", text)
    chunks = []
    intro = parts[0].strip()
    if intro:
        chunks.append({"page": rel, "section": "(intro)", "text": intro[:MAX_CHARS]})
    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].lstrip("# ").strip()
        body = (parts[i] + "\n" + parts[i + 1]).strip()
        if len(body) > 40:
            chunks.append({"page": rel, "section": heading, "text": body[:MAX_CHARS]})
    return chunks

def embed_batch(texts, key):
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(
            "https://api.voyageai.com/v1/embeddings",
            data=json.dumps({"model": MODEL, "input": texts}).encode(),
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            return [d["embedding"] for d in data["data"]]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = RETRY_WAIT * (attempt + 1)
                print("  rate limited (429), waiting " + str(wait) + "s...")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("unreachable")

def main():
    key = os.environ.get("VOYAGE_API_KEY", "")
    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    out_file = docs / "embeddings.json"
    if not key:
        print("VOYAGE_API_KEY not set, skipping semantic index (keyword search still works)")
        return
    chunks = []
    for page in sorted(docs.rglob("*.md")):
        chunks.extend(chunk_page(page, page.relative_to(docs).as_posix()))
    print("embedding " + str(len(chunks)) + " chunks with " + MODEL + " (batch " + str(BATCH) + ")")
    vectors = []
    for i in range(0, len(chunks), BATCH):
        vectors.extend(embed_batch([c["text"] for c in chunks[i:i + BATCH]], key))
        print("  " + str(min(i + BATCH, len(chunks))) + "/" + str(len(chunks)))
    for c, v in zip(chunks, vectors):
        c["vector"] = v
        del c["text"]
    out_file.write_text(json.dumps({"model": MODEL, "chunks": chunks}), encoding="utf-8")
    print("wrote docs/embeddings.json")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("embed.py failed non-fatally: " + str(e))
        sys.exit(0)
