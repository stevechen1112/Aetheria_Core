# Aetheria Core - 超個人化 LifeOS 命理分析系統

> **AI 驅動的六大命理分析引擎** | 紫微斗數 + 八字命理 + 西洋占星 + 靈數學 + 姓名學 + 塔羅牌  
> 文字諮詢：Gemini 2.0 Flash | 語音對話：OpenAI Realtime API (WebRTC)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Realtime%20API-412991.svg)](https://platform.openai.com/)
[![License](https://img.shields.io/badge/License-GPL%20v2-red.svg)]()
[![Version](https://img.shields.io/badge/Version-v1.9.3-brightgreen.svg)]()

---

## 📋 目錄

1. [快速開始](#-快速開始)
2. [系統架構](#-系統架構)
3. [環境設定](#-環境設定)
4. [AI 對話系統](#-ai-對話系統)
5. [六大命理系統](#-六大命理系統)
6. [API 端點完整清單](#-api-端點完整清單)
7. [專案結構](#-專案結構)
8. [開發指南](#-開發指南)
9. [常見問題排解](#-常見問題排解)
10. [版本歷史](#-版本歷史)

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 建立虛擬環境（強烈建議）
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 文件於專案根目錄：

```env
# ===== 必要的 API Keys =====
GEMINI_API_KEY=your_gemini_api_key      # Google AI - 文字對話用
OPENAI_API_KEY=your_openai_api_key      # OpenAI - 語音對話用

# ===== 模型設定 =====
MODEL_NAME=gemini-2.0-flash             # 文字對話模型（勿更改）
TEMPERATURE=0.4                          # 生成溫度 (0.0-1.0)
MAX_OUTPUT_TOKENS=8192                   # 最大輸出長度

# ===== 可選設定 =====
DEBUG_MODE=false
```

### 3. 啟動後端服務

```bash
# 方法一：使用 run.py（推薦）
python run.py

# 方法二：直接啟動
python src/api/server.py
```

API 服務將運行於 **http://localhost:5001**

### 4. 啟動前端服務

```bash
cd webapp
npm install    # 首次執行
npm run dev -- --host
```

前端將運行於 **http://localhost:5173**

### 5. 驗證服務狀態

```bash
# 健康檢查
curl http://localhost:5001/health

# 預期回應
{"status":"healthy","version":"1.9.3"}
```

---

## 🏗 系統架構

### 整體架構圖

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                         │
│                       http://localhost:5173                          │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    VoiceChat.jsx 元件                            ││
│  │  ┌─────────────────┐              ┌─────────────────────────┐   ││
│  │  │  💬 文字對話模式  │              │  🎙️ 語音對話模式         │   ││
│  │  │  輸入框 + 傳送   │              │  WebRTC + 麥克風        │   ││
│  │  └────────┬────────┘              └───────────┬─────────────┘   ││
│  └───────────┼───────────────────────────────────┼─────────────────┘│
│              │                                   │                   │
├──────────────┼───────────────────────────────────┼───────────────────┤
│              │        HTTP / WebRTC              │                   │
│              ▼                                   ▼                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                  Flask API Server (Port 5001)                    ││
│  │                      src/api/server.py                           ││
│  │  ┌──────────────────┐         ┌────────────────────────────┐    ││
│  │  │ POST /api/chat   │         │ POST /api/voice/session    │    ││
│  │  │     /consult     │         │ (SDP Exchange)             │    ││
│  │  └────────┬─────────┘         └──────────────┬─────────────┘    ││
│  │           │                                   │                  ││
│  │           ▼                                   ▼                  ││
│  │  ┌──────────────────┐         ┌────────────────────────────┐    ││
│  │  │   Gemini 2.0     │         │   OpenAI Realtime API      │    ││
│  │  │   Flash API      │         │   (gpt-4o-realtime-preview)│    ││
│  │  │   文字生成        │         │   WebRTC 語音串流           │    ││
│  │  └──────────────────┘         └────────────────────────────┘    ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                       六大命理計算模組 (src/calculators/)             │
│  ┌───────────┬───────────┬───────────┬───────────┬───────────┬─────┐│
│  │  紫微斗數  │  八字命理  │  西洋占星  │   靈數學   │   姓名學   │塔羅牌││
│  │  ziwei.py │  bazi.py  │astrology.py│numerology │  name.py  │tarot││
│  │           │           │            │    .py    │           │ .py ││
│  └───────────┴───────────┴───────────┴───────────┴───────────┴─────┘│
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                           資料層                                      │
│  ┌────────────────────────────┐  ┌────────────────────────────────┐ │
│  │   SQLite (aetheria.db)     │  │   JSON 資料檔 (data/)          │ │
│  │   - 用戶資料               │  │   - tarot_cards.json           │ │
│  │   - 命盤鎖定               │  │   - numerology_data.json       │ │
│  │   - 對話歷史               │  │   - name_analysis.json         │ │
│  │   - 分析報告               │  │   - chart_locks.json           │ │
│  └────────────────────────────┘  └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### 核心技術棧

| 層級 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **前端** | React + Vite | 7.3+ | 現代化 SPA，支援語音/文字混合介面 |
| **後端** | Flask | 3.0+ | Python Web 框架，RESTful API |
| **文字 AI** | Gemini 2.0 Flash | - | Google AI，命理分析與文字諮詢 |
| **語音 AI** | OpenAI Realtime API | - | WebRTC 即時雙向語音對話 |
| **資料庫** | SQLite | 3.x | 輕量級嵌入式資料庫 |
| **星曆計算** | Swiss Ephemeris | - | 專業天文計算（< 0.5° 誤差）|

---

## ⚙ 環境設定

### API Keys 取得方式

#### 1. Gemini API Key（文字對話必要）

```
1. 前往 Google AI Studio：https://aistudio.google.com/
2. 建立專案或選擇現有專案
3. 在 API Keys 頁面建立新的 Key
4. 複製 Key（格式：AIzaSy...）
```

#### 2. OpenAI API Key（語音對話必要）

```
1. 前往 OpenAI Platform：https://platform.openai.com/
2. 登入並前往 API Keys 頁面
3. 建立新的 Secret Key
4. 複製 Key（格式：sk-proj-...）

⚠️ 注意：需要有 Realtime API 的使用權限
⚠️ 確認帳戶有足夠的使用額度
```

### 環境變數完整說明

| 變數名 | 必要性 | 預設值 | 說明 |
|--------|--------|--------|------|
| `GEMINI_API_KEY` | ✅ 必要 | - | Google AI API Key |
| `OPENAI_API_KEY` | ✅ 必要 | - | OpenAI API Key（Realtime API） |
| `MODEL_NAME` | 可選 | `gemini-2.0-flash` | Gemini 模型名稱 |
| `TEMPERATURE` | 可選 | `0.4` | 生成溫度 (0.0-1.0) |
| `MAX_OUTPUT_TOKENS` | 可選 | `8192` | 最大輸出 token 數 |
| `DEBUG_MODE` | 可選 | `false` | 開啟詳細日誌 |

---

## 🎙 AI 對話系統

本系統整合 **雙 AI 引擎**，分別處理文字和語音對話：

### 文字對話模式（Gemini 2.0 Flash）

**流程**：
```
用戶輸入文字 → POST /api/chat/consult → Flask → Gemini API → 文字回覆
```

**特點**：
- 使用 Google Gemini 2.0 Flash 模型
- 回覆長度：200-400 字
- 風格：口語化、像朋友聊天、會引用命盤資料
- 支援對話歷史記憶

**Request 範例**：
```json
POST /api/chat/consult
{
  "message": "我 2026 年適合換工作嗎？",
  "session_id": "optional_session_id",
  "voice_mode": false
}
```

**Response 範例**：
```json
{
  "status": "success",
  "message": "根據你的八字，2026 年丙午年，火氣旺盛...",
  "session_id": "abc123"
}
```

### 語音對話模式（OpenAI Realtime API）

**流程**：
```
用戶麥克風 → WebRTC PeerConnection → SDP Exchange → OpenAI Realtime → 語音回覆
```

**連線步驟**：
1. 前端建立 `RTCPeerConnection`
2. 建立 SDP Offer（包含音訊軌道）
3. POST `/api/voice/session` 傳送 SDP
4. 後端呼叫 OpenAI `/v1/realtime/calls` 端點
5. 返回 SDP Answer
6. 建立雙向語音通道

**Request 範例**：
```json
POST /api/voice/session
{
  "sdp": "v=0\r\no=- 0 0 IN IP4 127.0.0.1\r\n...",
  "voice": "sage"
}
```

**Response 範例**：
```json
{
  "status": "success",
  "sdp": "v=0\r\no=- 0 0 IN IP4 0.0.0.0\r\n...",
  "session_id": "sess_xxx"
}
```

### 可用語音選項

取得方式：`GET /api/voice/voices`

| Voice ID | 名稱 | 風格描述 | 建議用途 |
|----------|------|----------|----------|
| `alloy` | Alloy | 中性平衡 | 通用場景 ⭐ 推薦 |
| `ash` | Ash | 溫暖柔和 | 輕鬆諮詢 |
| `ballad` | Ballad | 富有情感 | 情感話題 |
| `coral` | Coral | 清晰明亮 | 資訊傳達 |
| `echo` | Echo | 穩重低沉 | 專業諮詢 |
| `sage` | Sage | 智慧沉穩 | 命理諮詢 ⭐ 推薦 |
| `shimmer` | Shimmer | 活潑輕快 | 年輕用戶 |
| `verse` | Verse | 文藝氣質 | 文化話題 |

### ⚠️ 語音功能技術細節（重要）

**SDP 格式要求**：
- SDP 協議要求每行以 `\r\n` 結尾
- **絕對不可以對 SDP 做 `.strip()` 處理**
- 若移除末尾換行符會導致 OpenAI 返回 502 錯誤

**正確的 SDP 處理（server.py）**：
```python
# ✅ 正確：保留原始格式
sdp = data.get('sdp') or ''

# ❌ 錯誤：會破壞 SDP 格式
sdp = (data.get('sdp') or '').strip()
```

**session_config 格式**：
```python
session_config = {
    'type': 'realtime',
    'model': 'gpt-4o-realtime-preview',
    'audio': {
        'output': {
            'voice': 'sage'  # 或其他語音
        }
    },
    'instructions': '你是一位專業的命理諮詢師...'
    # ⚠️ 不要加入 input_audio_transcription 參數
}
```

---

## 🔮 六大命理系統

### 1. 紫微斗數（Zi Wei Dou Shu）

**功能**：
- 命盤排盤（十二宮位、14主星、輔星）
- 命盤分析（性格、事業、財運、感情）
- 流年運勢（大限、流年、流月）
- 合盤分析（兩人關係）
- 擇日功能

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/ziwei/calculate` | POST | 排盤計算 |
| `/api/ziwei/analyze` | POST | 命盤分析 |
| `/api/ziwei/fortune` | POST | 流年運勢 |
| `/api/ziwei/synastry` | POST | 合盤分析 |
| `/api/ziwei/election` | POST | 擇日功能 |

### 2. 八字命理（Ba Zi）

**功能**：
- 四柱排盤（年柱、月柱、日柱、時柱）
- 十神分析（正官、七殺、正印...）
- 五行分析（金木水火土比例）
- 大運推算
- 流年運勢

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/bazi/calculate` | POST | 四柱排盤 |
| `/api/bazi/analysis` | POST | 八字分析 |
| `/api/bazi/fortune` | POST | 流年運勢 |

### 3. 西洋占星術（Western Astrology）

**功能**：
- 本命盤計算（行星位置、宮位、相位）
- 合盤分析（Synastry）
- 流年運勢（Transit）
- 事業發展分析

**技術**：使用 Swiss Ephemeris 進行精確天文計算

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/astrology/natal` | POST | 本命盤計算 |
| `/api/astrology/synastry` | POST | 合盤分析 |
| `/api/astrology/transit` | POST | 流年運勢 |
| `/api/astrology/career` | POST | 事業發展 |

### 4. 靈數學（Numerology）

**功能**：
- 生命靈數計算
- 流年運勢
- 相容性分析
- 完整個人檔案

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/numerology/calculate` | POST | 靈數計算 |
| `/api/numerology/fortune` | POST | 流年運勢 |
| `/api/numerology/compatibility` | POST | 相容性分析 |
| `/api/numerology/profile` | POST | 完整檔案 |
| `/api/numerology/reading` | POST | 靈數解讀 |

### 5. 姓名學（Name Analysis）

**功能**：
- 五格剖象法分析
- 81 數理吉凶
- 三才配置
- 姓名建議

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/name/analyze` | POST | 姓名分析 |
| `/api/name/suggest` | POST | 命名建議 |
| `/api/name/reading` | POST | 姓名解讀 |

### 6. 塔羅牌（Tarot）

**功能**：
- 多種牌陣（單牌、三牌、凱爾特十字...）
- 每日一牌
- 情境解讀
- 78 張完整牌組（大阿爾卡那 + 小阿爾卡那）

**API 端點**：
| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/tarot/draw` | POST | 抽牌 |
| `/api/tarot/reading` | POST | 牌陣解讀 |
| `/api/tarot/daily` | POST | 每日一牌 |
| `/api/tarot/cards` | GET | 取得牌組資訊 |

---

## 📡 API 端點完整清單

### 系統相關

| 端點 | 方法 | 認證 | 說明 |
|------|------|------|------|
| `/health` | GET | ❌ | 健康檢查 |
| `/api/system/status` | GET | ❌ | 系統狀態 |

### 認證系統

| 端點 | 方法 | 認證 | 說明 |
|------|------|------|------|
| `/api/auth/register` | POST | ❌ | 用戶註冊 |
| `/api/auth/login` | POST | ❌ | 用戶登入 |
| `/api/auth/me` | GET | ✅ | 取得用戶資訊 |
| `/api/auth/refresh` | POST | ✅ | 刷新 Token |

### AI 諮詢

| 端點 | 方法 | 認證 | 說明 |
|------|------|------|------|
| `/api/chat/consult` | POST | ✅ | 文字對話諮詢 |
| `/api/chat/sessions` | GET | ✅ | 取得對話列表 |
| `/api/chat/messages` | GET | ✅ | 取得對話歷史 |
| `/api/voice/session` | POST | ✅ | 建立語音會話 |
| `/api/voice/voices` | GET | ❌ | 取得可用語音 |

### 戰略側寫

| 端點 | 方法 | 認證 | 說明 |
|------|------|------|------|
| `/api/strategic/holographic-profile` | POST | ✅ | 全息生命圖譜 |
| `/api/strategic/birth-time-rectifier` | POST | ✅ | 生辰校正器 |
| `/api/strategic/relationship-ecosystem` | POST | ✅ | 關係生態位 |
| `/api/strategic/decision-sandbox` | POST | ✅ | 決策沙盒 |

### 命盤管理

| 端點 | 方法 | 認證 | 說明 |
|------|------|------|------|
| `/api/charts/lock` | POST | ✅ | 鎖定命盤 |
| `/api/charts/unlock` | POST | ✅ | 解鎖命盤 |
| `/api/charts/list` | GET | ✅ | 取得命盤列表 |

---

## 📁 專案結構

```
Aetheria_Core/
├── .env                          # 環境變數設定（不進版控）
├── run.py                        # 主程式進入點
├── requirements.txt              # Python 依賴
├── pytest.ini                    # 測試設定
├── aetheria.db                   # SQLite 資料庫
│
├── src/                          # 主要程式碼
│   ├── __init__.py
│   │
│   ├── api/
│   │   └── server.py            # ⭐ Flask API 伺服器（~6150 行）
│   │                             #    包含所有 API 端點
│   │                             #    語音/文字對話處理
│   │
│   ├── calculators/              # 命理計算模組
│   │   ├── __init__.py
│   │   ├── astrology.py         # 西洋占星計算
│   │   ├── bazi.py              # 八字命理計算
│   │   ├── chart_extractor.py   # 命盤資料提取
│   │   ├── fortune.py           # 運勢計算
│   │   ├── name.py              # 姓名學計算
│   │   ├── numerology.py        # 靈數學計算
│   │   └── tarot.py             # 塔羅牌計算
│   │
│   ├── prompts/                  # AI 提示詞模板
│   │   ├── __init__.py
│   │   ├── astrology.py         # 占星提示詞
│   │   ├── bazi.py              # 八字提示詞
│   │   ├── numerology.py        # 靈數提示詞
│   │   └── ...
│   │
│   └── utils/                    # 工具模組
│       ├── __init__.py
│       ├── database.py          # SQLite 資料庫操作
│       ├── gemini_client.py     # Gemini API 客戶端
│       ├── logger.py            # 日誌系統
│       └── errors.py            # 錯誤處理
│
├── webapp/                       # 前端應用（React + Vite）
│   ├── src/
│   │   ├── App.jsx              # 主應用元件
│   │   ├── VoiceChat.jsx        # ⭐ 語音/文字對話元件（~560 行）
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── data/                         # 靜態資料
│   ├── tarot_cards.json         # 塔羅牌資料（78 張）
│   ├── numerology_data.json     # 靈數資料
│   ├── name_analysis.json       # 姓名學資料
│   ├── chart_locks.json         # 命盤鎖定資料
│   └── users.json               # 用戶資料
│
├── docs/                         # 文件
│   ├── 01_Technical_Whitepaper.md          # 技術白皮書
│   ├── 04_Architecture_Decision_LLM_First.md # ⭐ 核心架構決策
│   ├── 05_Gemini_Prompt_Templates.md       # 提示詞設計
│   ├── 06_Chart_Locking_System.md          # 定盤系統
│   └── ...
│
├── tests/                        # 測試檔案
│   ├── conftest.py              # pytest 設定
│   ├── test_api_health.py       # API 健康測試
│   ├── test_bazi.py             # 八字測試
│   ├── test_astrology.py        # 占星測試
│   └── ...
│
├── logs/                         # 日誌檔案
│   └── aetheria_YYYYMMDD.log
│
└── scripts/                      # 工具腳本
    ├── profile_*.py             # 側寫腳本
    ├── lock_*.py                # 命盤鎖定腳本
    └── ...
```

### 核心檔案說明

| 檔案 | 行數 | 職責 |
|------|------|------|
| `src/api/server.py` | ~6150 | 所有 API 端點、語音/文字對話、認證邏輯 |
| `webapp/src/VoiceChat.jsx` | ~560 | 語音對話前端元件（WebRTC 實作） |
| `src/utils/gemini_client.py` | ~100 | Gemini API 封裝，模型設定 |
| `src/utils/database.py` | ~500 | SQLite CRUD 操作 |
| `src/calculators/bazi.py` | ~800 | 八字計算核心邏輯 |
| `src/calculators/astrology.py` | ~600 | 占星計算（Swiss Ephemeris） |

---

## 🔧 開發指南

### 本地開發流程

```bash
# 1. 啟動 API 伺服器（會自動重載）
python run.py

# 2. 啟動前端開發伺服器
cd webapp
npm run dev -- --host

# 3. 執行測試
pytest tests/ -v

# 4. 執行特定測試
pytest tests/test_bazi.py -v
```

### 新增 API 端點

在 `src/api/server.py` 中新增：

```python
@app.route('/api/your-endpoint', methods=['POST'])
def your_endpoint():
    """
    你的 API 說明
    ---
    參數：
        - param1: 說明
    回傳：
        - data: 回傳資料
    """
    # 需要認證的端點
    user_id = require_auth_user_id()
    
    # 取得請求資料
    data = request.json or {}
    param1 = data.get('param1', 'default')
    
    # 你的邏輯
    result = process_something(param1)
    
    # 返回結果
    return jsonify({
        'status': 'success',
        'data': result
    })
```

### 新增命理計算模組

1. 在 `src/calculators/` 建立新模組：
   ```python
   # src/calculators/your_system.py
   class YourSystemCalculator:
       def calculate(self, birth_data):
           # 計算邏輯
           return result
   ```

2. 在 `src/prompts/` 建立提示詞：
   ```python
   # src/prompts/your_system.py
   def get_analysis_prompt(data):
       return f"分析以下資料：{data}"
   ```

3. 在 `server.py` 新增 API 端點

### 日誌與除錯

```bash
# 查看即時日誌
Get-Content logs/aetheria_*.log -Tail 100 -Wait

# 檢查特定錯誤
Select-String -Path logs/*.log -Pattern "ERROR"

# 測試 API 端點
curl -X POST http://localhost:5001/api/bazi/calculate \
  -H "Content-Type: application/json" \
  -d '{"birth_date":"1990-01-15","birth_time":"12:00"}'
```

---

## ❓ 常見問題排解

### Q1: 語音對話顯示 502 Bad Gateway

**症狀**：點擊語音按鈕後出現錯誤

**可能原因**：
1. `OPENAI_API_KEY` 未設定或無效
2. SDP 格式被破壞（`.strip()` 問題）
3. session_config 包含不支援的參數

**診斷步驟**：
```bash
# 1. 檢查 API Key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:20])"

# 2. 測試 OpenAI API 連線
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('OPENAI_API_KEY')
r = requests.get('https://api.openai.com/v1/models', 
                 headers={'Authorization': f'Bearer {key}'})
print(f'狀態: {r.status_code}')
"
```

**解決方法**：
- 確認 `server.py` 中 SDP 處理不使用 `.strip()`
- 確認 session_config 不包含 `input_audio_transcription`

### Q2: 文字對話顯示「無法生成回覆」

**可能原因**：
1. `GEMINI_API_KEY` 未設定或無效
2. `MODEL_NAME` 設定錯誤

**解決方法**：
```bash
# 檢查 .env
cat .env | findstr MODEL_NAME
# 應該是：MODEL_NAME=gemini-2.0-flash

# 測試 Gemini API
python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')
print(model.generate_content('Hello').text[:100])
"
```

### Q3: 前端無法連線到 API

**檢查清單**：
```bash
# 1. 確認 API 運行中
netstat -ano | findstr :5001

# 2. 確認前端運行中
netstat -ano | findstr :5173

# 3. 測試 API 健康檢查
curl http://localhost:5001/health
```

**vite.config.js 設定確認**：
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
```

### Q4: 資料庫錯誤

```bash
# 備份現有資料庫
copy aetheria.db aetheria.db.bak

# 重建資料庫
del aetheria.db
python run.py  # 會自動建立新資料庫
```

### Q5: 測試失敗

```bash
# 執行完整測試
pytest tests/ -v --tb=short

# 只測試特定模組
pytest tests/test_bazi.py -v

# 顯示詳細錯誤
pytest tests/ -v --tb=long
```

---

## 📖 延伸閱讀

### 重要文件

| 文件 | 說明 | 閱讀時間 |
|------|------|----------|
| [04_Architecture_Decision_LLM_First.md](docs/04_Architecture_Decision_LLM_First.md) | 核心架構決策文件 | 15 分鐘 |
| [01_Technical_Whitepaper.md](docs/01_Technical_Whitepaper.md) | 產品願景與技術白皮書 | 20 分鐘 |
| [05_Gemini_Prompt_Templates.md](docs/05_Gemini_Prompt_Templates.md) | 提示詞設計指南 | 30 分鐘 |
| [06_Chart_Locking_System.md](docs/06_Chart_Locking_System.md) | 命盤鎖定（定盤）系統 | 10 分鐘 |
| [STRATEGIC_API.md](docs/STRATEGIC_API.md) | 戰略側寫 API 文件 | 15 分鐘 |

### 外部參考

- [Google AI Studio](https://aistudio.google.com/) - Gemini API
- [OpenAI Platform](https://platform.openai.com/) - Realtime API
- [Swiss Ephemeris](https://www.astro.com/swisseph/) - 天文計算

---

## 📝 版本歷史

| 版本 | 日期 | 重大更新 |
|------|------|----------|
| **v1.9.3** | 2026-01-28 | 修復語音 API 502 錯誤（SDP 格式問題） |
| v1.9.2 | 2026-01-26 | AI 語音諮詢功能（OpenAI Realtime API） |
| v1.9.1 | 2026-01-26 | AI 文字諮詢功能（Gemini 2.0 Flash） |
| v1.9.0 | 2026-01-25 | 戰略側寫模組、UI v2.0 重新設計 |
| v1.8.0 | 2026-01-24 | 塔羅牌系統完成 |
| v1.7.0 | 2026-01-23 | 姓名學系統完成 |
| v1.6.0 | 2026-01-22 | 靈數學系統完成 |
| v1.5.0 | 2026-01-21 | 西洋占星系統完成 |
| v1.4.0 | 2026-01-20 | 八字命理系統完成 |
| v1.3.0 | 2026-01-19 | 紫微斗數系統完成 |

---

## 📄 授權

本專案採用 **GPL v2** 授權。

---

## 👥 貢獻指南

1. Fork 本專案
2. 建立 feature branch (`git checkout -b feature/amazing-feature`)
3. Commit 變更 (`git commit -m 'Add amazing feature'`)
4. Push 到 branch (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

---

*最後更新：2026-01-28*
*文件維護：Aetheria Team*
