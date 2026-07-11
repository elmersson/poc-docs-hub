#!/usr/bin/env python3
"""Auto-link mentions of known components/repos in aggregated pages to their
service page on the hub. Run AFTER catalog.py:
    python scripts/crosslink.py --source ..
Skips fenced code blocks, inline code, existing links, headings and self-mentions.
"""
import argparse
import os
import re
from pathlib import Path

import yaml

REPOS = {
    "poc-shop-frontend": "shop-frontend",
    "poc-orders-service": "orders-service",
    "poc-payments-service": "payments-service",
    "poc-inventory-service": "inventory-service",
    "poc-shared-contracts": "shared-contracts",
}

# repos.yaml (hub root) overrides the fallback dict below: one file to edit when onboarding a repo
_repos_file = Path(__file__).resolve().parent.parent / "repos.yaml"
if _repos_file.is_file():
    REPOS = yaml.safe_load(_repos_file.read_text(encoding="utf-8"))["repos"]


def load_targets(source):
    """name/repo -> (owner, slug)"""
    targets = {}
    for repo, slug in REPOS.items():
        f = source / repo / "catalog-info.yaml"
        if not f.is_file():
            continue
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        owner = (data.get("spec", {}) or {}).get("owner", "unowned")
        name = data["metadata"]["name"]
        targets[name] = (owner, slug)
        targets[repo] = (owner, slug)
    return targets

def linkify(page, targets, teams_root):
    text = page.read_text(encoding="utf-8")
    own = {k for k, (o, s) in targets.items() if str(page).replace(os.sep, "/").find("/" + o + "/" + s + "/") != -1}
    names = sorted((k for k in targets if k not in own), key=len, reverse=True)
    if not names:
        return False
    pattern = re.compile(r"(?<![\w\-/`\[])(" + "|".join(re.escape(n) for n in names) + r")(?![\w\-/`\]])")
    out, changed, fenced = [], False, False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        if fenced or stripped.startswith("#") or stripped.startswith("<small>") or "](" in line:
            out.append(line)
            continue
        def repl(m):
            owner, slug = targets[m.group(1)]
            target = teams_root / owner / slug / "index.md"
            rel = os.path.relpath(target, page.parent).replace(os.sep, "/")
            return "[" + m.group(1) + "](" + rel + ")"
        # split on inline code spans, only replace outside them
        parts = re.split(r"(`[^`]*`)", line)
        new_line = "".join(p if p.startswith("`") else pattern.sub(repl, p) for p in parts)
        if new_line != line:
            changed = True
        out.append(new_line)
    if changed:
        page.write_text("".join(out), encoding="utf-8")
    return changed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="..")
    args = parser.parse_args()
    source = Path(args.source).resolve()
    hub = Path(__file__).resolve().parent.parent
    teams_root = hub / "docs" / "teams"
    targets = load_targets(source)
    count = sum(1 for p in teams_root.rglob("*.md") if linkify(p, targets, teams_root))
    print("crosslinked component mentions in " + str(count) + " pages")

if __name__ == "__main__":
    main()
