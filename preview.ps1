# One-command local preview of the full docs site. Run from poc-docs-hub:
#   .\preview.ps1                (assumes service repos cloned next to this repo)
param([string]$Owner = "elmersson", [string]$Source = "..")
python scripts\aggregate.py --source $Source --github-owner $Owner
python scripts\catalog.py --source $Source --github-owner $Owner
python scripts\crosslink.py --source $Source
python scripts\health.py
python scripts\generate_llms_txt.py
python -m mkdocs serve
