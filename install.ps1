# Bid Agent Skill Windows 安装脚本
#
# awesome-bid-skill - AI-assisted bid/tender document writing workflow system
# 技术路线参照 awesome-novel-skill（GPL-3.0）的 Agent Skill 架构

param(
    [Parameter(Position = 0)]
    [string]$Platform
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host "用法: .\install.ps1 <平台>"
    Write-Host "平台: claude-code, hermes, openclaw, deepseek-tui"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Platform)) {
    Show-Usage
}

switch ($Platform) {
    "claude-code" {
        $SkillsDir = Join-Path $HOME ".claude\skills"
    }
    "hermes" {
        $SkillsDir = Join-Path $HOME ".hermes\skills"
    }
    "openclaw" {
        $SkillsDir = Join-Path $HOME ".openclaw\skills"
    }
    "deepseek-tui" {
        $SkillsDir = Join-Path $HOME ".deepseek\skills"
    }
    default {
        Write-Host "不支持的平台: $Platform"
        Show-Usage
    }
}

$Dest = Join-Path $SkillsDir "awesome-bid"
$ScriptDir = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($ScriptDir)) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

Write-Host "安装到: $Dest"
$env:BID_SKILL_HOME = $Dest
[Environment]::SetEnvironmentVariable('BID_SKILL_HOME', $Dest, 'User')
Write-Host "已设置用户环境变量 BID_SKILL_HOME=$Dest"

# 安全检查：Dest 不能为空、不能是根目录、路径中必须包含 awesome-bid
if (
    [string]::IsNullOrWhiteSpace($Dest) -or
    $Dest -eq [System.IO.Path]::GetPathRoot($Dest) -or
    $Dest -notlike '*awesome-bid*'
) {
    Write-Error "错误：安装目标路径异常 ($Dest)，中止。"
    exit 1
}

$RuntimeItems = @(
    "SKILL.md",
    "agents",
    "skills",
    "knowledge",
    "memory",
    "templates",
    "tools"
)

# 校验安装源完整性，避免删除旧安装后才发现源文件缺失
foreach ($Item in $RuntimeItems) {
    $Source = Join-Path $ScriptDir $Item
    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Error "错误：缺少安装源文件或目录: $Source"
        exit 1
    }
}

# 创建技能目录，已存在则清空
if (Test-Path -LiteralPath $Dest) {
    Remove-Item -LiteralPath $Dest -Recurse -Force
}
New-Item -ItemType Directory -Path $Dest -Force | Out-Null

# 只复制运行时需要的文件
foreach ($Item in $RuntimeItems) {
    $Source = Join-Path $ScriptDir $Item
    Copy-Item -LiteralPath $Source -Destination $Dest -Recurse -Force
}

$InitScript = Join-Path $Dest "tools\init.py"
Write-Host "安装完成!"
Write-Host "在投标项目目录运行: python `"$InitScript`" [project-path] [--type <1-4>]"
