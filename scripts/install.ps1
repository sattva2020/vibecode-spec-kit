<#!
.SYNOPSIS
    Installs the VS Code Memory Bank assets into a target project.

.DESCRIPTION
    Copies chat modes, isolation rules, templates, and automation scripts
    into an existing VS Code project directory. Also bootstraps the
    `.vscode/memory-bank` working tree using shipped templates.

.PARAMETER TargetPath
    Destination project directory. Defaults to the current working directory.

.PARAMETER DryRun
    Shows the operations that would be performed without modifying the file system.

.PARAMETER Force
    Overwrites existing files in the destination directories.

.EXAMPLE
    pwsh scripts/install.ps1 -TargetPath ../my-project

.EXAMPLE
    pwsh scripts/install.ps1 -TargetPath C:\Projects\demo -Force

.NOTES
    Run this script from the repository root (where the `scripts` folder lives).
#>
param(
    [Parameter(Position=0)]
    [string]$TargetPath = (Get-Location).Path,

    [switch]$DryRun,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Skip {
    param([string]$Message)
    Write-Host "[SKIP] $Message" -ForegroundColor Yellow
}

function Write-Action {
    param([string]$Message)
    Write-Host "[EXEC] $Message" -ForegroundColor Green
}

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot   = Split-Path -Parent $ScriptRoot
if (-not (Test-Path $TargetPath)) {
    if ($DryRun) {
        Write-Action "Would create target directory $TargetPath"
    } else {
        New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    }
}

if ($DryRun) {
    $TargetPath = [System.IO.Path]::GetFullPath($TargetPath)
} else {
    $TargetPath = Resolve-Path -LiteralPath $TargetPath | Select-Object -ExpandProperty Path
}

if (-not (Test-Path $RepoRoot)) {
    throw "Unable to resolve repository root from script location."
}

Write-Info "Repository root: $RepoRoot"
Write-Info "Target project:  $TargetPath"
if ($DryRun) { Write-Info "Dry-run mode enabled" }
if ($Force)  { Write-Info "Force overwrite enabled" }

$copies = @(
    @{ Name = 'Chat modes'; Source = '.github/chatmodes'; Destination = '.github/chatmodes' },
    @{ Name = 'Isolation rules'; Source = '.vscode/rules'; Destination = '.vscode/rules' },
    @{ Name = 'Templates'; Source = '.vscode/templates'; Destination = '.vscode/templates' },
    @{ Name = 'Automation scripts'; Source = '.vscode/memory-bank/scripts'; Destination = '.vscode/memory-bank/scripts' }
)

function Copy-Tree {
    param(
        [string]$SourceRelative,
        [string]$DestinationRelative
    )

    $sourcePath = Join-Path $RepoRoot $SourceRelative
    $destPath   = Join-Path $TargetPath $DestinationRelative

    if (-not (Test-Path $sourcePath)) {
        throw "Source path not found: $sourcePath"
    }

    if ($DryRun) {
        Write-Action "Would copy $SourceRelative -> $DestinationRelative"
        return
    }

    if (Test-Path $destPath) {
        if ($Force) {
            Remove-Item $destPath -Recurse -Force
        } else {
            Write-Skip "$DestinationRelative already exists (use -Force to overwrite)"
            return
        }
    }

    New-Item -ItemType Directory -Path (Split-Path $destPath) -Force | Out-Null
    Copy-Item $sourcePath -Destination $destPath -Recurse -Force
    Write-Action "Copied $SourceRelative -> $DestinationRelative"
}

foreach ($entry in $copies) {
    Copy-Tree -SourceRelative $entry.Source -DestinationRelative $entry.Destination
}

# Ensure working directories exist
$workingDirs = @(
    '.vscode/memory-bank',
    '.vscode/memory-bank/archive',
    '.vscode/memory-bank/auto',
    '.vscode/memory-bank/creative',
    '.vscode/memory-bank/plan',
    '.vscode/memory-bank/reflection',
    '.vscode/memory-bank/tests',
    '.vscode/memory-bank/van'
)

foreach ($dir in $workingDirs) {
    $path = Join-Path $TargetPath $dir
    if ($DryRun) {
        Write-Action "Would create directory $dir"
        continue
    }
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Action "Created directory $dir"
    }
}

# Seed core markdown files from templates
$templates = @('activeContext.md', 'progress.md', 'projectbrief.md', 'tasks.md')
foreach ($template in $templates) {
    $source = Join-Path $RepoRoot ".vscode/templates/memory_bank/$template"
    $dest   = Join-Path $TargetPath ".vscode/memory-bank/$template"

    if (-not (Test-Path $source)) {
        throw "Template not found: $source"
    }

    if ($DryRun) {
        Write-Action "Would seed $template"
        continue
    }

    if (-not (Test-Path $dest) -or $Force) {
        Copy-Item $source $dest -Force
        Write-Action "Seeded $template"
    } else {
        Write-Skip "$template already exists (use -Force to overwrite)"
    }
}

if (-not $DryRun) {
    Write-Info "Memory Bank assets installed successfully."
    Write-Info "Next steps: restart VS Code and trigger VAN mode."
}
