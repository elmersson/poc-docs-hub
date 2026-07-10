#!/usr/bin/env python3
"""Aggregate docs/ from sibling service repos into docs/services/, injecting an
ownership/freshness banner (with edit-at-source link) into each page.

Local:  python scripts/aggregate.py --source .. --github-owner elmersson
CI:     python scripts/aggregate.py --source ./checkout --github-owner OWNER
"""
import argparse
import re
import shutil
from pathlib import Path

REPOS = {
    "poc-shop-frontend": "shop-frontend",
    "poc-orders-service": "orders-service",
    "poc-payments-service": "payments-service",
    "poc-inventory-service": "inventory-service",
    "poc-shared-contracts": "shared-contracts",
}

def inject_meta_banner(md, repo, rel_in_repo, gh_owner):
    text = md.read_text(encoding="utf-8")
    if "<small>Owned by" in text:
        return
    owner = re.search(r"^owner:\s*(\S+)", text, re.M)
    reviewed = re.search(r"^last_reviewed:\s*(\S+)", text, re.M)
    if not owner:
        return
    parts = ["Owned by **" + owner.group(1) + "**"]
    if reviewed:
        parts.append("last reviewed " + reviewed.group(1))
    if gh_owner:
        url = "https://github.com/" + gh_owner + "/" + repo + "/edit/main/docs/" + rel_in_repo
        parts.append("[edit at source](" + url + ")")
    banner = "<small>" + " · ".join(parts) + "</small>\n"
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "\n" + banner)
            break
    md.write_text("".join(lines), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="..")
    parser.add_argument("--github-owner", default="")
    args = parser.parse_args()

    hub = Path(__file__).resolve().parent.parent
    target_root = hub / "docs" / "services"
    if target_root.exists():
        try:
            shutil.rmtree(target_root)
        except PermissionError:
            print("WARNING: could not clear docs/services, overwriting in place")

    missing = []
    for repo, slug in REPOS.items():
        src = Path(args.source).resolve() / repo / "docs"
        if not src.is_dir():
            missing.append(repo)
            continue
        shutil.copytree(src, target_root / slug, dirs_exist_ok=True)
        for page in (target_root / slug).rglob("*.md"):
            inject_meta_banner(page, repo, page.relative_to(target_root / slug).as_posix(), args.github_owner)
        print("aggregated " + repo + " -> docs/services/" + slug)

    if missing:
        print("WARNING: missing repos (skipped): " + ", ".join(missing))

if __name__ == "__main__":
    main()
