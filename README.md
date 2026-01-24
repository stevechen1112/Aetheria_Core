# Aetheria Core - 超個人化 LifeOS 命理分析系統

> **AI 驅動的雙核心命理分析引擎** | 紫微斗數 + 八字命理 | 基於 Gemini 3 Flash Preview

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-3%20Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()

## 📖 專案簡介

Aetheria Core 是一個結合傳統命理智慧與現代 AI 技術的智能分析系統。**v1.3.0 起支持紫微斗數與八字命理雙系統**，提供深度、準確且具洞察力的命理分析。

### 三種使用模式

- **模式 1：紫微斗數單獨分析** - 完整的紫微命盤排盤、分析、運勢、合盤、擇日功能
- **模式 2：八字命理單獨分析** - 四柱排盤、十神分析、大運推算、流年運勢
- **模式 3：交叉驗證分析** - 紫微與八字雙重驗證，提供更精準的命理判斷

### 核心理念

- **雙系統驗證**：紫微斗數與八字命理交叉驗證，提高準確度
- **LLM-First 策略**：充分發揮大型語言模型在複雜推理與自然語言生成上的優勢
- **結構化提取**：確保 AI 輸出符合命理學術規範
- **定盤鎖定**：防止重複分析帶來的不一致性
- **漸進式功能**：從基礎分析到進階合盤、擇日等全方位服務

---

## ✨ 功能特性

### 核心功能

#### 1. 命盤分析 (Chart Analysis)
- **晚子時判定**：自動處理 23:00-01:00 跨日排盤邏輯
- **結構化提取**：自動提取命宮、十二宮位、主星、四化、格局等關鍵資訊
- **深度解讀**：涵蓋性格特質、事業運勢、財運分析、感情婚姻等多維度分析
- **輸出長度**：2500-3500 字專業分析報告

#### 2. 定盤系統 (Chart Locking)
- **永久鎖定**：首次分析後鎖定命盤結構，確保一致性
- **版本控制**：完整保存原始分析內容與提取結果
- **防止漂移**：避免 LLM 多次分析產生的不一致問題

#### 3. 流年運勢 (Fortune Analysis)
- **年度運勢**：針對特定年份提供詳細運勢分析
- **月度細分**：每月運勢走向與關鍵時間點
- **決策建議**：基於流年命盤提供具體行動建議
- **輸出長度**：2000-3000 字年度運勢報告

### 進階功能

#### 4. 合盤分析 (Synastry Analysis)
- **婚配合盤**：8 維度深度分析（2500-3000 字）
  - 性格契合度、價值觀匹配、情感模式、事業互動
  - 財務觀念、家庭角色、溝通方式、穩定性評估
- **合夥分析**：7 維度事業合盤（2000-2500 字）
  - 能力互補、角色分工、財務規劃、風險管理
  - 股權建議、決策機制、成長策略
- **快速評估**：5 分鐘快速合盤（500-800 字）
  - 綜合評分、三大優勢、三大挑戰、關鍵建議

#### 5. 擇日功能 (Date Selection)
- **婚嫁擇日**：精選 Top 10 吉日（3000-4000 字）
  - 儀式時辰、風水方位、家族協調、禁忌事項
- **開業擇日**：行業專屬擇日（2500-3500 字）
  - 行業分析、財神方位、宣傳時機、開業儀式
- **搬家擇日**：入宅吉日選擇（2500-3500 字）
  - 家庭成員入宅順序、床位安置、風水佈局、安神儀式

### 八字命理系統 (v1.3.0 新增)

#### 6. 八字排盤 (BaZi Calculation)
- **四柱計算**：年柱、月柱、日柱、時柱精準排盤
- **真太陽時修正**：基於經度的時間校正（可選）
- **十神分析**：完整的十神系統（比肩、劫財、食神、傷官等）
- **大運推算**：10 步大運，每步 10 年運程
- **用神判斷**：用神、喜神、忌神自動分析
- **納音五行**：60 甲子納音配置

