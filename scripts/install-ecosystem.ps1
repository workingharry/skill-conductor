#!/usr/bin/env pwsh
<#
.SYNOPSIS
    一鍵安裝 Skill Conductor 及其核心聯動技能套件 (One-click installer for Skill Conductor ecosystem)
.DESCRIPTION
    自動檢測並透過 npx skills 安裝：
    - find-skills (Vercel Labs 生態檢索)
    - grill-me, grill-with-docs, domain-modeling (Matt Pocock 決策詰問與 ADR)
    - agent-browser (Vercel Labs 瀏覽器自動化)
    - ponytail (Dietrich Gebert 極簡敏捷實作)
    - gemini-web-copilot (Google Gemini 網頁百萬長上下文 Copilot)
#>

$ErrorActionPreference = "Stop"

Write-Host "🚀 [Skill Conductor] 開始一鍵安裝核心技能套件..." -ForegroundColor Cyan

# 確保目標路徑
$skillsDir = Join-Path $PSScriptRoot ".." ".agents" "skills"
if (-not (Test-Path $skillsDir)) {
    New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
}

$skillsToInstall = @(
    @{ Name = "find-skills"; Source = "https://github.com/vercel-labs/skills"; Skill = "find-skills" },
    @{ Name = "grill-me"; Source = "https://github.com/mattpocock/skills"; Skill = "grill-me" },
    @{ Name = "grill-with-docs"; Source = "https://github.com/mattpocock/skills"; Skill = "grill-with-docs" },
    @{ Name = "domain-modeling"; Source = "https://github.com/mattpocock/skills"; Skill = "domain-modeling" },
    @{ Name = "tdd"; Source = "https://github.com/mattpocock/skills"; Skill = "tdd" },
    @{ Name = "codebase-design"; Source = "https://github.com/mattpocock/skills"; Skill = "codebase-design" },
    @{ Name = "improve-codebase-architecture"; Source = "https://github.com/mattpocock/skills"; Skill = "improve-codebase-architecture" },
    @{ Name = "triage"; Source = "https://github.com/mattpocock/skills"; Skill = "triage" },
    @{ Name = "handoff"; Source = "https://github.com/mattpocock/skills"; Skill = "handoff" },
    @{ Name = "frontend-design"; Source = "https://github.com/anthropics/claude-plugins-official"; Skill = "frontend-design" },
    @{ Name = "guizang-ppt-skill"; Source = "https://github.com/op7418/guizang-ppt-skill"; Skill = "guizang-ppt-skill" },
    @{ Name = "agent-browser"; Source = "https://github.com/vercel-labs/agent-browser"; Skill = "agent-browser" },
    @{ Name = "ponytail"; Source = "https://github.com/dietrichgebert/ponytail"; Skill = "ponytail" }
)

foreach ($item in $skillsToInstall) {
    Write-Host "📦 正在安裝技能: $($item.Name)..." -ForegroundColor Yellow
    npx -y skills add $item.Source --skill $item.Skill --yes
}

# 安裝 gemini-web-copilot
$geminiTarget = Join-Path $skillsDir "gemini-web-copilot"
if (-not (Test-Path $geminiTarget)) {
    Write-Host "📦 正在從 GitHub 安裝 gemini-web-copilot..." -ForegroundColor Yellow
    git clone https://github.com/workingharry/gemini-web-copilot.git $geminiTarget
} else {
    Write-Host "✅ gemini-web-copilot 已存在，略過 clone。" -ForegroundColor Green
}

Write-Host "`n🎉 所有核心技能已全數安裝完成！" -ForegroundColor Green
