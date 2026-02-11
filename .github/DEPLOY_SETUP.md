# GitHub Actions 自動部署設定指南

## 📋 設定步驟

### 1. 建立 Deploy 專用 SSH 金鑰（建議）

在 Windows 本機建立一組僅用於部署的金鑰：

```powershell
ssh-keygen -t ed25519 -C "aetheria-deploy" -f $env:USERPROFILE\.ssh\aetheria_deploy
```

完成後會產生：
- 私鑰：`~/.ssh/aetheria_deploy`
- 公鑰：`~/.ssh/aetheria_deploy.pub`

### 2. 將 SSH 私鑰加入 GitHub Secrets

1. **取得 SSH 私鑰內容**：
   ```powershell
   cat $env:USERPROFILE\.ssh\aetheria_deploy
   ```
   複製完整輸出（包含 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）

2. **加入 GitHub Secrets**：
   - 前往 https://github.com/stevechen1112/Aetheria_Core/settings/secrets/actions
   - 點擊 **"New repository secret"**
   - Name: `SSH_PRIVATE_KEY`
   - Value: 貼上剛才複製的私鑰內容
   - 點擊 **"Add secret"**

### 3. 將 SSH 公鑰加入 Linode

把 `~/.ssh/aetheria_deploy.pub` 內容加到伺服器 `/root/.ssh/authorized_keys`：

```powershell
type $env:USERPROFILE\.ssh\aetheria_deploy.pub
```

在 Linode 上執行：

```bash
echo "<貼上公鑰內容>" >> /root/.ssh/authorized_keys
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

### 4. 測試自動部署

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

### 5. 監控部署狀態

- 前往 https://github.com/stevechen1112/Aetheria_Core/actions
- 查看最新的 workflow run
- 可即時查看部署日誌

---

## 🔍 故障排除

### 問題：SSH 連接失敗

**解決方法**：
1. 確認私鑰有正確加入 `SSH_PRIVATE_KEY`
2. 確認 GitHub Actions runner 可以連線到 172.237.6.53:22

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
2. 更新後端代碼（/root/Aetheria_Core）
3. 安裝 Python 依賴
4. 更新前端代碼（/opt/aetheria）
5. 安裝前端依賴並建置
6. 重啟 systemd 服務（aetheria.service）

### 環境變數
目前無需額外環境變數，伺服器已有 `.env` 文件。

如需更新伺服器環境變數，需手動 SSH 登入修改 `/root/Aetheria_Core/.env`。

---

## ✅ 完成確認

設定完成後，您應該能夠：
- ✅ 推送代碼到 GitHub 自動觸發部署
- ✅ 在 Actions 頁面看到部署進度
- ✅ 部署完成後檢查健康狀態：http://172.237.6.53:5001/health
