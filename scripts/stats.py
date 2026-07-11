#!/usr/bin/env python3
"""Render docs/analytics.md from the MCP query log (query-log.jsonl).

Run any time:  python scripts/stats.py [--log path]
Shows queries per day, tool mix, top queries, zero-result rate, feedback ratio.
"""
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=None)
    args = parser.parse_args()
    hub = Path(__file__).resolve().parent.parent
    log = Path(args.log) if args.log else hub / "query-log.jsonl"

    events = []
    if log.is_file():
        for line in log.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    searches = [e for e in events if e.get("tool") in ("search_docs", "semantic_search")]
    feedback = [e for e in events if e.get("tool") == "give_feedback"]
    zero = [e for e in searches if e.get("results", 0) == 0]
    days = Counter(e["ts"][:10] for e in events if "ts" in e)
    tools = Counter(e.get("tool", "?") for e in events)
    top_q = Counter(e.get("query", "").lower().strip() for e in searches if e.get("query"))
    helpful = sum(1 for e in feedback if e.get("helpful"))

    out = ["---", "owner: team-platform", "system: demo-shop",
           "last_reviewed: " + date.today().isoformat(), "---", "",
           "# Docs analytics", "",
           "Generated from the MCP query log (" + str(len(events)) + " events). "
           "This is how we measure whether the docs answer questions, not just whether people ask them.", "",
           "## Health numbers", "",
           "| Metric | Value |", "|---|---|",
           "| Search queries | " + str(len(searches)) + " |",
           "| Zero-result rate | " + (f"{len(zero)/len(searches):.0%}" if searches else "n/a") + " |",
           "| Feedback events | " + str(len(feedback)) + " |",
           "| Helpful rate | " + (f"{helpful/len(feedback):.0%}" if feedback else "n/a") + " |", ""]

    out += ["## Events per day", "", "| Day | Events |", "|---|---|"]
    out += ["| " + d + " | " + str(n) + " |" for d, n in sorted(days.items())[-14:]] or ["| - | - |"]

    out += ["", "## Tool mix", "", "| Tool | Calls |", "|---|---|"]
    out += ["| " + t + " | " + str(n) + " |" for t, n in tools.most_common()]

    out += ["", "## Top queries", ""]
    out += ["- \"" + q + "\" (" + str(n) + "x)" for q, n in top_q.most_common(15)] or ["None yet."]

    out += ["", "## Unhelpful feedback (docs backlog candidates)", ""]
    bad = [e for e in feedback if not e.get("helpful")]
    out += ["- \"" + e.get("query", "?") + "\": " + (e.get("note") or "no note") for e in bad[-20:]] or ["None. Either the docs are great or nobody is giving feedback."]

    # trend history: one row per day
    snap = {"date": date.today().isoformat(), "queries": len(searches),
            "zero_rate": round(len(zero) / len(searches), 2) if searches else None,
            "helpful_rate": round(helpful / len(feedback), 2) if feedback else None}
    hist = hub / "stats-history.jsonl"
    lines_h = hist.read_text(encoding="utf-8").splitlines() if hist.is_file() else []
    if not lines_h or json.loads(lines_h[-1])["date"] != snap["date"]:
        with open(hist, "a", encoding="utf-8") as f:
            f.write(json.dumps(snap) + "\n")
        lines_h.append(json.dumps(snap))
    if len(lines_h) > 1:
        out += ["", "## Trend", "", "| Date | Queries | Zero-result | Helpful |", "|---|---|---|---|"]
        for l in lines_h[-8:]:
            h = json.loads(l)
            out.append("| " + h["date"] + " | " + str(h["queries"]) + " | "
                       + (str(h["zero_rate"]) if h["zero_rate"] is not None else "-") + " | "
                       + (str(h["helpful_rate"]) if h["helpful_rate"] is not None else "-") + " |")

    (hub / "docs" / "analytics.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote docs/analytics.md from " + str(len(events)) + " events")

if __name__ == "__main__":
    main()
