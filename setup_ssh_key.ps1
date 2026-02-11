# SSH 金鑰配置腳本（讓 Linode 免密碼登入）
# 使用方式：.\setup_ssh_key.ps1（只需執行一次，會要求輸入 root 密碼）

$SERVER = "root@172.237.6.53"
$PUBLIC_KEY_PATH = "$env:USERPROFILE\.ssh\id_rsa.pub"

Write-Host "🔑 配置 SSH 金鑰到 Linode 伺服器..." -ForegroundColor Cyan
Write-Host ""

# 檢查公鑰是否存在
if (-not (Test-Path $PUBLIC_KEY_PATH)) {
    Write-Host "❌ 找不到 SSH 公鑰：$PUBLIC_KEY_PATH" -ForegroundColor Red
    Write-Host "   請先生成 SSH 金鑰：ssh-keygen -t rsa -b 4096" -ForegroundColor Yellow
    exit 1
}

# 讀取公鑰
$publicKey = Get-Content $PUBLIC_KEY_PATH -Raw
Write-Host "✅ 找到 SSH 公鑰" -ForegroundColor Green
Write-Host ""

# 上傳公鑰到伺服器
Write-Host "📤 上傳公鑰到伺服器（需要輸入 root 密碼）..." -ForegroundColor Yellow
$command = @"
mkdir -p ~/.ssh && \
chmod 700 ~/.ssh && \
echo '$publicKey' >> ~/.ssh/authorized_keys && \
chmod 600 ~/.ssh/authorized_keys && \
echo 'SSH key added successfully'
"@

ssh $SERVER $command

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SSH 金鑰配置完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "🧪 測試免密碼登入..." -ForegroundColor Cyan
    $testResult = ssh -o ConnectTimeout=5 $SERVER "echo 'Connection successful without password'"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 免密碼登入測試成功！" -ForegroundColor Green
        Write-Host "   您現在可以執行 .\deploy_linode.ps1 進行部署（無需密碼）" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  免密碼登入測試失敗，可能需要重新配置" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "❌ SSH 金鑰配置失敗" -ForegroundColor Red
}

Write-Host ""
