# GitHub Actions 自動部署設定指南

## 📋 設定步驟

### 1. 將 SSH 私鑰加入 GitHub Secrets

1. **取得 SSH 私鑰內容**：
   ```powershell
   cat $env:USERPROFILE\.ssh\id_rsa
   ```
   複製完整輸出（包含 `-----BEGIN RSA PRIVATE KEY-----` 和 `-----END RSA PRIVATE KEY-----`）

2. **加入 GitHub Secrets**：
   - 前往 https://github.com/stevechen1112/Aetheria_Core/settings/secrets/actions
   - 點擊 **"New repository secret"**
   - Name: `SSH_PRIVATE_KEY`
   - Value: 貼上剛才複製的私鑰內容
   - 點擊 **"Add secret"**

### 2. 確認伺服器已設定 SSH 公鑰

確認以下內容已在伺服器 `/root/.ssh/authorized_keys` 中：

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC5ismbd+XKcT2Nad1anwElkgjSFifI7nV01G/P4dcRBsXhFUXh/veh860UB/xdBFePhwuaKlCG3qgCXBlLYt8zusSTpIVxl6u4CjNos3/1kBCJ7I/fOPUnmyNdVuzQxCXDPkeEFJsg2M/tDTZIaCNTQmYGSokTdBR9Cth1UuYKtwYaKvId4cFrJydAT1iSUEH4MQK6lToNpLe6+2nNkdB+VnagWljPlVFo0iDgIe0UjTSsJLxa+bfVBuxiqMIJMRH75406b4I/EN7so70RSQK1rmg2Ar+pz78lC8rblV2enqLCxtY3bwYjOfIQ2LsFD84/+8D6xYidzviDyboXIoRB7fSl6AJW1VtvpUlSSw6ojuG+oXD7c0CN6fDJ+jAtJv6AA70Wk8+89NtZL9gtwSr5he8/mzHUtKVQqxwmEfFjEABuhMrZOG11C5FZ1r08sHI9esJcn8bYG1WRdI9CEdHfAMRkKZfHGaXjnBOGqb/65add1DO4geUbLYl6+9yvw1HOpZGHg8yA1KyfZiovECrILD2PMdGkx48I1/v0UTNlwKW6VEjqdGrnEx5u9MtDcTheN3mdpHksueVC4fAcoTS5TOPwKNZuh1q4lz0sM3L/91F1aQtyp42aHTm15VnRBs5j71NFRhxbDJCM+8vzBzjjRHXf5YC2EpfmTxCdpe+B8Q== user@DESKTOP-P2P8LUT
```

如果沒有，執行：
```powershell
.\setup_ssh_key.ps1
```

### 3. 測試自動部署

完成上述設定後，每次推送到 `main` 分支時會自動觸發部署：

```powershell
git add .
git commit -m "test: trigger auto-deploy"
git push origin main
```

或手動觸發：
- 前往 https://github.com/stevechen1112/Aetheria_Core/actions
- 選擇 "Deploy to Linode" workflow
- 點擊 "Run workflow"

### 4. 監控部署狀態

- 前往 https://github.com/stevechen1112/Aetheria_Core/actions
- 查看最新的 workflow run
- 可即時查看部署日誌

---

## 🔍 故障排除

### 問題：SSH 連接失敗

**解決方法**：
1. 確認私鑰格式正確（PEM 格式，不是 OpenSSH 格式）
2. 如果是 OpenSSH 格式，轉換為 PEM：
   ```powershell
   ssh-keygen -p -m PEM -f $env:USERPROFILE\.ssh\id_rsa
   ```

### 問題：權限拒絕

**解決方法**：
1. 確認公鑰已加入伺服器：
   ```bash
   ssh root@172.237.6.53 "cat ~/.ssh/authorized_keys"
   ```
2. 確認權限正確：
   ```bash
   ssh root@172.237.6.53 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
   ```

### 問題：服務重啟失敗

**解決方法**：
手動檢查伺服器上使用的 process manager：
```bash
ssh root@172.237.6.53 "systemctl status aetheria || supervisorctl status aetheria || pm2 list"
```

---

## 📝 Workflow 說明

### 觸發條件
- 推送到 `main` 分支
- 手動觸發（workflow_dispatch）

### 部署流程
1. SSH 連接到伺服器
2. Pull 最新代碼
3. 安裝 Python 依賴
4. 安裝前端依賴
5. 建置前端
6. 重啟服務（自動偵測 systemd/supervisor/PM2）

### 環境變數
目前無需額外環境變數，伺服器已有 `.env` 文件。

如需更新伺服器環境變數，需手動 SSH 登入修改 `/root/Aetheria_Core/.env`。

---

## ✅ 完成確認

設定完成後，您應該能夠：
- ✅ 推送代碼到 GitHub 自動觸發部署
- ✅ 在 Actions 頁面看到部署進度
- ✅ 部署完成後檢查健康狀態：http://172.237.6.53:5001/api/utils/health
