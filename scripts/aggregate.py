#!/usr/bin/env python3
"""Aggregate docs/ from sibling service repos into docs/teams/<team>/<service>/,
injecting an ownership/freshness banner (with edit-at-source link) into each page.

Local:  python scripts/aggregate.py --source .. --github-owner elmersson
CI:     python scripts/aggregate.py --source ./checkout --github-owner OWNER
"""
import argparse
import re
import shutil
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


def load_owner(repo_dir):
    f = repo_dir / "catalog-info.yaml"
    if f.is_file():
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        return (data.get("spec", {}) or {}).get("owner", "unowned")
    return "unowned"

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
    for legacy in ("services", "teams"):
        d = hub / "docs" / legacy
        if d.exists():
            try:
                shutil.rmtree(d)
            except PermissionError:
                print("WARNING: could not clear docs/" + legacy)

    missing = []
    for repo, slug in REPOS.items():
        repo_dir = Path(args.source).resolve() / repo
        src = repo_dir / "docs"
        if not src.is_dir():
            missing.append(repo)
            continue
        team = load_owner(repo_dir)
        target = hub / "docs" / "teams" / team / slug
        shutil.copytree(src, target, dirs_exist_ok=True)
        for page in target.rglob("*.md"):
            inject_meta_banner(page, repo, page.relative_to(target).as_posix(), args.github_owner)
        print("aggregated " + repo + " -> docs/teams/" + team + "/" + slug)


    if missing:
        print("WARNING: missing repos: " + ", ".join(missing))

if __name__ == "__main__":
    main()
