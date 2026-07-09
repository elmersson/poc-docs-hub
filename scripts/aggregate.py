#!/usr/bin/env python3
"""Aggregate docs/ from sibling service repos into this site under docs/services/.

Local mode (demo): all poc-* repos cloned next to poc-docs-hub.
    python scripts/aggregate.py --source ..
CI mode: repos checked out into ./checkout/<repo> by the workflow.
    python scripts/aggregate.py --source ./checkout
"""
import argparse
import shutil
from pathlib import Path

REPOS = {
    "poc-shop-frontend": "shop-frontend",
    "poc-orders-service": "orders-service",
    "poc-payments-service": "payments-service",
    "poc-inventory-service": "inventory-service",
    "poc-shared-contracts": "shared-contracts",
}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="..", help="dir containing the repo clones")
    args = parser.parse_args()

    hub = Path(__file__).resolve().parent.parent
    target_root = hub / "docs" / "services"
    if target_root.exists():
        shutil.rmtree(target_root)

    missing = []
    for repo, slug in REPOS.items():
        src = Path(args.source).resolve() / repo / "docs"
        if not src.is_dir():
            missing.append(repo)
            continue
        shutil.copytree(src, target_root / slug)
        print(f"aggregated {repo} -> docs/services/{slug}")

    if missing:
        print(f"WARNING: missing repos (skipped): {', '.join(missing)}")

if __name__ == "__main__":
    main()
