#!/usr/bin/env python3
"""Export a DORA-style register of information from the catalog and runbooks.

Produces register.json and register.csv: every component with owner, type,
dependencies (including third-party Resources once catalogued), plus every
runbook with criticality, last_tested and RTO. Run after aggregate + catalog:
    python scripts/export_register.py
This does not replace the compliance function's register; it is the engineering
evidence feed for it, generated from the same source of truth as the docs site.
"""
import csv
import json
import re
from datetime import date
from pathlib import Path

def front_matter(text):
    m = re.match(r"^---\n([\s\S]*?)\n---", text)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
    return fm

def main():
    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    cat = json.loads((docs / "catalog.json").read_text(encoding="utf-8"))

    rows = []
    for name, c in sorted(cat["components"].items()):
        rows.append({
            "record_type": "component", "name": name, "owner": c["owner"],
            "component_type": c["type"], "repo": c["repo"],
            "depends_on": ";".join(c["depends_on"]),
            "depended_on_by": ";".join(cat["depended_on_by"].get(name, [])),
            "criticality": "", "last_tested": "", "rto": "", "last_reviewed": "",
        })
    for rb in sorted(docs.rglob("runbooks/*.md")):
        fm = front_matter(rb.read_text(encoding="utf-8"))
        rows.append({
            "record_type": "runbook", "name": rb.stem, "owner": fm.get("owner", ""),
            "component_type": "", "repo": "", "depends_on": "", "depended_on_by": "",
            "criticality": fm.get("criticality", ""), "last_tested": fm.get("last_tested", ""),
            "rto": fm.get("rto", ""), "last_reviewed": fm.get("last_reviewed", ""),
        })

    out = {"generated": date.today().isoformat(), "records": rows}
    (hub / "register.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    with open(hub / "register.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    runbooks = sum(1 for r in rows if r["record_type"] == "runbook")
    print("wrote register.json + register.csv: " + str(len(rows) - runbooks) + " components, " + str(runbooks) + " runbooks")

if __name__ == "__main__":
    main()
