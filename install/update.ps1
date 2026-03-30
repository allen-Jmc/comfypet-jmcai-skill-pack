param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('codex', 'claude', 'openclaw')]
    [string]$Agent,

    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

Push-Location $RepoRoot
try {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git pull --ff-only
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    } else {
        Write-Warning 'git was not found in PATH; skipping git pull and continuing with local files.'
    }
} finally {
    Pop-Location
}

& (Join-Path $PSScriptRoot 'install.ps1') -Agent $Agent -RepoRoot $RepoRoot
exit $LASTEXITCODE
