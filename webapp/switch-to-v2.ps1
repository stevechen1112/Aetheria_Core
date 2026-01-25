# Aetheria UI v2.0 啟用腳本
# 使用方法：在 PowerShell 中執行 .\switch-to-v2.ps1

Write-Host "🎨 Aetheria UI v2.0 啟用腳本" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

$srcPath = "src"

# 檢查是否在正確的目錄
if (-not (Test-Path $srcPath)) {
    Write-Host "❌ 錯誤：請在 webapp 目錄下執行此腳本" -ForegroundColor Red
    exit 1
}

# 備份舊版本
Write-Host "📦 備份舊版本..." -ForegroundColor Yellow

if (Test-Path "$srcPath\App.jsx") {
    if (-not (Test-Path "$srcPath\App.old.jsx")) {
        Copy-Item "$srcPath\App.jsx" "$srcPath\App.old.jsx"
        Write-Host "  ✓ App.jsx -> App.old.jsx" -ForegroundColor Green
    } else {
        Write-Host "  ℹ App.old.jsx 已存在，跳過備份" -ForegroundColor Gray
    }
}

if (Test-Path "$srcPath\App.css") {
    if (-not (Test-Path "$srcPath\App.old.css")) {
        Copy-Item "$srcPath\App.css" "$srcPath\App.old.css"
        Write-Host "  ✓ App.css -> App.old.css" -ForegroundColor Green
    } else {
        Write-Host "  ℹ App.old.css 已存在，跳過備份" -ForegroundColor Gray
    }
}

# 啟用新版本
Write-Host "`n🚀 啟用 v2.0 版本..." -ForegroundColor Yellow

if (Test-Path "$srcPath\App.v2.jsx") {
    Copy-Item "$srcPath\App.v2.jsx" "$srcPath\App.jsx" -Force
    Write-Host "  ✓ App.v2.jsx -> App.jsx" -ForegroundColor Green
} else {
    Write-Host "  ❌ 找不到 App.v2.jsx" -ForegroundColor Red
    exit 1
}

if (Test-Path "$srcPath\App.v2.css") {
    Copy-Item "$srcPath\App.v2.css" "$srcPath\App.css" -Force
    Write-Host "  ✓ App.v2.css -> App.css" -ForegroundColor Green
} else {
    Write-Host "  ❌ 找不到 App.v2.css" -ForegroundColor Red
    exit 1
}

Write-Host "`n✨ UI v2.0 啟用成功！" -ForegroundColor Green
Write-Host "`n📝 後續步驟：" -ForegroundColor Cyan
Write-Host "  1. npm run dev - 啟動開發伺服器" -ForegroundColor White
Write-Host "  2. 訪問 http://localhost:5173" -ForegroundColor White
Write-Host "  3. 查看 UI_V2_README.md 了解新功能`n" -ForegroundColor White
