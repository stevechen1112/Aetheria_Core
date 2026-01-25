# Aetheria UI 還原至舊版本腳本
# 使用方法：在 PowerShell 中執行 .\switch-to-old.ps1

Write-Host "🔄 Aetheria UI 還原至舊版本" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$srcPath = "src"

# 檢查是否在正確的目錄
if (-not (Test-Path $srcPath)) {
    Write-Host "❌ 錯誤：請在 webapp 目錄下執行此腳本" -ForegroundColor Red
    exit 1
}

# 檢查備份是否存在
if (-not (Test-Path "$srcPath\App.old.jsx")) {
    Write-Host "❌ 找不到備份檔案 App.old.jsx" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$srcPath\App.old.css")) {
    Write-Host "❌ 找不到備份檔案 App.old.css" -ForegroundColor Red
    exit 1
}

# 還原舊版本
Write-Host "🔄 還原舊版本..." -ForegroundColor Yellow

Copy-Item "$srcPath\App.old.jsx" "$srcPath\App.jsx" -Force
Write-Host "  ✓ App.old.jsx -> App.jsx" -ForegroundColor Green

Copy-Item "$srcPath\App.old.css" "$srcPath\App.css" -Force
Write-Host "  ✓ App.old.css -> App.css" -ForegroundColor Green

Write-Host "`n✨ 已還原至舊版本！" -ForegroundColor Green
Write-Host "`n📝 後續步驟：" -ForegroundColor Cyan
Write-Host "  1. npm run dev - 啟動開發伺服器`n" -ForegroundColor White
