<#
  Aetheria Core - Linode 部署腳本

  使用方式：\.\deploy_linode.ps1
  - 建議先用 setup_ssh_key.ps1 設定 SSH key（免密部署）
  - 會同時更新：
    - 後端：/root/Aetheria_Core（systemd aetheria.service）
    - 前端：/opt/aetheria（Nginx root 指向 /opt/aetheria/webapp/dist）
#>

$SERVER = "root@172.237.6.53"
$BACKEND_DIR = "/root/Aetheria_Core"  # 後端 repo 位置
$FRONTEND_DIR = "/opt/aetheria"       # 前端/Nginx root 對應 repo 位置

function Invoke-Remote($cmd) {
    ssh $SERVER $cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Remote command failed: $cmd"
    }
}

Write-Host "🚀 開始部署 Aetheria Core 到 Linode..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 檢查後端目錄..." -ForegroundColor Yellow
$backendExists = ssh $SERVER "test -d $BACKEND_DIR && echo 'exists' || echo 'not_exists'"
if ($backendExists -match "not_exists") {
    Write-Host "   ⚠️  後端目錄不存在，正在克隆 repository..." -ForegroundColor Yellow
    Invoke-Remote "cd /root && git clone https://github.com/stevechen1112/Aetheria_Core.git"
} else {
    Write-Host "   ✅ 後端目錄已存在" -ForegroundColor Green
}

Write-Host "📁 檢查前端目錄..." -ForegroundColor Yellow
$frontendExists = ssh $SERVER "test -d $FRONTEND_DIR && echo 'exists' || echo 'not_exists'"
if ($frontendExists -match "not_exists") {
    Write-Host "   ⚠️  前端目錄不存在，正在克隆 repository..." -ForegroundColor Yellow
    Invoke-Remote "mkdir -p $FRONTEND_DIR && cd $FRONTEND_DIR/.. && git clone https://github.com/stevechen1112/Aetheria_Core.git $(Split-Path -Leaf $FRONTEND_DIR)"
} else {
    Write-Host "   ✅ 前端目錄已存在" -ForegroundColor Green
}

Write-Host ""
Write-Host "📥 更新後端代碼..." -ForegroundColor Yellow
Invoke-Remote "cd $BACKEND_DIR && git fetch origin && git reset --hard origin/main && git log -1 --oneline"
Write-Host "   ✅ 後端代碼更新完成" -ForegroundColor Green

Write-Host ""
Write-Host "📦 安裝 Python 依賴..." -ForegroundColor Yellow
Invoke-Remote "cd $BACKEND_DIR && if [ -d .venv ]; then VENV=.venv; elif [ -d venv ]; then VENV=venv; else VENV=.venv; python3 -m venv \"$VENV\"; fi; . \"$VENV/bin/activate\"; pip install -q -r requirements.txt"
Write-Host "   ✅ Python 依賴安裝完成" -ForegroundColor Green

Write-Host ""
Write-Host "📦 安裝前端依賴..." -ForegroundColor Yellow
Write-Host "📥 更新前端代碼..." -ForegroundColor Yellow
Invoke-Remote "cd $FRONTEND_DIR && git fetch origin && git reset --hard origin/main && git log -1 --oneline"
Write-Host "   ✅ 前端代碼更新完成" -ForegroundColor Green

Write-Host ""
Write-Host "📦 安裝前端依賴..." -ForegroundColor Yellow
Invoke-Remote "cd $FRONTEND_DIR/webapp && (npm ci --silent || npm install --silent)"
Write-Host "   ✅ 前端依賴安裝完成" -ForegroundColor Green

Write-Host ""
Write-Host "🏗️  建置前端（輸出到 dist/）..." -ForegroundColor Yellow
Invoke-Remote "cd $FRONTEND_DIR/webapp && npm run build"
Write-Host "   ✅ 前端建置完成" -ForegroundColor Green

Write-Host ""
Write-Host "🔄 重啟服務..." -ForegroundColor Yellow

Write-Host "   使用 systemd 重啟 aetheria.service..." -ForegroundColor Cyan
Invoke-Remote "systemctl restart aetheria.service"
Invoke-Remote "systemctl is-active aetheria.service"

Write-Host ""
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 檢查應用狀態：" -ForegroundColor Cyan
Write-Host "   http://172.237.6.53:5001/health" -ForegroundColor White
Write-Host ""
