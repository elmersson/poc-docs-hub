#!/usr/bin/env python3
"""Generate the system catalog from catalog-info.yaml files and inject relation
panels into each aggregated service page.

Run AFTER aggregate.py, BEFORE health.py / mkdocs build:
    python scripts/catalog.py --source ..
Produces docs/catalog.md and appends a Relations section to docs/services/<slug>/index.md.
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

def load_components(source: Path) -> dict:
    comps = {}
    for repo, slug in REPOS.items():
        f = source / repo / "catalog-info.yaml"
        if not f.is_file():
            continue
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        spec = data.get("spec", {})
        comps[data["metadata"]["name"]] = {
            "slug": slug,
            "repo": repo,
            "description": data["metadata"].get("description", ""),
            "type": spec.get("type", ""),
            "owner": spec.get("owner", ""),
            "depends_on": [d.split(":", 1)[1] for d in spec.get("dependsOn", [])],
            "provides": spec.get("providesApis", []) or [],
            "consumes": spec.get("consumesApis", []) or [],
        }
    return comps

def link(comps: dict, name: str, from_service_page: bool) -> str:
    if name not in comps:
        return f"`{name}`"
    prefix = "../" if from_service_page else "services/"
    return f"[{name}]({prefix}{comps[name]['slug']}/index.md)"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="..")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    hub = Path(__file__).resolve().parent.parent
    comps = load_components(source)

    api_providers = {}
    api_consumers = {}
    depended_by = {n: [] for n in comps}
    for name, c in comps.items():
        for api in c["provides"]:
            api_providers.setdefault(api, []).append(name)
        for api in c["consumes"]:
            api_consumers.setdefault(api, []).append(name)
        for dep in c["depends_on"]:
            depended_by.setdefault(dep, []).append(name)

    out = [
        "---", "owner: team-platform", "system: demo-shop",
        f"last_reviewed: {date.today().isoformat()}", "---", "",
        "# System catalog", "",
        "Generated from each repo's `catalog-info.yaml`. This page, not a wiki, is the source of truth for ownership and coupling.", "",
        "## Components", "",
        "| Component | Type | Team | Depends on | Provides | Consumes |", "|---|---|---|---|---|---|",
    ]
    for name in sorted(comps):
        c = comps[name]
        out.append(
            f"| {link(comps, name, False)} | {c['type']} | {c['owner']} | "
            f"{', '.join(link(comps, d, False) for d in c['depends_on']) or '-'} | "
            f"{', '.join(f'`{a}`' for a in c['provides']) or '-'} | "
            f"{', '.join(f'`{a}`' for a in c['consumes']) or '-'} |"
        )

    out += ["", "## Dependency graph", "", "```mermaid", "graph LR"]
    for name, c in comps.items():
        out.append(f'  {name.replace("-", "_")}["{name}<br/><i>{c["owner"]}</i>"]')
    for name, c in comps.items():
        for dep in c["depends_on"]:
            if dep in comps:
                out.append(f'  {name.replace("-", "_")} --> {dep.replace("-", "_")}')
    out += ["```", ""]

    out += ["## APIs and their consumers", ""]
    for api in sorted(set(api_providers) | set(api_consumers)):
        provs = ", ".join(link(comps, p, False) for p in api_providers.get(api, [])) or "unknown"
        cons = ", ".join(link(comps, x, False) for x in api_consumers.get(api, [])) or "none recorded"
        out.append(f"- `{api}`: provided by {provs}; consumed by {cons}")

    (hub / "docs" / "catalog.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    injected = 0
    for name, c in comps.items():
        idx = hub / "docs" / "services" / c["slug"] / "index.md"
        if not idx.is_file():
            continue
        text = idx.read_text(encoding="utf-8")
        if "## Relations" in text:
            continue
        panel = ["", "## Relations", "", f"Owner: **{c['owner']}** · Type: {c['type']} · Repo: `{c['repo']}`", ""]
        if c["depends_on"]:
            panel.append("- Depends on: " + ", ".join(link(comps, d, True) for d in c["depends_on"]))
        if depended_by.get(name):
            panel.append("- Depended on by: " + ", ".join(link(comps, d, True) for d in depended_by[name]))
        for api in c["provides"]:
            cons = ", ".join(link(comps, x, True) for x in api_consumers.get(api, [])) or "none recorded"
            panel.append(f"- Provides `{api}`, consumed by: {cons}")
        for api in c["consumes"]:
            provs = ", ".join(link(comps, p, True) for p in api_providers.get(api, [])) or "unknown"
            panel.append(f"- Consumes `{api}`, provided by: {provs}")
        panel.append("")
        panel.append("[Full system catalog](../../catalog.md) · [Event catalog](../../event-catalog.md)")
        idx.write_text(text.rstrip() + "\n" + "\n".join(panel) + "\n", encoding="utf-8")
        injected += 1

    print(f"wrote docs/catalog.md ({len(comps)} components), injected relations into {injected} service pages")

if __name__ == "__main__":
    main()
