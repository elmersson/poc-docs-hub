#!/usr/bin/env python3
"""Generate llms.txt (index) and llms-full.txt (full corpus) from docs/.

Run after aggregate.py, before or after mkdocs build:
    python scripts/generate_llms_txt.py --base-url https://example.github.io/poc-docs-hub
Outputs into docs/ so mkdocs copies them into the built site.
"""
import argparse
from pathlib import Path

def title_of(md: Path) -> str:
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md.stem.replace("-", " ")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="", help="published site base URL")
    args = parser.parse_args()

    hub = Path(__file__).resolve().parent.parent
    docs = hub / "docs"
    pages = sorted(p for p in docs.rglob("*.md") if p.name != "llms-full.md")

    index_lines = [
        "# Demo Shop Engineering Docs",
        "",
        "> Aggregated docs-as-code for the demo-shop system: architecture,",
        "> event catalog, and per-service reference/how-to/ADR pages.",
        "",
        "## Pages",
        "",
    ]
    full_parts = []
    for page in pages:
        rel = page.relative_to(docs).as_posix()
        url = f"{args.base_url}/{rel.removesuffix('.md')}/" if args.base_url else rel
        index_lines.append(f"- [{title_of(page)}]({url})")
        full_parts.append(f"\n\n---\n<!-- source: {rel} -->\n\n" + page.read_text(encoding="utf-8"))

    (docs / "llms.txt").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (docs / "llms-full.txt").write_text("".join(full_parts).strip() + "\n", encoding="utf-8")
    print(f"wrote llms.txt ({len(pages)} pages) and llms-full.txt")

if __name__ == "__main__":
    main()
