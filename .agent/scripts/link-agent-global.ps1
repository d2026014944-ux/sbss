<#
.SYNOPSIS
    Links the .agent folder to other project directories so Antigravity
    can use the same agents, skills, workflows, and scripts everywhere.

.DESCRIPTION
    Creates an NTFS junction (directory link) in the target project directory
    that points back to the master .agent folder. This means every project
    shares the exact same .agent configuration — edits in one place apply everywhere.

.PARAMETER TargetProject
    Path to the project directory where you want to link .agent.
    Can be a single path or an array of paths.

.PARAMETER MasterAgent
    Path to the master .agent folder. Defaults to the folder where this script lives (../).

.EXAMPLE
    # Link a single project
    .\link-agent-global.ps1 -TargetProject "C:\Users\Daniel Palma\Documents\MeuProjeto"

.EXAMPLE
    # Link multiple projects at once
    .\link-agent-global.ps1 -TargetProject @(
        "C:\Users\Daniel Palma\Documents\projeto-a",
        "C:\Users\Daniel Palma\Documents\projeto-b",
        "D:\Work\client-project"
    )

.EXAMPLE
    # Link ALL subdirectories under a parent folder
    .\link-agent-global.ps1 -TargetProject (Get-ChildItem "C:\Users\Daniel Palma\Documents" -Directory).FullName
#>

param(
    [Parameter(Mandatory = $true)]
    [string[]]$TargetProject,

    [string]$MasterAgent = (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
)

$masterAgentPath = Join-Path $MasterAgent ".agent"

if (-not (Test-Path $masterAgentPath)) {
    # If MasterAgent doesn't contain .agent, try the script's own parent
    $scriptDir = Split-Path -Parent $PSScriptRoot
    $masterAgentPath = $scriptDir
    if (-not (Test-Path (Join-Path $masterAgentPath "ARCHITECTURE.md"))) {
        Write-Error "Master .agent folder not found at '$masterAgentPath'. Please specify -MasterAgent."
        exit 1
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Antigravity .agent Global Linker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Master .agent: $masterAgentPath" -ForegroundColor Green
Write-Host ""

$success = 0
$skipped = 0
$failed  = 0

foreach ($project in $TargetProject) {
    $project = $project.TrimEnd('\', '/')
    $targetAgentPath = Join-Path $project ".agent"

    Write-Host "  Processing: $project" -ForegroundColor White

    # Skip if it's the master project itself
    $resolvedProject = Resolve-Path $project -ErrorAction SilentlyContinue
    $resolvedMaster  = Resolve-Path (Split-Path $masterAgentPath) -ErrorAction SilentlyContinue
    if ($resolvedProject -and $resolvedMaster -and ($resolvedProject.Path -eq $resolvedMaster.Path)) {
        Write-Host "    -> SKIPPED (this is the master project)" -ForegroundColor Yellow
        $skipped++
        continue
    }

    # Check if target directory exists
    if (-not (Test-Path $project)) {
        Write-Host "    -> FAILED: Directory does not exist" -ForegroundColor Red
        $failed++
        continue
    }

    # If .agent already exists at target
    if (Test-Path $targetAgentPath) {
        $item = Get-Item $targetAgentPath -Force

        # Check if it's already a junction pointing to the right place
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            $existingTarget = (Get-Item $targetAgentPath).Target
            if ($existingTarget -eq $masterAgentPath) {
                Write-Host "    -> SKIPPED (junction already exists and points correctly)" -ForegroundColor Yellow
                $skipped++
                continue
            } else {
                Write-Host "    -> Removing existing junction (pointed to: $existingTarget)" -ForegroundColor DarkYellow
                Remove-Item $targetAgentPath -Force
            }
        } else {
            # It's a real folder — back it up
            $backupName = ".agent.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            $backupPath = Join-Path $project $backupName
            Write-Host "    -> Backing up existing .agent to $backupName" -ForegroundColor DarkYellow
            Rename-Item $targetAgentPath $backupPath
        }
    }

    # Create the junction
    try {
        New-Item -ItemType Junction -Path $targetAgentPath -Target $masterAgentPath -ErrorAction Stop | Out-Null
        Write-Host "    -> LINKED successfully" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "    -> FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Results: $success linked | $skipped skipped | $failed failed" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($success -gt 0) {
    Write-Host "All linked projects now share the same .agent configuration." -ForegroundColor Green
    Write-Host "Any changes to the master .agent will be reflected everywhere." -ForegroundColor Green
}
