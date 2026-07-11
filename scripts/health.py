#!/usr/bin/env python3
"""Generate docs/health.md: a docs health dashboard from front-matter across the corpus.

Run AFTER aggregate.py so service docs are present:
    python scripts/health.py
Statuses by last_reviewed age: fresh < 90 days, aging 90-183, stale > 183.
"""
from datetime import date, datetime
from pathlib import Path

FRESH_DAYS, STALE_DAYS = 90, 183

def front_matter(md: Path) -> dict:
    lines = md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:30]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm

def main() -> None:
    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    today = date.today()
    rows, missing = [], []

    for page in sorted(docs.rglob("*.md")):
        rel = page.relative_to(docs).as_posix()
        if rel == "health.md":
            continue
        fm = front_matter(page)
        owner, reviewed = fm.get("owner"), fm.get("last_reviewed")
        if not owner or not reviewed:
            missing.append(rel)
            continue
        try:
            age = (today - datetime.strptime(reviewed, "%Y-%m-%d").date()).days
        except ValueError:
            missing.append(rel)
            continue
        status = "fresh" if age < FRESH_DAYS else ("aging" if age <= STALE_DAYS else "STALE")
        rows.append((owner, rel, reviewed, age, status))

    teams = {}
    for owner, rel, reviewed, age, status in rows:
        teams.setdefault(owner, []).append((rel, reviewed, age, status))

    out = [
        "---", "owner: team-platform", "system: demo-shop",
        f"last_reviewed: {today.isoformat()}", "---", "",
        "# Docs health dashboard", "",
        f"Generated {today.isoformat()}. Freshness by `last_reviewed` front-matter: "
        f"fresh under {FRESH_DAYS} days, aging up to {STALE_DAYS}, stale beyond that.", "",
        "## Summary per team", "",
        "| Team | Pages | Fresh | Aging | Stale |", "|---|---|---|---|---|",
    ]
    for team in sorted(teams):
        pages = teams[team]
        counts = {s: sum(1 for *_, st in pages if st == s) for s in ("fresh", "aging", "STALE")}
        out.append(f"| {team} | {len(pages)} | {counts['fresh']} | {counts['aging']} | {counts['STALE']} |")

    stale = [(o, r, rv, a) for o, r, rv, a, s in rows if s == "STALE"]
    out += ["", "## Pages past the review SLA", ""]
    if stale:
        out += ["| Page | Team | Last reviewed | Days |", "|---|---|---|---|"]
        out += [f"| {r} | {o} | {rv} | {a} |" for o, r, rv, a in sorted(stale, key=lambda x: -x[3])]
    else:
        out.append("None. All pages are within the review SLA.")

    out += ["", "## Pages missing front-matter", ""]
    out += ([f"- {m}" for m in missing] or ["None."])

    # machine-readable snapshot (for the MCP get_docs_health tool) + trend history
    import json
    team_stats = {}
    for team in sorted(teams):
        pages = teams[team]
        team_stats[team] = {
            "pages": len(pages),
            "fresh": sum(1 for *_, st in pages if st == "fresh"),
            "aging": sum(1 for *_, st in pages if st == "aging"),
            "stale": sum(1 for *_, st in pages if st == "STALE"),
        }
    snapshot = {"date": today.isoformat(), "teams": team_stats,
                "totals": {"pages": len(rows), "stale": len(stale), "missing_frontmatter": len(missing)}}
    (docs / "health.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    hist = docs.parent / "health-history.jsonl"
    lines_h = hist.read_text(encoding="utf-8").splitlines() if hist.is_file() else []
    if not lines_h or json.loads(lines_h[-1])["date"] != snapshot["date"]:
        with open(hist, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot) + "\n")
        lines_h.append(json.dumps(snapshot))
    # trend section appended to health.md
    if len(lines_h) > 1:
        trend = ["", "## Trend", "", "| Date | Pages | Stale |", "|---|---|---|"]
        for l in lines_h[-8:]:
            h = json.loads(l)
            trend.append("| " + h["date"] + " | " + str(h["totals"]["pages"]) + " | " + str(h["totals"]["stale"]) + " |")
        out += trend

    (docs / "health.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote docs/health.md: {len(rows)} pages, {len(stale)} stale, {len(missing)} missing front-matter")

if __name__ == "__main__":
    main()
