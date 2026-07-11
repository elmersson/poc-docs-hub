# Scaffold a new service onto the docs platform in one command. Run from docs-platform-poc:
#   .\new-service.ps1 -Repo poc-shipping-service -Name shipping-service -Team team-fulfillment -Port 4004
param(
    [Parameter(Mandatory)][string]$Repo,
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Team,
    [string]$Port = "4000",
    [string]$Description = "TODO: one-line purpose"
)
$ErrorActionPreference = "Continue"
if (Test-Path $Repo) { Write-Host "ERROR: $Repo already exists" -ForegroundColor Red; exit 1 }

# 1. copy template and fill placeholders
Copy-Item -Recurse repo-template $Repo
Get-ChildItem $Repo -Recurse -File | ForEach-Object {
    $c = Get-Content $_.FullName -Raw
    $c = $c -replace "<SERVICE-NAME>", $Name `
           -replace "<TEAM-NAME>", $Team `
           -replace "<PORT>", $Port `
           -replace "<ONE-LINE PURPOSE>", $Description `
           -replace "<YYYY-MM-DD>", (Get-Date -Format "yyyy-MM-dd")
    Set-Content $_.FullName $c -NoNewline
}

# 2. register in the hub (repos.yaml is the single source of truth)
$slug = $Name
Add-Content poc-docs-hub\repos.yaml "  ${Repo}: $slug"

Write-Host ""
Write-Host "Scaffolded $Repo (team: $Team). Remaining manual steps:" -ForegroundColor Green
Write-Host " 1. Fill remaining <PLACEHOLDERS> (catalog links, CLAUDE.md architecture notes)"
Write-Host " 2. If $Team is new: add it to poc-docs-hub\teams.yaml (Slack + CODEOWNERS)"
Write-Host " 3. git init, push, set ANTHROPIC_API_KEY secret, install Claude GitHub App"
Write-Host " 4. Commit the repos.yaml change in poc-docs-hub"
