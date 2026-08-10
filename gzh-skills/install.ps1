# gzh-skills 一键安装脚本（Windows PowerShell）
#
# 功能：
#   1. 把本目录下所有 gzh-* 技能文件夹复制到目标 Agent 平台的 skills/ 目录
#   2. 自动从 gzh-image/config.example.json 生成 config.json 模板（若尚不存在）
#
# 用法：
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 D:\skills   # 指定目标目录
#
# 默认目标：%USERPROFILE%\.workbuddy\skills

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

if ($args.Count -gt 0) {
    $Target = $args[0]
} else {
    $Target = Join-Path $env:USERPROFILE ".workbuddy\skills"
}

Write-Host "▶ gzh-skills 一键安装"
Write-Host "  源目录  : $ScriptDir"
Write-Host "  目标目录: $Target"
Write-Host ""

New-Item -ItemType Directory -Force -Path $Target | Out-Null

$skills = Get-ChildItem -Path $ScriptDir -Directory -Filter 'gzh-*' | Sort-Object Name
if ($skills.Count -eq 0) {
    Write-Host "⚠️  未在 $ScriptDir 下找到任何 gzh-* 技能目录，请确认脚本位置正确。"
    exit 1
}

$count = 0
foreach ($d in $skills) {
    Write-Host "  · 安装 $($d.Name)"
    $dest = Join-Path $Target $d.Name
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item $d.FullName $dest -Recurse -Force
    $count++
}

$example = Join-Path $Target 'gzh-image\config.example.json'
$cfg = Join-Path $Target 'gzh-image\config.json'
if ((Test-Path $example) -and -not (Test-Path $cfg)) {
    Copy-Item $example $cfg
    Write-Host "  · 已生成 gzh-image/config.json 模板，请填入你的 providers / wechat 密钥"
}

Write-Host ""
Write-Host "✅ 完成：共安装 $count 个技能到 $Target"
Write-Host "   下一步：编辑 $cfg 填入图像与微信公众号密钥"
Write-Host "   使用说明：见各技能 SKILL.md 与合集 README"
