#!/usr/bin/env python3
"""Retrieval eval harness: runs evals/golden.yaml against keyword search
(same scoring as the MCP server) and, when VOYAGE_API_KEY is set, semantic search.

Metrics: hit@3 (expected page in top 3), MRR, abstain correctness (no results,
or top keyword score below threshold). Exits 1 if keyword hit@3 < 0.7.

Run after building the corpus:  python scripts/run_evals.py
"""
import os
import re
import sys
from pathlib import Path

import yaml

ABSTAIN_MAX_SCORE = 4.0  # IDF-weighted score at/below which results are noise

def keyword_search(docs, query):
    """Mirror of server.mjs keywordSearch scoring (IDF-weighted, whole-word)."""
    import math
    stop = {"the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "is", "are",
            "do", "does", "how", "what", "when", "why", "who", "this", "that", "we", "our", "it"}
    def stem(w):
        for suf in ("ing", "ed", "es", "s"):
            if len(w) > 4 and w.endswith(suf):
                return w[: -len(suf)]
        return w
    terms = [stem(t) for t in re.findall(r"[a-z0-9]+", query.lower()) if t not in stop and len(t) > 2]
    if not terms:
        return []
    pages = []
    for page in docs.rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        rel0 = page.relative_to(docs).as_posix()
        if rel0 in ("analytics.md",):  # generated from queries; indexing it would self-contaminate search
            continue
        tokens = [stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())]
        headings = set(stem(t) for t in re.findall(r"[a-z0-9]+", " ".join(re.findall(r"^#{1,3} .*$", text, re.M)).lower()))
        pages.append((page.relative_to(docs).as_posix(), tokens, headings))
    n_pages = len(pages)
    df = {t: sum(1 for _, tokens, _ in pages if t in tokens) for t in terms}
    need = (len(terms) + 1) // 2
    hits = []
    for rel, tokens, headings in pages:
        matched, score = 0, 0.0
        for t in terms:
            tf = tokens.count(t)
            if tf == 0:
                continue
            matched += 1
            idf = math.log(1 + n_pages / (1 + df[t]))
            score += (1 + math.log(tf)) * idf * (2 if t in headings else 1)
        if matched >= need and score > 0:
            hits.append((score, rel))
    hits.sort(key=lambda x: -x[0])
    return hits[:8]

def main():
    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    golden = yaml.safe_load((hub / "evals" / "golden.yaml").read_text(encoding="utf-8"))["questions"]

    hits3, rr_sum, answer_n = 0, 0.0, 0
    abstain_ok, abstain_n = 0, 0
    failures = []
    for item in golden:
        q, expect = item["q"], item["expect"]
        results = keyword_search(docs, q)
        if expect == "answer":
            answer_n += 1
            pages = [p for _, p in results[:3]]
            all_pages = [p for _, p in results]
            if item["expected_page"] in pages:
                hits3 += 1
                rr_sum += 1.0 / (pages.index(item["expected_page"]) + 1)
            else:
                rank = all_pages.index(item["expected_page"]) + 1 if item["expected_page"] in all_pages else None
                failures.append((q, item["expected_page"], rank, pages[:3]))
        else:
            abstain_n += 1
            top_score = results[0][0] if results else 0
            if top_score <= ABSTAIN_MAX_SCORE:
                abstain_ok += 1
            else:
                failures.append((q, "ABSTAIN", None, [p for _, p in results[:3]]))

    hit_rate = hits3 / answer_n if answer_n else 0
    mrr = rr_sum / answer_n if answer_n else 0
    print("keyword search: hit@3 " + f"{hit_rate:.0%}" + " (" + str(hits3) + "/" + str(answer_n) + "), "
          "MRR " + f"{mrr:.2f}" + ", abstain " + str(abstain_ok) + "/" + str(abstain_n))
    for q, expected, rank, got in failures:
        where = "rank " + str(rank) if rank else "not in top 8"
        print("  MISS: '" + q + "' expected " + expected + " (" + where + "), got " + str(got))

    if os.environ.get("VOYAGE_API_KEY") and (docs / "embeddings.json").exists():
        print("(semantic eval: run manually via the MCP tool; automated version is a pilot TODO)")

    if hit_rate < 0.7:
        print("FAIL: hit@3 below 0.7 threshold")
        sys.exit(1)
    print("PASS")

if __name__ == "__main__":
    main()
