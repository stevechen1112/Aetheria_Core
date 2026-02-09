#!/usr/bin/env pwsh
# PowerShell 測試腳本

$BASE_URL = "http://localhost:5001"

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Aetheria 修復驗證測試" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# 1. 註冊用戶
$username = "test_fix_$(Get-Date -Format 'HHmmss')"
Write-Host "`n[1] 註冊用戶: $username" -ForegroundColor Yellow

$registerBody = @{
    username = $username
    password = "test123"
    email = "$username@test.com"
} | ConvertTo-Json

try {
    $registerResp = Invoke-RestMethod -Uri "$BASE_URL/api/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -TimeoutSec 10
    if ($registerResp.status -ne "success") {
        Write-Host "   ✗ 註冊失敗: $registerResp" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✓ 註冊成功" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 異常: $_" -ForegroundColor Red
    exit 1
}

# 2. 登入
Write-Host "`n[2] 登入用戶" -ForegroundColor Yellow

$loginBody = @{
    username = $username
    password = "test123"
} | ConvertTo-Json

try {
    $loginResp = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -TimeoutSec 10
    if ($loginResp.status -ne "success") {
        Write-Host "   ✗ 登入失敗" -ForegroundColor Red
        exit 1
    }
    $token = $loginResp.token
    $sessionId = $loginResp.session_id
    Write-Host "   ✓ 登入成功 (Session: $sessionId)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 異常: $_" -ForegroundColor Red
    exit 1
}

# 3. 發送包含生辰的訊息
Write-Host "`n[3] 發送包含生辰資料的訊息" -ForegroundColor Yellow

$message = "你好！我是1990年7月22日下午2點15分出生的，男生，在高雄。想了解我的命盤。"
Write-Host "   訊息: $message" -ForegroundColor White

$consultBody = @{
    message = $message
    session_id = $sessionId
} | ConvertTo-Json

Write-Host "`n   AI 回應:" -ForegroundColor White

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/chat/consult-stream" -Method POST -Body $consultBody -Headers $headers -TimeoutSec 60
    
    $toolCalls = @()
    $textChunks = @()
    $fuseTriggered = $false
    
    # 解析 SSE
    $lines = $response.Content -split "`n"
    $eventType = $null
    
    foreach ($line in $lines) {
        if ($line.StartsWith("event:")) {
            $eventType = $line.Substring(6).Trim()
        }
        elseif ($line.StartsWith("data:")) {
            $dataStr = $line.Substring(5).Trim()
            try {
                $data = $dataStr | ConvertFrom-Json
                
                if ($eventType -eq "text") {
                    $chunk = $data.chunk
                    Write-Host $chunk -NoNewline
                    $textChunks += $chunk
                }
                elseif ($eventType -eq "tool") {
                    $status = $data.status
                    $name = $data.name
                    if ($status -eq "executing") {
                        Write-Host "`n   [工具執行] $name" -ForegroundColor Magenta
                        $toolCalls += $name
                        if ($data.fuse_triggered) {
                            $fuseTriggered = $true
                            Write-Host "   ⚡ [熔斷機制觸發]" -ForegroundColor Red
                        }
                    }
                }
                elseif ($eventType -eq "done") {
                    Write-Host "`n`n   ✓ 對話完成" -ForegroundColor Green
                    break
                }
            } catch {}
        }
    }
    
    # 分析結果
    $fullText = -join $textChunks
    
    Write-Host "`n==============================================================" -ForegroundColor Cyan
    Write-Host "測試結果分析:" -ForegroundColor Cyan
    Write-Host "==============================================================" -ForegroundColor Cyan
    
    Write-Host "`n✓ AI 回應長度: $($fullText.Length) 字元" -ForegroundColor White
    Write-Host "✓ 工具調用次數: $($toolCalls.Count)" -ForegroundColor White
    Write-Host "✓ 調用的工具: $($toolCalls -join ', ')" -ForegroundColor White
    
    if ($fuseTriggered) {
        Write-Host "⚡ 熔斷機制觸發: 是" -ForegroundColor Red
    }
    
    # 檢查項目
    $successCount = 0
    $totalChecks = 4
    
    Write-Host "`n檢查項目:" -ForegroundColor Yellow
    
    # Check 1: AI 有排盤
    if ($toolCalls.Count -gt 0) {
        Write-Host "  [✓] AI 主動排盤" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  [✗] AI 未排盤" -ForegroundColor Red
    }
    
    # Check 2: 排盤工具包含計算類
    $calculateTools = $toolCalls | Where-Object { $_ -like "*calculate*" }
    if ($calculateTools.Count -gt 0) {
        Write-Host "  [✓] 執行了計算工具: $($calculateTools -join ', ')" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  [✗] 未執行計算工具" -ForegroundColor Red
    }
    
    # Check 3: 沒有反覆詢問
    $questionCount = ($fullText -split '\?').Count + ($fullText -split '？').Count - 2
    if ($questionCount -lt 3) {
        Write-Host "  [✓] 沒有過度詢問（問號數: $questionCount）" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  [✗] 疑似反覆詢問（問號數: $questionCount）" -ForegroundColor Red
    }
    
    # Check 4: 有具體分析內容
    $keywords = @('命宮', '主星', '八字', '日主', '太陽', '上升', '宮位')
    $foundKeywords = $keywords | Where-Object { $fullText -like "*$_*" }
    if ($foundKeywords.Count -gt 0) {
        Write-Host "  [✓] 包含命理術語: $($foundKeywords[0..2] -join ', ')" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  [✗] 缺少命理分析內容" -ForegroundColor Red
    }
    
    Write-Host "`n==============================================================" -ForegroundColor Cyan
    Write-Host "總評: $successCount/$totalChecks 項通過" -ForegroundColor White
    
    if ($successCount -ge 3) {
        Write-Host "✓✓✓ 修復效果良好！" -ForegroundColor Green
    } elseif ($successCount -ge 2) {
        Write-Host "⚠ 部分改善，仍需調整" -ForegroundColor Yellow
    } else {
        Write-Host "✗✗✗ 修復未生效" -ForegroundColor Red
    }
    
    Write-Host "==============================================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "   ✗ 異常: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
