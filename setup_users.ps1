# 创建测试用户的 PowerShell 脚本

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Aetheria 测试用户设置" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$baseUrl = "http://localhost:5000"

# 创建用户 test_user_002
Write-Host "`n正在创建 test_user_002..." -ForegroundColor Yellow

$body = @{
    user_id = "test_user_002"
    birth_date = "农历70年5月15日"
    birth_time = "14:30"
    birth_location = "台湾台北市"
    gender = "女"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/analysis" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✓ 命盘分析完成" -ForegroundColor Green
    
    Start-Sleep -Seconds 2
    
    $lockBody = @{ user_id = "test_user_002" } | ConvertTo-Json
    $lockResponse = Invoke-RestMethod -Uri "$baseUrl/api/lock" -Method Post -Body $lockBody -ContentType "application/json"
    Write-Host "✓ 命盘已锁定" -ForegroundColor Green
    
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "✓ 测试用户准备完成" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "`n现在可以运行：" -ForegroundColor White
    Write-Host "  python test_advanced_auto.py" -ForegroundColor Yellow
    
} catch {
    Write-Host "✗ 错误: $_" -ForegroundColor Red
}
