param(
    [string]$Version = '1.0.0',
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$Changelog = 'Initial public release',
    [switch]$RunDryRun
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    throw "clawhub CLI is not installed. Install it first with 'npm i -g clawhub' or 'pnpm add -g clawhub'."
}

if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    throw "Version must be semver without a leading 'v'. Current value: $Version"
}

$slug = 'comfypet-jmcai-skill'
$displayName = 'JMCAI Comfypet'
$tags = 'latest,comfyui,image,video,jmcai'
$payloadRoot = Join-Path $RepoRoot "skills\$slug"
$skillsRoot = Join-Path $RepoRoot 'skills'

if (-not (Test-Path $payloadRoot)) {
    throw "Skill payload not found: $payloadRoot"
}

$publishCommand = "clawhub skill publish `"$payloadRoot`" --slug `"$slug`" --name `"$displayName`" --version `"$Version`" --tags `"$tags`" --changelog `"$Changelog`""
$dryRunCommand = "clawhub sync --root `"$skillsRoot`" --dry-run --tags `"$tags`" --changelog `"$Changelog`""
$syncCommand = "clawhub sync --root `"$skillsRoot`" --all --tags `"$tags`" --changelog `"$Changelog`" --bump patch"

Write-Host "ClawHub publish template ready."
Write-Host "Slug: $slug"
Write-Host "Name: $displayName"
Write-Host "Version: $Version"
Write-Host "Tags: $tags"
Write-Host ""
Write-Host "Dry-run preview:"
Write-Host $dryRunCommand
Write-Host ""
Write-Host "Publish single skill:"
Write-Host $publishCommand
Write-Host ""
Write-Host "Sync all local skills:"
Write-Host $syncCommand

if ($RunDryRun) {
    Write-Host ""
    Write-Host "Running clawhub dry-run..."
    & clawhub sync --root $skillsRoot --dry-run --tags $tags --changelog $Changelog
}
