# 快速创建 test_user_002
Write-Host "正在创建 test_user_002..." -ForegroundColor Yellow

# 步骤1：分析命盘
$body1 = @{
    user_id = "test_user_002"
    birth_date = "农历70年5月15日"
    birth_time = "14:30"
    birth_location = "台湾台北市"
    gender = "女"
} | ConvertTo-Json -Compress

Write-Host "`n步骤1：开始命盘分析..."
$r1 = Invoke-RestMethod -Uri "http://localhost:5000/api/analysis" -Method POST -Body $body1 -ContentType "application/json"
Write-Host "✓ 分析完成" -ForegroundColor Green

# 等待2秒
Start-Sleep -Seconds 2

# 步骤2：锁定命盘
$body2 = @{
    user_id = "test_user_002"
} | ConvertTo-Json -Compress

Write-Host "`n步骤2：锁定命盘..."
$r2 = Invoke-RestMethod -Uri "http://localhost:5000/api/lock" -Method POST -Body $body2 -ContentType "application/json"
Write-Host "✓ 命盘已锁定" -ForegroundColor Green

# 验证
Write-Host "`n步骤3：验证创建结果..."
$verify = Invoke-RestMethod -Uri "http://localhost:5000/api/lock/test_user_002" -Method GET
Write-Host "✓ test_user_002 创建成功！" -ForegroundColor Green
Write-Host "`n用户信息："
Write-Host "  用户ID: test_user_002"
Write-Host "  出生: 农历70年5月15日 14:30"
Write-Host "  地点: 台湾台北市"
Write-Host "  性别: 女"
Write-Host "`n现在可以运行合盘测试了！" -ForegroundColor Cyan
