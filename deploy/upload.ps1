# Aetheria Core - Windows 上傳腳本
# 使用方式: 在 PowerShell 中執行此腳本

$REMOTE_HOST = "172.237.19.63"
$REMOTE_USER = "root"
$REMOTE_DIR = "/opt/aetheria"
$LOCAL_DIR = "C:\Users\User\Desktop\Aetheria_Core"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Aetheria Core - 上傳到 Linode" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 創建壓縮檔
Write-Host "`n[1/3] 正在打包專案..." -ForegroundColor Yellow

# 排除不需要的檔案
$excludeList = @(
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "*.pyc",
    "dist",
    ".env",
    "deploy"
)

$tempZip = "$env:TEMP\aetheria_deploy.zip"
if (Test-Path $tempZip) { Remove-Item $tempZip -Force }

# 使用 Compress-Archive
$filesToInclude = Get-ChildItem -Path $LOCAL_DIR -Exclude $excludeList
Compress-Archive -Path $filesToInclude.FullName -DestinationPath $tempZip -Force

Write-Host "  壓縮檔已創建: $tempZip" -ForegroundColor Green
Write-Host "  大小: $([math]::Round((Get-Item $tempZip).Length / 1MB, 2)) MB" -ForegroundColor Green

# 2. 上傳到伺服器
Write-Host "`n[2/3] 正在上傳到伺服器..." -ForegroundColor Yellow
Write-Host "  請輸入密碼..." -ForegroundColor Cyan

# 使用 scp 上傳
scp $tempZip "${REMOTE_USER}@${REMOTE_HOST}:/tmp/aetheria_deploy.zip"

# 3. 在伺服器上解壓並執行部署
Write-Host "`n[3/3] 正在遠端部署..." -ForegroundColor Yellow

$remoteCommands = @"
mkdir -p $REMOTE_DIR
cd $REMOTE_DIR
rm -rf *
unzip -o /tmp/aetheria_deploy.zip -d $REMOTE_DIR
rm /tmp/aetheria_deploy.zip
chmod +x deploy/deploy.sh
bash deploy/deploy.sh
"@

ssh "${REMOTE_USER}@${REMOTE_HOST}" $remoteCommands

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   部署完成！" -ForegroundColor Green
Write-Host "   訪問: http://$REMOTE_HOST" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