#### 7. 八字命理分析 (BaZi Analysis)
- **命格總論**：四柱組合、格局層次、五行配置（500-700 字）
- **性格特質**：性格傾向、處世風格、思維模式（400-600 字）
- **事業財運**：職業方向、財運狀況、求財方式（600-800 字）
- **婚姻感情**：婚緣早晚、配偶特點、感情模式（500-700 字）
- **健康狀況**：體質分析、易發疾病、養生建議（300-500 字）
- **大運流年**：當前大運吉凶、未來運勢走向（600-800 字）
- **開運建議**：五行開運、方位顏色、趨吉避凶（400-600 字）

#### 8. 八字流年運勢 (BaZi Fortune)
- **整體運勢**：流年干支作用、運勢評分（300-400 字）
- **事業財運**：工作發展、財運機會、貴人小人（400-500 字）
- **感情婚姻**：桃花運勢、感情穩定性、經營建議（300-400 字）
- **健康注意**：易發健康問題、養生保健（200-300 字）
- **月份吉凶**：12 個月吉凶預測（400-500 字）
- **趨吉避凶**：開運建議、風險規避、決策時機（300-400 字）

#### 9. 交叉驗證分析 (Cross Validation)
- **命格層次驗證**：紫微與八字格局對照，綜合評估（400-500 字）
- **性格特質對照**：兩套體系性格描述共鳴點分析（500-600 字）
- **事業財運交叉分析**：官祿宮與財官印食雙重驗證（600-800 字）
- **婚姻感情雙重驗證**：夫妻宮與配偶星互補信息（500-700 字）
- **大運流年對照**：紫微大限與八字大運時間點比對（600-700 字）
- **健康狀況驗證**：疾厄宮與五行偏枯一致性（300-400 字）
- **綜合研判與建議**：一致性結論、分歧點分析、決策依據（700-900 字）
- **標註系統**：
  - ✓✓✓ 高度可信（兩套體系一致）
  - ⚠️ 需觀察（存在分歧）
  - ↔️ 互補參考（不同角度補充）

---

## 🚀 快速開始

### 系統需求

- Python 3.9+
- Google Gemini API Key
- 約 50MB 磁碟空間

### 安裝步驟

#### 1. 下載專案

```powershell
cd C:\Users\User\Desktop
git clone <repository_url> Aetheria_Core
cd Aetheria_Core
```

#### 2. 安裝依賴

```powershell
pip install -r requirements.txt
```

所需套件：
- `google-generativeai` - Gemini API 客戶端
- `Flask` - API 服務框架
- `python-dotenv` - 環境變數管理

#### 3. 設定 API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/apikey) 獲取 API Key
2. 複製 `.env.example` 為 `.env`
3. 填入您的 API Key：

```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-3-flash-preview
TEMPERATURE=0.4
MAX_OUTPUT_TOKENS=8192
```

#### 4. 啟動 API 服務

```powershell
# 方式 1: 直接運行
python api_server.py

# 方式 2: 背景運行（推薦）
$null = Start-Job -Name AetheriaAPI -ScriptBlock { 
    Set-Location C:\Users\User\Desktop\Aetheria_Core
    python api_server.py 
}
```

驗證服務：
```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
```

---

## 📡 API 文檔

### 基礎端點

#### 1. 健康檢查

```http
GET /health
```

**回應：**
```json
{
  "service": "Aetheria Chart Locking API",
  "status": "ok"
}
```

#### 2. 初始命盤分析

```http
POST /api/chart/initial-analysis
Content-Type: application/json

{
  "user_id": "user_001",
  "birth_date": "農曆68年9月23日",
  "birth_time": "23:58",
  "birth_location": "台灣彰化市",
  "gender": "男"
}
```

**回應：**
```json
{
  "user_id": "user_001",
  "analysis": "完整命盤分析內容（2500-3500字）",
  "chart_structure": {
    "命宮": {...},
    "格局": [...],
    "十二宮": {...},
    "四化": {...}
  },
  "extracted_successfully": true
}
```

