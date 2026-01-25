# Aetheria UI v2.0 E2E Test Script
# Test member registration, login, profile management

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Aetheria UI v2.0 E2E Testing" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:5001"
$testEmail = "e2etest_$(Get-Random)@example.com"
$testPassword = "testpass123"
$testDisplayName = "E2E Test User"

# 測試計數器
$totalTests = 0
$passedTests = 0
$failedTests = 0

function Test-API {
    param(
        [string]$TestName,
        [scriptblock]$TestBlock
    )
    
    $script:totalTests++
    Write-Host "[$script:totalTests] 測試: $TestName" -ForegroundColor Yellow
    
    try {
        & $TestBlock
        Write-Host "  ✅ 通過" -ForegroundColor Green
        $script:passedTests++
        return $true
    } catch {
        Write-Host "  ❌ 失敗: $($_.Exception.Message)" -ForegroundColor Red
        $script:failedTests++
        return $false
    }
}

# 測試 1: 健康檢查
Test-API "後端健康檢查" {
    try {
        $result = Invoke-WebRequest -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
        if ($result.StatusCode -ne 200) {
            throw "狀態碼不是 200"
        }
    } catch {
        # /health 可能不存在，嘗試其他端點
        $result = Invoke-WebRequest -Uri "$baseUrl/api/tarot/daily" -Method Get -ErrorAction Stop
        if ($result.StatusCode -ne 200) {
            throw "API 不可用"
        }
    }
}

# 測試 2: 會員註冊
$global:registeredToken = $null
$global:registeredUserId = $null

Test-API "會員註冊功能" {
    $headers = @{'Content-Type'='application/json'}
    $body = @{
        email = $testEmail
        password = $testPassword
        display_name = $testDisplayName
        consents = @{
            terms_accepted = $true
            data_usage_accepted = $true
        }
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" -Method Post -Headers $headers -Body $body
    
    if ($result.status -ne 'success') {
        throw "註冊失敗"
    }
    if (-not $result.token) {
        throw "沒有返回 token"
    }
    if (-not $result.user_id) {
        throw "沒有返回 user_id"
    }
    
    $global:registeredToken = $result.token
    $global:registeredUserId = $result.user_id
    Write-Host "  → User ID: $($result.user_id)" -ForegroundColor Gray
    Write-Host "  → Token: $($result.token.Substring(0, 16))..." -ForegroundColor Gray
}

# 測試 3: 重複註冊（應該失敗）
Test-API "重複註冊防護" {
    $headers = @{'Content-Type'='application/json'}
    $body = @{
        email = $testEmail
        password = $testPassword
        display_name = "重複用戶"
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" -Method Post -Headers $headers -Body $body -ErrorAction Stop
        throw "應該要失敗但成功了"
    } catch {
        if ($_.Exception.Message -like "*409*" -or $_.Exception.Message -like "*已註冊*") {
            # 正確：返回 409 衝突
            return
        } else {
            throw $_
        }
    }
}

# 測試 4: 錯誤密碼登入（應該失敗）
Test-API "錯誤密碼防護" {
    $headers = @{'Content-Type'='application/json'}
    $body = @{
        email = $testEmail
        password = "wrongpassword"
    } | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method Post -Headers $headers -Body $body -ErrorAction Stop
        throw "應該要失敗但成功了"
    } catch {
        if ($_.Exception.Message -like "*401*" -or $_.Exception.Message -like "*錯誤*") {
            # 正確：返回 401 未授權
            return
        } else {
            throw $_
        }
    }
}

# 測試 5: 正確登入
$global:loginToken = $null

Test-API "會員登入功能" {
    $headers = @{'Content-Type'='application/json'}
    $body = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method Post -Headers $headers -Body $body
    
    if ($result.status -ne 'success') {
        throw "登入失敗"
    }
    if (-not $result.token) {
        throw "沒有返回 token"
    }
    
    $global:loginToken = $result.token
    Write-Host "  → Token: $($result.token.Substring(0, 16))..." -ForegroundColor Gray
}

# 測試 6: 獲取個人資料
Test-API "獲取個人資料" {
    $headers = @{
        'Authorization' = "Bearer $global:loginToken"
        'Content-Type' = 'application/json'
    }
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/profile" -Method Get -Headers $headers
    
    if ($result.status -ne 'success') {
        throw "獲取失敗"
    }
    if ($result.profile.email -ne $testEmail) {
        throw "Email 不符"
    }
    if ($result.profile.display_name -ne $testDisplayName) {
        throw "顯示名稱不符"
    }
    
    Write-Host "  → Email: $($result.profile.email)" -ForegroundColor Gray
    Write-Host "  → 顯示名稱: $($result.profile.display_name)" -ForegroundColor Gray
}

# 測試 7: 更新個人資料
Test-API "更新個人資料" {
    $headers = @{
        'Authorization' = "Bearer $global:loginToken"
        'Content-Type' = 'application/json'
    }
    $body = @{
        display_name = "更新後的名稱"
        phone = "0912345678"
        preferences = @{
            tone = "professional"
            response_length = "medium"
        }
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/profile" -Method Patch -Headers $headers -Body $body
    
    if ($result.status -ne 'success') {
        throw "更新失敗"
    }
    
    # 驗證更新
    $profile = Invoke-RestMethod -Uri "$baseUrl/api/profile" -Method Get -Headers $headers
    if ($profile.profile.display_name -ne "更新後的名稱") {
        throw "名稱未更新"
    }
    if ($profile.profile.phone -ne "0912345678") {
        throw "電話未更新"
    }
    
    Write-Host "  → 新名稱: $($profile.profile.display_name)" -ForegroundColor Gray
}

# 測試 8: 登出
Test-API "會員登出功能" {
    $headers = @{
        'Authorization' = "Bearer $global:loginToken"
        'Content-Type' = 'application/json'
    }
    $body = @{
        token = $global:loginToken
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "$baseUrl/api/auth/logout" -Method Post -Headers $headers -Body $body
    
    if ($result.status -ne 'success') {
        throw "登出失敗"
    }
}

# 測試 9: 登出後無法訪問（應該失敗）
Test-API "登出後 Token 失效" {
    $headers = @{
        'Authorization' = "Bearer $global:loginToken"
        'Content-Type' = 'application/json'
    }
    
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/api/profile" -Method Get -Headers $headers -ErrorAction Stop
        throw "應該要失敗但成功了"
    } catch {
        if ($_.Exception.Message -like "*401*" -or $_.Exception.Message -like "*404*") {
            # 正確：Token 已失效
            return
        } else {
            throw $_
        }
    }
}

# 測試 10: 前端頁面加載
Test-API "前端頁面可訪問" {
    $result = Invoke-WebRequest -Uri "http://localhost:5173" -Method Get
    
    if ($result.StatusCode -ne 200) {
        throw "前端無法訪問"
    }
    if ($result.Content -notlike "*Aetheria*") {
        throw "前端內容不正確"
    }
}

# 輸出測試結果
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "測試結果摘要" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "總測試數: $totalTests" -ForegroundColor White
Write-Host "通過: $passedTests" -ForegroundColor Green
Write-Host "失敗: $failedTests" -ForegroundColor Red
Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "✅ 所有測試通過！" -ForegroundColor Green
    Write-Host "會員註冊、登入、個人資料管理功能完整且正常運作。" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ 有 $failedTests 個測試失敗" -ForegroundColor Red
    exit 1
}
