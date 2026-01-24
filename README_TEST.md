# Aetheria 測試指南

## 🚀 快速開始

### 步驟 1：安裝依賴套件

```powershell
# 在專案目錄執行
pip install -r requirements.txt
```

如果沒有 pip，請先安裝 Python（建議 3.9 以上版本）。

---

### 步驟 2：設定 API Key

1. **取得 Gemini API Key**
   - 前往：https://aistudio.google.com/apikey
   - 登入 Google 帳號
   - 點選「Create API Key」
   - 複製產生的 API Key

2. **填入 .env 檔案**
   - 開啟專案目錄中的 `.env` 檔案
   - 找到這一行：
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
   - 將 `your_gemini_api_key_here` 替換成您剛才複製的 API Key
   - 儲存檔案

   **範例**：
   ```
   GEMINI_API_KEY=AIzaSyABC123def456GHI789jkl0MNOP
   ```

3. **安全提醒**
   - ⚠️ 不要將 `.env` 檔案上傳到 GitHub 或公開分享
   - `.gitignore` 已經設定會忽略此檔案

---

### 步驟 3：執行測試

```powershell
# 預設模式：執行預設測試案例（農曆68年9月23日）
python test_aetheria.py

# 互動模式：輸入您自己的出生資料
python test_aetheria.py -i

# 顯示說明
python test_aetheria.py --help
```

---

## 📊 測試流程說明

### 測試腳本會做什麼？

1. **環境檢查**
   - 確認 `.env` 檔案存在
   - 確認 API Key 已設定
   - 顯示配置資訊

2. **執行命理分析**
   - 使用 Gemini 3 Pro
   - 分析預設案例（農曆68年9月23日 23:58 台灣彰化男性）
   - 顯示完整命盤解讀

3. **準確性驗證**
   - 詢問您評分（1-5分）
   - 收集您的意見
   - 記錄到 `feedback_log.jsonl`

4. **儲存結果**
   - 完整分析結果存到 `test_result_*.txt`
   - 方便後續檢視與比對

---

## 📁 產生的檔案說明

| 檔案 | 說明 |
|------|------|
| `test_result_case_1_*.txt` | 測試案例的完整分析結果 |
| `feedback_log.jsonl` | 所有反饋記錄（JSON Lines 格式） |
| `.env` | API Key 配置（請勿分享） |

---

## 🧪 測試案例說明

### Case 1：農曆68年9月23日（標準案例）

這是一個真實驗證過的案例：
- 出生：農曆68年9月23日 23:58
- 地點：台灣彰化市
- 性別：男
- 驗證：用戶反饋「性格幾乎符合」

**測試目標**：
- 驗證晚子時（23:58）的判定邏輯
- 確認「日月並明」格局分析
- 測試創業建議的準確性

---

## ⚙️ 進階配置

### 調整模型參數

編輯 `.env` 檔案：

```env
# 模型選擇
MODEL_NAME=gemini-3-pro-preview       # 最強推理
# MODEL_NAME=gemini-3-flash-preview   # 較快速

# 溫度（創造性）
TEMPERATURE=0.4    # 0.0-1.0，越低越保守

# 最大輸出長度
MAX_OUTPUT_TOKENS=8192

# 除錯模式
DEBUG_MODE=true    # 顯示更多技術細節
```

### 模型選擇建議

**✨ 测试结论（2026/01/24）**：经过完整对比测试，**Gemini 3 Flash Preview 品质完全相当于 Pro 版本**，且速度快 2x，成本节省 30-40%。

| 模型 | 優點 | 缺點 | 適用場景 |
|------|------|------|----------|
| `gemini-3-flash-preview` | **速度快 2x、成本低、品質相當** | 無明顯缺點 | **所有場景推薦** ⭐ |
| `gemini-3-pro-preview` | 推理強、準確 | 較慢、較貴 | 特殊需求場景 |
| `gemini-2.5-pro` | 穩定版 | 可能較舊 | 生產環境 |

---

## 🐛 常見問題排除

### Q1：顯示 "API_KEY_INVALID"

**原因**：API Key 錯誤或未啟用

**解決方式**：
1. 重新檢查 `.env` 中的 API Key 是否正確
2. 確認沒有多餘的空格或換行
3. 前往 https://aistudio.google.com/apikey 確認 Key 狀態

---

### Q2：顯示 "QUOTA_EXCEEDED"

**原因**：API 配額用完

**解決方式**：
1. Gemini 有免費額度，可能已用完
2. 前往 https://console.cloud.google.com/ 檢查
3. 等待配額重置（通常每日重置）

---

### Q3：顯示 "MODEL_NOT_FOUND"

**原因**：模型名稱錯誤

**解決方式**：
修改 `.env` 的 `MODEL_NAME` 為以下任一值：
- `gemini-3-pro-preview`
- `gemini-3-flash-preview`
- `gemini-2.5-pro`

---

### Q4：分析結果很短或不完整

**原因**：`MAX_OUTPUT_TOKENS` 設定太小

**解決方式**：
在 `.env` 中調整：
```env
MAX_OUTPUT_TOKENS=8192  # 增加到 8192 或更高
```

---

### Q5：安裝 google-generativeai 失敗

**原因**：Python 版本太舊或網路問題

**解決方式**：
```powershell
# 升級 pip
python -m pip install --upgrade pip

# 重新安裝
pip install google-generativeai --upgrade

# 如果還是失敗，檢查 Python 版本（需要 3.9+）
python --version
```

---

## 📈 評估標準

### 準確性評分標準

| 分數 | 標準 | 行動 |
|------|------|------|
| 5 分 | 非常準確（像您的 Gemini 3 Pro 體驗） | ✅ 可以進入下一階段開發 |
| 4 分 | 大部分符合，少數細節需調整 | ✅ 微調 prompt 後可用 |
| 3 分 | 還可以，但有明顯缺陷 | ⚠️ 需要優化 prompt 或調整參數 |
| 2 分 | 有些不符合 | ❌ 重新檢視系統提示詞 |
| 1 分 | 完全不符合 | ❌ 檢查是否有技術問題 |

### 目標

收集 **50-100 個測試案例**，平均分數達到 **4.0 以上**，即可確認 LLM-First 策略可行。

---

## 🎯 下一步

### 如果測試成功（評分 >= 4.0）

1. **收集更多案例**
   - 使用 `-i` 互動模式測試更多真實案例
   - 邀請朋友提供出生資料並驗證

2. **開發其他功能**
   - 多輪對話（記住之前的命盤）
   - 流年運勢分析
   - 決策支援模組

3. **準備產品化**
   - 建立 Web 介面
   - 設計用戶註冊/登入
   - 實施快取機制降低成本

### 如果測試失敗（評分 < 4.0）

1. **分析失敗原因**
   - 檢視 `test_result_*.txt`
   - 哪個部分不準確？（格局判定 vs 性格描述 vs 建議）

2. **調整策略**
   - 修改 `test_aetheria.py` 中的系統提示詞
   - 降低 `TEMPERATURE`（更保守）
   - 增加更多範例在 prompt 中

3. **重新測試**
   - 刪除 `feedback_log.jsonl`
   - 重新執行測試
   - 比對改善程度

---

## 📞 需要協助？

如果遇到問題，請提供以下資訊：
1. 錯誤訊息完整內容
2. `.env` 的配置（隱藏 API Key）
3. `test_result_*.txt` 的內容
4. Python 版本：`python --version`

---

**祝測試順利！🌟**
