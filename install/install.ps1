param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('codex', 'claude', 'openclaw')]
    [string]$Agent,

    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

$skillName = 'comfypet-jmcai-skill'
$legacySkillName = 'jmcai-workflow-skill'
$payloadRoot = Join-Path $RepoRoot "skills\$skillName"

if (-not (Test-Path $payloadRoot)) {
    throw "Skill payload not found: $payloadRoot"
}

function Get-TargetDir {
    param([string]$SelectedAgent)

    switch ($SelectedAgent) {
        'codex' { return Join-Path $HOME ".codex\skills\$skillName" }
        'claude' { return Join-Path $HOME ".claude\skills\$skillName" }
        'openclaw' { return Join-Path $HOME ".openclaw\workspace\skills\$skillName" }
        default { throw "Unsupported agent: $SelectedAgent" }
    }
}

function Resolve-PythonCommand {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return [PSCustomObject]@{
            Executable = 'python'
            Arguments  = @()
        }
    }

    if (Get-Command py -ErrorAction SilentlyContinue) {
        return [PSCustomObject]@{
            Executable = 'py'
            Arguments  = @('-3')
        }
    }

    throw 'Python 3 is required but was not found in PATH.'
}

$targetDir = Get-TargetDir -SelectedAgent $Agent
$targetParent = Split-Path $targetDir -Parent
$legacyDir = Join-Path $targetParent $legacySkillName

New-Item -ItemType Directory -Path $targetParent -Force | Out-Null

if ((Test-Path $legacyDir) -and -not (Test-Path $targetDir)) {
    Move-Item -LiteralPath $legacyDir -Destination $targetDir
    Write-Host "Migrated legacy skill directory to $targetDir"
}

$backupConfig = $null
if (Test-Path (Join-Path $targetDir 'config.json')) {
    $backupConfig = Join-Path ([System.IO.Path]::GetTempPath()) ("$skillName-config-" + [System.Guid]::NewGuid().ToString() + '.json')
    Copy-Item -LiteralPath (Join-Path $targetDir 'config.json') -Destination $backupConfig -Force
}

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Get-ChildItem -LiteralPath $targetDir -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne 'config.json' } |
    Remove-Item -Recurse -Force

Copy-Item -Path (Join-Path $payloadRoot '*') -Destination $targetDir -Recurse -Force

if ($backupConfig) {
    Copy-Item -LiteralPath $backupConfig -Destination (Join-Path $targetDir 'config.json') -Force
    Remove-Item -LiteralPath $backupConfig -Force
} elseif (-not (Test-Path (Join-Path $targetDir 'config.json')) -and (Test-Path (Join-Path $targetDir 'config.example.json'))) {
    Copy-Item -LiteralPath (Join-Path $targetDir 'config.example.json') -Destination (Join-Path $targetDir 'config.json')
}

$pythonCommand = Resolve-PythonCommand
$pythonExe = $pythonCommand.Executable
$pythonArgs = @($pythonCommand.Arguments)
$pythonArgs += @('jmcai_skill.py', '--config', 'config.json', 'doctor')

Push-Location $targetDir
$doctorExitCode = 0
try {
    & $pythonExe @pythonArgs
    $doctorExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($doctorExitCode -ne 0) {
    Write-Warning "Skill payload installed, but doctor reported issues. Open JMCAI desktop app and rerun 'python jmcai_skill.py doctor' in $targetDir."
}

Write-Host "Installed $skillName to $targetDir"