#### 3. 鎖定命盤

```http
POST /api/chart/lock
Content-Type: application/json

{
  "user_id": "user_001"
}
```

#### 4. 查詢鎖定狀態

```http
GET /api/chart/get-lock?user_id=user_001
```

### 流年運勢端點

#### 5. 流年運勢分析

```http
POST /api/fortune/annual
Content-Type: application/json

{
  "user_id": "user_001",
  "target_year": 2026
}
```

**回應：** 2000-3000 字年度運勢分析

#### 6. 流年運勢（已鎖定用戶）

```http
POST /api/fortune/annual-locked
Content-Type: application/json

{
  "user_id": "user_001",
  "target_year": 2026
}
```

### 合盤分析端點

#### 7. 婚配合盤

```http
POST /api/synastry/marriage
Content-Type: application/json

{
  "user_id_a": "user_001",
  "user_id_b": "user_002"
}
```

**回應：** 2500-3000 字婚配分析（8 維度）

#### 8. 合夥關係分析

```http
POST /api/synastry/partnership
Content-Type: application/json

{
  "user_id_a": "user_001",
  "user_id_b": "user_002",
  "partnership_context": "計劃合作開設 AI 命理諮詢工作室，預計投資 500 萬"
}
```

**回應：** 2000-2500 字合夥分析（7 維度 + 股權建議）

#### 9. 快速合盤評估

```http
POST /api/synastry/quick
Content-Type: application/json

{
  "user_id_a": "user_001",
  "user_id_b": "user_002",
  "relationship_type": "婚配"
}
```

**回應：** 500-800 字快速評估

### 擇日功能端點

#### 10. 婚嫁擇日

```http
POST /api/date-selection/marriage
Content-Type: application/json

{
  "groom_id": "user_001",
  "bride_id": "user_002",
  "target_year": 2026,
  "preferences": {
    "preferred_months": [5, 10],
    "weekend_only": true
  }
}
```

**回應：** 3000-4000 字擇日分析（Top 10 吉日）

#### 11. 開業擇日

```http
POST /api/date-selection/business
Content-Type: application/json

{
  "user_id": "user_001",
  "target_year": 2026,
  "business_type": "AI 命理諮詢工作室",
  "preferences": {
    "preferred_months": [3, 4, 9],
    "weekend_only": true
  }
}
```

**回應：** 2500-3500 字擇日分析

#### 12. 搬家擇日

```http
POST /api/date-selection/moving
Content-Type: application/json

{
  "user_id": "user_001",
  "target_year": 2026,
  "family_members": [
    {"relation": "本人", "user_id": "user_001"},
    {"relation": "配偶", "user_id": "user_002"}
  ],
  "preferences": {
    "preferred_months": [2, 8],
    "weekend_only": true
  }
}
```

**回應：** 2500-3500 字擇日分析

---

### 八字命理端點 (v1.3.0 新增)

#### 13. 八字排盤計算

```http
POST /api/bazi/calculate
Content-Type: application/json

{
  "year": 1979,
  "month": 10,
  "day": 11,
  "hour": 23,
  "minute": 58,
  "gender": "male",
  "longitude": 120.52,
  "use_apparent_solar_time": true
}
```

**回應：**
```json
{
  "status": "success",
  "data": {
    "四柱": {
      "年柱": {"天干": "己", "地支": "未", "納音": "天上火"},
      "月柱": {"天干": "甲", "地支": "戌", "納音": "山頭火"},
      "日柱": {"天干": "壬", "地支": "子", "納音": "桑柘木"},
      "時柱": {"天干": "甲", "地支": "子", "納音": "海中金"}
    },
    "日主": {"天干": "壬", "五行": "水"},
    "強弱": {"結論": "身弱", "評分": 20},
    "用神": {"用神": ["金", "水"], "喜神": ["金", "水"], "忌神": ["土", "火"]},
    "大運": [...]
  }
}
```

