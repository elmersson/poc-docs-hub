#!/usr/bin/env python3
"""Mine the query log for documentation gaps and write a prioritized report.

Takes zero-result searches, low-score semantic hits and unhelpful feedback,
clusters them (via the Anthropic API when ANTHROPIC_API_KEY is set, else by
shared keywords), and writes gaps-report.md with suggested owners from the
catalog. Run weekly:  python scripts/mine_gaps.py
"""
import json
import os
import re
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

LOW_SCORE = 0.5

def bad_interactions(log):
    bad = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = e.get("tool")
        if t in ("search_docs", "semantic_search") and e.get("results", 1) == 0:
            bad.append({"query": e.get("query", ""), "reason": "zero results"})
        elif t == "semantic_search" and e.get("top_score", 1) < LOW_SCORE:
            bad.append({"query": e.get("query", ""), "reason": "low relevance (" + str(e.get("top_score")) + ")"})
        elif t == "give_feedback" and not e.get("helpful"):
            bad.append({"query": e.get("query", ""), "reason": "marked unhelpful: " + (e.get("note") or "no note")})
    return [b for b in bad if b["query"]]

def cluster_bedrock(items):
    import boto3  # lazy; uses standard AWS credentials
    prompt = ("Cluster these documentation queries that our docs failed to answer into topic groups. "
              "For each cluster output a JSON object: {\"topic\": short name, \"suggestion\": one sentence on what doc to write or fix, \"queries\": [...]}. "
              "Return ONLY a JSON array.\n\n" + json.dumps(items, ensure_ascii=False))
    client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "eu-central-1"))
    resp = client.converse(
        modelId=os.environ.get("GAP_MODEL_ID", "eu.anthropic.claude-haiku-4-5-v1:0"),
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 2000},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    m = re.search(r"\[[\s\S]*\]", text)
    return json.loads(m.group(0)) if m else []

def cluster_llm(items, key):
    prompt = ("Cluster these documentation queries that our docs failed to answer into topic groups. "
              "For each cluster output a JSON object: {\"topic\": short name, \"suggestion\": one sentence on what doc to write or fix, \"queries\": [...]}. "
              "Return ONLY a JSON array.\n\n" + json.dumps(items, ensure_ascii=False))
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({"model": "claude-haiku-4-5-20251001", "max_tokens": 2000,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        text = json.loads(r.read())["content"][0]["text"]
    m = re.search(r"\[[\s\S]*\]", text)
    return json.loads(m.group(0)) if m else []

def cluster_naive(items):
    groups = defaultdict(list)
    for b in items:
        words = [w for w in re.findall(r"[a-z]{4,}", b["query"].lower()) if w not in ("what", "does", "with", "have", "this", "that")]
        groups[words[0] if words else "misc"].append(b["query"])
    return [{"topic": k, "suggestion": "Review these queries and add or fix the covering doc.", "queries": v} for k, v in groups.items()]

def main():
    hub = Path(__file__).resolve().parent.parent
    log = hub / "query-log.jsonl"
    if not log.is_file():
        print("no query-log.jsonl yet, nothing to mine")
        return
    bad = bad_interactions(log)
    if not bad:
        print("no gap candidates found in the log")
        return
    provider = os.environ.get("LLM_PROVIDER", "bedrock")
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    try:
        if provider == "bedrock":
            clusters = cluster_bedrock(bad)
        elif key:
            clusters = cluster_llm(bad, key)
        else:
            clusters = cluster_naive(bad)
    except Exception as e:
        print("LLM clustering failed (" + str(e) + "), using naive grouping")
        clusters = cluster_naive(bad)

    owners = {}
    cat = hub / "docs" / "catalog.json"
    if cat.is_file():
        try:
            comps = json.loads(cat.read_text(encoding="utf-8"))["components"]
            for name, c in comps.items():
                owners[name] = c["owner"]
        except (json.JSONDecodeError, KeyError):
            pass  # catalog optional for gap mining

    out = ["# Docs gap report, " + date.today().isoformat(), "",
           "Mined from " + str(len(bad)) + " failed interactions in the query log. "
           "Each cluster is a docs backlog candidate; assign to the owning team and create an issue.", ""]
    for c in clusters:
        out += ["## " + c.get("topic", "?"), "", c.get("suggestion", ""), ""]
        hint = [t + " (owner " + o + ")" for t, o in owners.items() if t.split("-")[0] in c.get("topic", "").lower()]
        if hint:
            out.append("Likely owner: " + ", ".join(hint))
            out.append("")
        out += ["- \"" + q + "\"" for q in c.get("queries", [])]
        out.append("")
    (hub / "gaps-report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote gaps-report.md with " + str(len(clusters)) + " clusters from " + str(len(bad)) + " failed interactions")

if __name__ == "__main__":
    main()
