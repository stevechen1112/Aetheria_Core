# Aetheria Core - Linode 部署腳本
# 使用方式：.\deploy_linode.ps1（會要求輸入 SSH 密碼）

$SERVER = "root@172.237.6.53"
$APP_DIR = "/root/Aetheria_Core"  # 如果路徑不同，請修改這裡

Write-Host "🚀 開始部署 Aetheria Core 到 Linode..." -ForegroundColor Cyan
Write-Host ""

# 檢查伺服器上是否已存在應用目錄
Write-Host "📁 檢查應用目錄..." -ForegroundColor Yellow
$checkCmd = "test -d $APP_DIR && echo 'exists' || echo 'not_exists'"
$result = ssh $SERVER $checkCmd

if ($result -match "not_exists") {
    Write-Host "   ⚠️  應用目錄不存在，正在克隆 repository..." -ForegroundColor Yellow
    ssh $SERVER "cd /root && git clone https://github.com/stevechen1112/Aetheria_Core.git"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 克隆失敗" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   ✅ 應用目錄已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "📥 拉取最新代碼..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR && git fetch origin && git reset --hard origin/main"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git pull 失敗" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 代碼更新完成 (Commit: ed6c003)" -ForegroundColor Green

Write-Host ""
Write-Host "📦 安裝 Python 依賴..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python 依賴安裝失敗" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Python 依賴安裝完成" -ForegroundColor Green

Write-Host ""
Write-Host "📦 安裝前端依賴..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR/webapp && npm install"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install 失敗" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 前端依賴安裝完成" -ForegroundColor Green

Write-Host ""
Write-Host "🏗️  建置前端..." -ForegroundColor Yellow
ssh $SERVER "cd $APP_DIR/webapp && npm run build"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 前端建置失敗" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ 前端建置完成" -ForegroundColor Green

Write-Host ""
Write-Host "🔄 重啟服務..." -ForegroundColor Yellow

# 嘗試檢測使用的 process manager
$pmCheck = ssh $SERVER "
    if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service | grep -q aetheria; then
        echo 'systemd'
    elif command -v supervisorctl >/dev/null 2>&1 && supervisorctl status | grep -q aetheria; then
        echo 'supervisor'
    elif command -v pm2 >/dev/null 2>&1 && pm2 list | grep -q aetheria; then
        echo 'pm2'
    else
        echo 'manual'
    fi
"

switch ($pmCheck.Trim()) {
    "systemd" {
        Write-Host "   使用 systemd 重啟..." -ForegroundColor Cyan
        ssh $SERVER "systemctl restart aetheria"
    }
    "supervisor" {
        Write-Host "   使用 supervisor 重啟..." -ForegroundColor Cyan
        ssh $SERVER "supervisorctl restart aetheria"
    }
    "pm2" {
        Write-Host "   使用 PM2 重啟..." -ForegroundColor Cyan
        ssh $SERVER "cd $APP_DIR && pm2 restart aetheria"
    }
    default {
        Write-Host "   ⚠️  未檢測到 process manager" -ForegroundColor Yellow
        Write-Host "   請手動重啟服務，或執行：" -ForegroundColor Yellow
        Write-Host "   ssh $SERVER 'cd $APP_DIR && python run.py'" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 檢查應用狀態：" -ForegroundColor Cyan
Write-Host "   http://172.237.6.53:5001/api/utils/health" -ForegroundColor White
Write-Host ""