#### 14. 八字命理分析

```http
POST /api/bazi/analysis
Content-Type: application/json

{
  "user_id": "user_001",
  "year": 1979,
  "month": 10,
  "day": 11,
  "hour": 23,
  "minute": 58,
  "gender": "male",
  "longitude": 120.52,
  "use_apparent_solar_time": true
}
```

**回應：** 3500-5000 字完整八字分析
- 命格總論、性格特質、事業財運、婚姻感情
- 健康狀況、大運流年、開運建議

#### 15. 八字流年運勢

```http
POST /api/bazi/fortune
Content-Type: application/json

{
  "user_id": "user_001",
  "year": 1979,
  "month": 10,
  "day": 11,
  "hour": 23,
  "gender": "male",
  "query_year": 2024,
  "query_month": null,
  "longitude": 120.52
}
```

**回應：** 2000-3000 字流年運勢分析
- 整體運勢評分、事業財運、感情婚姻
- 健康注意、月份吉凶、趨吉避凶建議

#### 16. 紫微+八字交叉驗證

```http
POST /api/cross-validation/ziwei-bazi
Content-Type: application/json

{
  "user_id": "user_001",
  "year": 1979,
  "month": 10,
  "day": 11,
  "hour": 23,
  "minute": 58,
  "gender": "male",
  "longitude": 120.52,
  "use_apparent_solar_time": true
}
```

**回應：** 4000-6000 字交叉驗證分析
- 命格層次驗證、性格特質對照、事業財運交叉分析
- 婚姻感情雙重驗證、大運流年對照、綜合研判與建議
- 包含紫微命盤摘要、八字命盤摘要、一致性標註

**注意：** 此端點需要用戶已鎖定紫微命盤

---

## 🧪 測試指南

### 方式 1：互動式測試

```powershell
python test_advanced.py
```

提供選單介面，可逐一測試各項功能：
1. 婚配合盤分析
2. 合夥關係分析
3. 快速合盤評估
4. 婚嫁擇日
5. 開業擇日
6. 搬家入宅擇日
7. 執行所有測試

### 方式 2：自動化測試

```powershell
python test_advanced_auto.py
```

自動執行 3 個核心測試：
- 快速合盤評估（~20 秒）
- 開業擇日（~50 秒）
- 合夥關係分析（~65 秒）

### 測試用戶

系統預設包含兩個測試用戶：

**test_user_001（男）**
- 出生：農曆68年9月23日 23:58
- 地點：台灣彰化市
- 命盤：陽梁昌祿格

**test_user_002（女）**
- 出生：農曆70年5月15日 14:30
- 地點：台灣台北市
- 命盤：天同坐命、紫貪在官祿

---

## ⚙️ 技術架構

### 系統架構圖

```
┌─────────────────────────────────────────────────┐
│                  Client Layer                    │
│  (REST API Calls / Python Scripts / Web Apps)   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Flask API Server                    │
│              (api_server.py)                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Endpoints (13 routes)                   │   │
│  │  - Chart Analysis                        │   │
│  │  - Fortune Analysis                      │   │
│  │  - Synastry Analysis                     │   │
│  │  - Date Selection                        │   │
│  └──────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌───▼────┐
│Gemini │   │ Chart   │   │Fortune │
│  API  │   │Extractor│   │ Teller │
└───────┘   └────┬────┘   └────────┘
                 │
           ┌─────▼─────┐
           │   Data    │
           │  Storage  │
           │chart_locks│
           │.json      │
           └───────────┘
```

### 核心模組

| 模組 | 檔案 | 說明 |
|------|------|------|
| **API 服務** | `api_server.py` | Flask API 主程式（13 端點） |
| **命盤提取** | `chart_extractor.py` | 結構化提取命盤資訊 |
| **流年運勢** | `fortune_teller.py` | 流年命盤計算與分析 |
| **Prompt 模板** | `fortune_prompts.py` | 流年運勢 Prompt |
| | `synastry_prompts.py` | 合盤分析 Prompt |
| | `date_selection_prompts.py` | 擇日功能 Prompt |
| **資料存儲** | `data/chart_locks.json` | 鎖定命盤資料庫 |

