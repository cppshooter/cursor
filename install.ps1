[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Platform
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host "Usage: .\install.ps1 <platform>"
    Write-Host "Platforms: claude-code, hermes, openclaw, deepseek-tui"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Platform)) {
    Show-Usage
}

$userHome = [Environment]::GetFolderPath("UserProfile")

switch ($Platform) {
    "claude-code" { $skillsDir = Join-Path $userHome ".claude\skills" }
    "hermes" { $skillsDir = Join-Path $userHome ".hermes\skills" }
    "openclaw" { $skillsDir = Join-Path $userHome ".openclaw\skills" }
    "deepseek-tui" { $skillsDir = Join-Path $userHome ".deepseek\skills" }
    default {
        Write-Host "Unsupported platform: $Platform"
        Show-Usage
    }
}

$dest = Join-Path $skillsDir "awesome-bid"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = [System.IO.Path]::GetPathRoot($dest)

Write-Host "Installing to: $dest"

# Set the variable for the current session and future sessions.
$env:BID_SKILL_HOME = $dest
[Environment]::SetEnvironmentVariable("BID_SKILL_HOME", $dest, "User")
Write-Host "Saved user environment variable BID_SKILL_HOME=$dest"

# Also add the variable to common PowerShell profiles.
$profilePaths = @(
    $PROFILE.CurrentUserCurrentHost,
    $PROFILE.CurrentUserAllHosts
) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique

$escapedDest = $dest.Replace("'", "''")
$profileLine = '$env:BID_SKILL_HOME = ''{0}''' -f $escapedDest

foreach ($profilePath in $profilePaths) {
    $profileDir = Split-Path -Parent $profilePath

    try {
        if (-not [string]::IsNullOrWhiteSpace($profileDir) -and -not (Test-Path $profileDir)) {
            [System.IO.Directory]::CreateDirectory($profileDir) | Out-Null
        }

        if (-not (Test-Path $profilePath)) {
            New-Item -ItemType File -Path $profilePath -Force | Out-Null
        }

        $hasSetting = Select-String -Path $profilePath -Pattern "BID_SKILL_HOME" -Quiet -ErrorAction SilentlyContinue
        if (-not $hasSetting) {
            Add-Content -Path $profilePath -Value $profileLine
            Write-Host "Added BID_SKILL_HOME=$dest to $profilePath"
        }
    }
    catch {
        Write-Warning "Skipped PowerShell profile update: $profilePath. $_"
    }
}

# Safety checks.
if ([string]::IsNullOrWhiteSpace($dest) -or
    $dest.TrimEnd('\') -eq $rootPath.TrimEnd('\') -or
    $dest -notlike "*awesome-bid*") {
    Write-Host "Error: invalid install target ($dest). Aborting."
    exit 1
}

# Recreate the skill directory.
if (Test-Path $dest) {
    Remove-Item -Path $dest -Recurse -Force
}
New-Item -ItemType Directory -Path $dest -Force | Out-Null

# Copy runtime files only.
$copyItems = @(
    "SKILL.md",
    "agents",
    "skills",
    "knowledge",
    "memory",
    "templates",
    "tools"
)

foreach ($item in $copyItems) {
    $source = Join-Path $scriptDir $item
    if (-not (Test-Path $source)) {
        throw "Missing install source file or directory: $source"
    }

    Copy-Item -Path $source -Destination $dest -Recurse -Force
}

Write-Host "Install complete!"
$initPath = Join-Path $dest "tools\init.py"
Write-Host ('Run in your bid project directory: python "{0}" [project-path] [--type <1-4>]' -f $initPath)
