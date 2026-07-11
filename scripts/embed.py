#!/usr/bin/env python3
"""Build a semantic-search index over the aggregated docs.

Providers (env EMBED_PROVIDER):
  bedrock  - Amazon Titan Text Embeddings V2 via AWS Bedrock (default for Qred:
             same AWS account, no new vendor, $0.02/M tokens). Uses boto3 with
             standard AWS credentials (env/instance role/OIDC in CI).
  voyage   - Voyage AI (needs VOYAGE_API_KEY; used in the PoC before AWS).

Chunks pages by H2 section, writes docs/embeddings.json for semantic_search.
Skips gracefully (exit 0) when credentials are absent, so pipelines never break.

Run AFTER aggregate.py + catalog.py:
    EMBED_PROVIDER=bedrock python scripts/embed.py
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROVIDER = os.environ.get("EMBED_PROVIDER", "bedrock")
BEDROCK_MODEL = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
BEDROCK_REGION = os.environ.get("AWS_REGION", "eu-central-1")
VOYAGE_MODEL = "voyage-4-lite"
BATCH = int(os.environ.get("EMBED_BATCH", "32"))  # voyage only; titan embeds one text per call
MAX_CHARS = 6000
MAX_RETRIES = 8
RETRY_WAIT = 25

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

def embed_voyage(texts, key):
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(
            "https://api.voyageai.com/v1/embeddings",
            data=json.dumps({"model": VOYAGE_MODEL, "input": texts}).encode(),
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return [d["embedding"] for d in json.loads(r.read())["data"]]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = RETRY_WAIT * (attempt + 1)
                print("  rate limited (429), waiting " + str(wait) + "s...")
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("unreachable")

def embed_all_bedrock(chunks):
    import boto3  # lazy: only needed for this provider
    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    vectors = []
    for i, c in enumerate(chunks):
        body = json.dumps({"inputText": c["text"], "dimensions": 1024, "normalize": True})
        resp = client.invoke_model(modelId=BEDROCK_MODEL, body=body,
                                   contentType="application/json", accept="application/json")
        vectors.append(json.loads(resp["body"].read())["embedding"])
        if (i + 1) % 50 == 0:
            print("  " + str(i + 1) + "/" + str(len(chunks)))
    return vectors

def main():
    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    chunks = []
    for page in sorted(docs.rglob("*.md")):
        chunks.extend(chunk_page(page, page.relative_to(docs).as_posix()))

    if PROVIDER == "voyage":
        key = os.environ.get("VOYAGE_API_KEY", "")
        if not key:
            print("VOYAGE_API_KEY not set, skipping semantic index (keyword search still works)")
            return
        print("embedding " + str(len(chunks)) + " chunks with " + VOYAGE_MODEL)
        vectors = []
        for i in range(0, len(chunks), BATCH):
            vectors.extend(embed_voyage([c["text"] for c in chunks[i:i + BATCH]], key))
            print("  " + str(min(i + BATCH, len(chunks))) + "/" + str(len(chunks)))
        model = VOYAGE_MODEL
    else:
        try:
            print("embedding " + str(len(chunks)) + " chunks with " + BEDROCK_MODEL + " (" + BEDROCK_REGION + ")")
            vectors = embed_all_bedrock(chunks)
        except Exception as e:
            print("Bedrock unavailable (" + str(e) + "), skipping semantic index (keyword search still works)")
            return
        model = BEDROCK_MODEL

    for c, v in zip(chunks, vectors):
        c["vector"] = v
        del c["text"]
    (docs / "embeddings.json").write_text(
        json.dumps({"provider": PROVIDER, "model": model, "region": BEDROCK_REGION, "chunks": chunks}),
        encoding="utf-8")
    print("wrote docs/embeddings.json (" + PROVIDER + "/" + model + ")")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("embed.py failed non-fatally: " + str(e))
        sys.exit(0)