### Prompt 工程策略

1. **結構化輸出**：透過 Markdown 格式定義嚴格的輸出結構
2. **上下文注入**：將已鎖定的命盤結構注入 Prompt
3. **專業術語**：使用正統命理術語確保專業性
4. **範例驅動**：提供分析範例引導 LLM 輸出
5. **長度控制**：明確指定各段落字數要求

---

## 📊 效能指標

### 模型選擇：Gemini 3 Flash Preview ⭐

經過完整對比測試（2026/01/24），確認 **Gemini 3 Flash Preview** 為最佳選擇：

| 指標 | Flash Preview | Pro Preview | 差異 |
|------|---------------|-------------|------|
| **命盤分析速度** | 42.49s | 87.36s | **快 2.06x** |
| **流年運勢速度** | 35.72s | 61.89s | **快 1.73x** |
| **Token 用量** | 5,754 | 9,480 | **省 39%** |
| **結構完整度** | 3/4 | 3/4 | **相同** |
| **內容品質** | 優秀 | 優秀 | **相當** |
| **成本** | 低 | 高 | **省 30-40%** |

**結論**：Flash Preview 在速度、成本上全面領先，且品質完全相當於 Pro 版本。

### 典型回應時間

| 功能 | 平均時間 | Token 消耗 |
|------|----------|-----------|
| 命盤分析 | 40-50s | 5,000-6,000 |
| 流年運勢 | 35-45s | 5,000-6,500 |
| 快速合盤 | 20-25s | 3,000-4,000 |
| 婚配合盤 | 60-70s | 7,000-8,000 |
| 擇日分析 | 50-60s | 6,000-7,500 |

---

## 🛠️ 開發指南

### 專案結構

```
Aetheria_Core/
├── api_server.py              # Flask API 主程式
├── chart_extractor.py         # 命盤結構提取器
├── fortune_teller.py          # 流年運勢計算
├── fortune_prompts.py         # 流年 Prompt
├── synastry_prompts.py        # 合盤 Prompt
├── date_selection_prompts.py  # 擇日 Prompt
├── data/
│   └── chart_locks.json       # 命盤資料庫
├── test_advanced.py           # 互動式測試
├── test_advanced_auto.py      # 自動化測試
├── requirements.txt           # 依賴套件
├── .env                       # 環境變數（不提交）
├── .env.example               # 環境變數範本
├── README.md                  # 本檔案
├── README_TEST.md             # 測試指南
└── README_ADVANCED_TEST.md    # 進階測試指南
```

### 添加新功能

#### 1. 定義 Prompt

在對應的 `*_prompts.py` 檔案中添加新的 Prompt 模板：

```python
NEW_FEATURE_PROMPT = f"""
你是 Aetheria，專業的紫微斗數分析師。

請針對以下命盤進行【新功能】分析：
{{chart_info}}

輸出要求：
1. 【分析維度1】（字數範圍）
2. 【分析維度2】（字數範圍）
...

總字數：XXXX-XXXX 字
"""
```

#### 2. 實作 API 端點

在 `api_server.py` 中添加新端點：

```python
@app.route('/api/new-feature', methods=['POST'])
def new_feature():
    data = request.get_json()
    user_id = data.get('user_id')
    
    # 載入鎖定命盤
    chart_data = chart_locker.load_chart(user_id)
    
    # 呼叫 Gemini
    prompt = NEW_FEATURE_PROMPT.format(chart_info=chart_data)
    response = model.generate_content(prompt)
    
    return jsonify({
        'user_id': user_id,
        'analysis': response.text
    })
```

#### 3. 添加測試

在 `test_advanced.py` 或創建新的測試檔案。

### 除錯技巧

#### 1. 檢查 API 健康狀態

