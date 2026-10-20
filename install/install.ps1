param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('codex', 'claude', 'openclaw', 'antigravity', 'gemini')]
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
        'antigravity' { return Join-Path $HOME ".gemini\config\skills\$skillName" }
        'gemini' { return Join-Path $HOME ".gemini\config\skills\$skillName" }
        default { throw "Unsupported agent: $SelectedAgent" }
    }
}

function Resolve-PythonCommand {
    # 优先检测并使用 uv 管理与执行环境
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        return [PSCustomObject]@{
            Executable = 'uv'
            Arguments  = @('run', 'python')
        }
    }

    # 其次检测标准 python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return [PSCustomObject]@{
            Executable = 'python'
            Arguments  = @()
        }
    }

    # 兼容 Windows py 启动器
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
$normalizeArgs = @($pythonCommand.Arguments)
# 确保在任何 Python 环境（包括嵌入式 Python）下都能正确加载当前目录的模块
$normalizeArgs += @('-c', "import os, sys; sys.path.insert(0, os.getcwd()); import jmcai_skill; jmcai_skill.write_normalized_config_file('config.json')")
$doctorArgs = @($pythonCommand.Arguments)
$doctorArgs += @('jmcai_skill.py', '--config', 'config.json', 'doctor')

Push-Location $targetDir
$doctorExitCode = 0
try {
    & $pythonExe @normalizeArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to normalize config.json in $targetDir"
    }

    & $pythonExe @doctorArgs
    $doctorExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

if ($doctorExitCode -ne 0) {
    Write-Warning "Skill payload installed, but doctor reported issues."
    Write-Host "--------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "[HINT] This skill requires the JMCAI Desktop App to be running." -ForegroundColor Cyan
    Write-Host "Download it here: https://github.com/allen-Jmc/comfypet-jmcai-Dist" -ForegroundColor Cyan
    Write-Host "Please start the app and rerun 'python jmcai_skill.py doctor' in $targetDir." -ForegroundColor Cyan
    Write-Host "--------------------------------------------------------" -ForegroundColor Yellow
}

Write-Host "Installed $skillName to $targetDir"
