# Aetheria Core - Linode deploy script (Windows PowerShell 5.1 safe)
# Usage: .\deploy_linode.ps1

$ErrorActionPreference = 'Stop'

$SERVER = 'root@172.237.6.53'
$BACKEND_DIR = '/root/Aetheria_Core'
$FRONTEND_DIR = '/opt/aetheria'

$FRONTEND_PARENT_DIR = $FRONTEND_DIR.Substring(0, $FRONTEND_DIR.LastIndexOf('/'))
$FRONTEND_BASENAME = $FRONTEND_DIR.Substring($FRONTEND_DIR.LastIndexOf('/') + 1)

function Invoke-Remote([string]$cmd) {
    ssh $SERVER $cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Remote command failed: $cmd"
    }
}

Write-Host "Deploy to Linode: $SERVER" -ForegroundColor Cyan

Write-Host "Check backend dir..." -ForegroundColor Yellow
$backendExists = ssh $SERVER ("if [ -d " + $BACKEND_DIR + " ]; then echo exists; else echo not_exists; fi")
if ($backendExists -match 'not_exists') {
    Write-Host "Backend dir missing, cloning..." -ForegroundColor Yellow
    Invoke-Remote "set -e; cd /root; git clone https://github.com/stevechen1112/Aetheria_Core.git"
} else {
    Write-Host "Backend dir exists" -ForegroundColor Green
}

Write-Host "Check frontend dir..." -ForegroundColor Yellow
$frontendExists = ssh $SERVER ("if [ -d " + $FRONTEND_DIR + " ]; then echo exists; else echo not_exists; fi")
if ($frontendExists -match 'not_exists') {
    Write-Host "Frontend dir missing, cloning..." -ForegroundColor Yellow
    Invoke-Remote ("set -e; mkdir -p " + $FRONTEND_PARENT_DIR + "; cd " + $FRONTEND_PARENT_DIR + "; git clone https://github.com/stevechen1112/Aetheria_Core.git " + $FRONTEND_BASENAME)
} else {
    Write-Host "Frontend dir exists" -ForegroundColor Green
}

Write-Host "Update backend code..." -ForegroundColor Yellow
Invoke-Remote ("set -e; cd " + $BACKEND_DIR + "; git fetch origin; git reset --hard origin/main; git log -1 --oneline")

Write-Host "Install backend deps..." -ForegroundColor Yellow
Invoke-Remote ("set -e; cd " + $BACKEND_DIR + "; if [ -d .venv ]; then VENV=.venv; elif [ -d venv ]; then VENV=venv; else VENV=.venv; python3 -m venv `$VENV; fi; . `$VENV/bin/activate; pip install -q -r requirements.txt")

Write-Host "Update frontend code..." -ForegroundColor Yellow
Invoke-Remote ("set -e; cd " + $FRONTEND_DIR + "; git fetch origin; git reset --hard origin/main; git log -1 --oneline")

Write-Host "Install frontend deps..." -ForegroundColor Yellow
Invoke-Remote ("set -e; cd " + $FRONTEND_DIR + "/webapp; npm install --silent")

Write-Host "Build frontend (dist)..." -ForegroundColor Yellow
Invoke-Remote ("set -e; cd " + $FRONTEND_DIR + "/webapp; npm run build")

Write-Host "Restart service..." -ForegroundColor Yellow
Invoke-Remote "systemctl restart aetheria-api.service"

$state = ''
for ($i = 0; $i -lt 12; $i++) {
    Start-Sleep -Seconds 1
    $state = ssh $SERVER "systemctl is-active aetheria-api.service; exit 0"
    if ($state -match 'active') { break }
}

Write-Host ("Service state: " + ($state -replace "\s+", " ").Trim()) -ForegroundColor Cyan
ssh $SERVER "systemctl status --no-pager -l aetheria-api.service | head -n 25; exit 0" | Out-Host

Write-Host "Deploy done" -ForegroundColor Green
Write-Host "Health: http://172.237.6.53:5001/health" -ForegroundColor White