```powershell
Invoke-RestMethod -Uri http://localhost:5000/health
```

#### 2. 查看 Job 狀態

```powershell
Get-Job -Name AetheriaAPI | Receive-Job
```

#### 3. 驗證環境變數

```powershell
python debug_config.py
```

#### 4. 測試 Gemini 連線

```powershell
python list_models.py
```

---

## 🔒 資料隱私與安全

### 資料存儲

- **本地存儲**：所有命盤資料存放於本地 `data/chart_locks.json`
- **不外傳**：除 Gemini API 分析外，資料不傳送至任何第三方
- **API Key 保護**：`.env` 檔案已加入 `.gitignore`

### API Key 安全

⚠️ **重要提醒**：
1. 不要將 `.env` 檔案提交至版本控制
2. 不要在公開場合分享 API Key
3. 定期輪換 API Key
4. 監控 API 使用量，防止濫用

---

## 📝 更新日誌

### v1.2.0 (2026-01-24)

**新功能：**
- ✅ 合盤分析系統（婚配、合夥、快速評估）
- ✅ 擇日功能（婚嫁、開業、搬家）
- ✅ 模型切換至 Gemini 3 Flash Preview
- ✅ 完整的 API 端點文檔

**優化：**
- ⚡ 分析速度提升 2x
- 💰 成本降低 30-40%
- 📊 添加效能監控

**測試：**
- ✅ 3/3 自動化測試通過
- ✅ 6 個進階功能全部驗證

### v1.1.0 (2026-01-23)

**新功能：**
- ✅ 流年運勢分析系統
- ✅ FortuneTeller 流年命盤計算
- ✅ 流年運勢 API 端點

**優化：**
- 🔄 定盤系統穩定性提升
- 📝 Prompt 工程優化

### v1.3.0 (2026-01-24) - 八字系統上線

**重大更新：雙核心系統**
- ✅ 八字命理排盤引擎（基於 sxtwl 庫）
- ✅ 四柱計算（年月日時）+ 真太陽時修正
- ✅ 十神分析（比肩、劫財、食神、傷官等）
- ✅ 大運推算（10 步大運，每步 10 年）
- ✅ 用神判斷（用神、喜神、忌神）
- ✅ 納音五行（60 甲子納音）
- ✅ 八字命理分析 AI Prompt（3500-5000 字）
- ✅ 八字流年運勢分析（2000-3000 字）
- ✅ 紫微+八字交叉驗證系統（4000-6000 字）
- ✅ 三種使用模式架構：紫微 / 八字 / 交叉驗證
- ✅ 4 個新增 API 端點
- ✅ 完整測試腳本（test_bazi_system.py, test_three_modes.py）

**技術改進：**
- 新增 bazi_calculator.py（480+ 行核心計算引擎）
- 新增 bazi_prompts.py（八字分析提示詞模板）
- API Server 新增八字路由組（/api/bazi/*, /api/cross-validation/*）
- Requirements.txt 新增 sxtwl>=2.0.7 依賴

### v1.0.0 (2026-01-22)

**初始版本：**
- ✅ 命盤分析功能
- ✅ 定盤鎖定系統
- ✅ ChartExtractor 結構化提取
- ✅ Flask API 基礎框架

---

## 🤝 貢獻指南

本專案目前為私有專案，暫不接受外部貢獻。

---

## 📄 授權

Copyright © 2026 Aetheria Team. All rights reserved.

本專案為私有專案，未經授權不得使用、複製或分發。

---

## 📞 聯絡方式

如有問題或建議，請透過以下方式聯絡：

- 📧 Email: [待補充]
- 💬 Discord: [待補充]
- 🐛 Issues: [待補充]

---

## 🌟 致謝

- **Google Gemini Team** - 提供強大的 AI 模型
- **Flask Community** - 優秀的 Web 框架
- **紫微斗數學術社群** - 傳統命理智慧傳承

---

**Built with ❤️ by Aetheria Team**

*最後更新：2026 年 1 月 24 日*
