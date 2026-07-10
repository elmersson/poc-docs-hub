#!/usr/bin/env python3
"""Generate the system catalog and per-team landing pages from catalog-info.yaml,
and inject relation panels into each aggregated service page.

Run AFTER aggregate.py:  python scripts/catalog.py --source ..
Produces docs/catalog.md, docs/teams/<team>/index.md, and appends a Relations
section to docs/teams/<team>/<slug>/index.md.
"""
import argparse
from datetime import date
from pathlib import Path

import yaml

REPOS = {
    "poc-shop-frontend": "shop-frontend",
    "poc-orders-service": "orders-service",
    "poc-payments-service": "payments-service",
    "poc-inventory-service": "inventory-service",
    "poc-shared-contracts": "shared-contracts",
}

FM = ["---", "owner: team-platform", "system: demo-shop",
      "last_reviewed: " + date.today().isoformat(), "---", ""]

def load_components(source):
    comps = {}
    for repo, slug in REPOS.items():
        f = source / repo / "catalog-info.yaml"
        if not f.is_file():
            continue
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        spec = data.get("spec", {}) or {}
        comps[data["metadata"]["name"]] = {
            "slug": slug,
            "repo": repo,
            "description": data["metadata"].get("description", ""),
            "type": spec.get("type", ""),
            "owner": spec.get("owner", "unowned"),
            "depends_on": [d.split(":", 1)[1] for d in spec.get("dependsOn", []) or []],
            "provides": spec.get("providesApis", []) or [],
            "consumes": spec.get("consumesApis", []) or [],
        }
    return comps

def path_of(c):
    return "teams/" + c["owner"] + "/" + c["slug"] + "/index.md"

def link_from_root(comps, name):
    if name not in comps:
        return "`" + name + "`"
    return "[" + name + "](" + path_of(comps[name]) + ")"

def link_from_service(comps, name):
    # service pages live at docs/teams/<team>/<slug>/index.md
    if name not in comps:
        return "`" + name + "`"
    c = comps[name]
    return "[" + name + "](../../" + c["owner"] + "/" + c["slug"] + "/index.md)"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="..")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    hub = Path(__file__).resolve().parent.parent
    comps = load_components(source)

    api_providers, api_consumers = {}, {}
    depended_by = {n: [] for n in comps}
    for name, c in comps.items():
        for api in c["provides"]:
            api_providers.setdefault(api, []).append(name)
        for api in c["consumes"]:
            api_consumers.setdefault(api, []).append(name)
        for dep in c["depends_on"]:
            depended_by.setdefault(dep, []).append(name)

    # ---- catalog.md ----
    out = FM + ["# System catalog", "",
        "Generated from each repo's `catalog-info.yaml`. This page, not a wiki, is the source of truth for ownership and coupling.", "",
        "## Components", "",
        "| Component | Type | Team | Depends on | Provides | Consumes |", "|---|---|---|---|---|---|"]
    for name in sorted(comps):
        c = comps[name]
        out.append("| " + link_from_root(comps, name) + " | " + c["type"] + " | "
            + "[" + c["owner"] + "](teams/" + c["owner"] + "/index.md) | "
            + (", ".join(link_from_root(comps, d) for d in c["depends_on"]) or "-") + " | "
            + (", ".join("`" + a + "`" for a in c["provides"]) or "-") + " | "
            + (", ".join("`" + a + "`" for a in c["consumes"]) or "-") + " |")

    out += ["", "## Dependency graph", "", "```mermaid", "graph LR"]
    for name, c in comps.items():
        out.append("  " + name.replace("-", "_") + '["' + name + "<br/><i>" + c["owner"] + '</i>"]')
    for name, c in comps.items():
        for dep in c["depends_on"]:
            if dep in comps:
                out.append("  " + name.replace("-", "_") + " --> " + dep.replace("-", "_"))
    out += ["```", "", "## APIs and their consumers", ""]
    for api in sorted(set(api_providers) | set(api_consumers)):
        provs = ", ".join(link_from_root(comps, p) for p in api_providers.get(api, [])) or "unknown"
        cons = ", ".join(link_from_root(comps, x) for x in api_consumers.get(api, [])) or "none recorded"
        out.append("- `" + api + "`: provided by " + provs + "; consumed by " + cons)
    (hub / "docs" / "catalog.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    # ---- team landing pages ----
    teams = {}
    for name, c in comps.items():
        teams.setdefault(c["owner"], []).append(name)
    for team, members in sorted(teams.items()):
        page = ["---", "owner: " + team, "system: demo-shop",
                "last_reviewed: " + date.today().isoformat(), "---", "",
                "# " + team, "",
                "Services and libraries owned by **" + team + "**.", "",
                "| Component | Type | Description |", "|---|---|---|"]
        for name in sorted(members):
            c = comps[name]
            page.append("| [" + name + "](" + c["slug"] + "/index.md) | " + c["type"] + " | " + c["description"] + " |")
        page += ["", "[System catalog](../../catalog.md) · [Docs health](../../health.md)"]
        d = hub / "docs" / "teams" / team
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.md").write_text("\n".join(page) + "\n", encoding="utf-8")

    # ---- relations panels ----
    injected = 0
    for name, c in comps.items():
        idx = hub / "docs" / "teams" / c["owner"] / c["slug"] / "index.md"
        if not idx.is_file():
            continue
        text = idx.read_text(encoding="utf-8")
        if "## Relations" in text:
            continue
        panel = ["", "## Relations", "",
                 "Owner: **[" + c["owner"] + "](../index.md)** · Type: " + c["type"] + " · Repo: `" + c["repo"] + "`", ""]
        if c["depends_on"]:
            panel.append("- Depends on: " + ", ".join(link_from_service(comps, d) for d in c["depends_on"]))
        if depended_by.get(name):
            panel.append("- Depended on by: " + ", ".join(link_from_service(comps, d) for d in depended_by[name]))
        for api in c["provides"]:
            cons = ", ".join(link_from_service(comps, x) for x in api_consumers.get(api, [])) or "none recorded"
            panel.append("- Provides `" + api + "`, consumed by: " + cons)
        for api in c["consumes"]:
            provs = ", ".join(link_from_service(comps, p) for p in api_providers.get(api, [])) or "unknown"
            panel.append("- Consumes `" + api + "`, provided by: " + provs)
        panel += ["", "[Full system catalog](../../../catalog.md) · [Event catalog](../../../event-catalog.md)"]
        idx.write_text(text.rstrip() + "\n" + "\n".join(panel) + "\n", encoding="utf-8")
        injected += 1

    print("wrote catalog.md, " + str(len(teams)) + " team pages, injected relations into " + str(injected) + " service pages")

if __name__ == "__main__":
    main()
