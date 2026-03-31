param(
    [string]$Version = '1.1.0',
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    throw "Version must be semver without a leading 'v'. Current value: $Version"
}

$skillName = 'comfypet-jmcai-skill'
$payloadRoot = Join-Path $RepoRoot "skills\$skillName"
$distRoot = Join-Path $RepoRoot 'dist'
$distPayloadRoot = Join-Path $distRoot $skillName
$zipPath = Join-Path $distRoot "$skillName-v$Version.zip"
$checksumsPath = Join-Path $distRoot 'checksums.txt'

$requiredPaths = @(
    (Join-Path $payloadRoot 'SKILL.md'),
    (Join-Path $payloadRoot 'agents\openai.yaml'),
    (Join-Path $payloadRoot 'scripts\jmcai_skill.py'),
    (Join-Path $payloadRoot 'references'),
    (Join-Path $payloadRoot 'assets'),
    (Join-Path $payloadRoot 'config.example.json')
)

foreach ($path in $requiredPaths) {
    if (-not (Test-Path $path)) {
        throw "Missing required payload path: $path"
    }
}

if (Test-Path $distRoot) {
    Remove-Item -LiteralPath $distRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $distRoot -Force | Out-Null
Copy-Item -LiteralPath $payloadRoot -Destination $distRoot -Recurse -Force

Get-ChildItem -LiteralPath $distPayloadRoot -Recurse -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq '__pycache__' } |
    Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $distPayloadRoot -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -eq '.pyc' -or $_.Name -eq 'config.json' } |
    Remove-Item -Force

Compress-Archive -Path (Join-Path $distPayloadRoot '*') -DestinationPath $zipPath -Force

Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
try {
    $entryNames = $archive.Entries | ForEach-Object { $_.FullName }
    if ('SKILL.md' -notin $entryNames) {
        throw "Zip archive root does not contain SKILL.md"
    }
} finally {
    $archive.Dispose()
}

$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
Set-Content -LiteralPath $checksumsPath -Value "$hash *$([System.IO.Path]::GetFileName($zipPath))"

Write-Host "Distribution build complete."
Write-Host "Payload directory: $distPayloadRoot"
Write-Host "Zip package: $zipPath"
Write-Host "SHA256: $hash"
