# Aetheria Core 2.0 — Agent-Oriented AI 命理顧問

> **六大命理系統**：紫微斗數 · 八字 · 西洋占星 · 靈數 · 姓名學 · 塔羅  
> **AI 模型**：Gemini 2.0 Flash（Agent + Tool Use 自主決策）  
> **架構**：Chat-First UI ｜ 三層記憶 ｜ Function Calling ｜ SSE 串流 ｜ 情緒感知

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-19.2-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646cff.svg)](https://vite.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-187%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-GPL%20v2-red.svg)]()

---

## 🎯 核心特色

### 💬 Chat-First 對話介面
- 無表單、無選單，全程自然語言對話
- 訪客免註冊即可開始，自動建立匿名身份
- 口語化命理解讀，取代冰冷的制式報告
- **對話歷史側邊欄**：可收合、可切換、可刪除過去對話

### 🧠 三層記憶系統
| 層級 | 內容 | 保留期限 |
|------|------|----------|
| Layer 1 | 短期工作記憶（最近 10-20 輪） | 90 天 |
| Layer 2 | 自動摘要（關鍵事件壓縮） | 永久 |
| Layer 3 | 核心知識庫（命盤結構 + 用戶畫像） | 永久 |

### 🤖 Agent 智慧核心
- **敘事型人設系統**：非規則清單，而是用第一人稱故事定義 AI 性格與說話風格
- **5 階段對話狀態機**：初見 → 信任建立 → 收集資料 → 深度諮詢 → 總結
- **情緒感知**：辨識焦慮、迷惘、急迫等訊號，調整回應策略
- **智慧離題偵測**：區分「回答 AI 提問」與「真正離題」，避免誤判
- **敏感話題保護**：自殺防護 · 隱私保護 · 專業轉介

### 🔧 Tool Use 系統
- **11 個工具**：六大排盤計算、塔羅抽牌、對話歷史搜尋、用戶畫像讀寫
- **Gemini Function Calling**：AI 自主決定調用時機
- **智慧去重**：已有命盤數據時自動跳過重複排盤
- **後台運算進度**：SSE 即時推播
- **命盤 Widget**：排盤結果以結構化卡片嵌入對話（紫微/八字/占星專屬佈局）

### 🔮 六大命理引擎
| 系統 | 引擎 | 核心功能 |
|------|------|----------|
| 紫微斗數 | `iztro-py` + `sxtwl` | 十二宮排盤、四化、大限流年流月 |
| 八字命理 | `sxtwl` 壽星天文曆 | 四柱排盤、十神、強弱、大運 |
| 西洋占星 | `kerykeion` | 行星位置、宮位、相位、星座 |
| 生命靈數 | 自研引擎 | 生命數、天賦數、流年數 |
| 姓名學 | 康熙字典筆劃 | 五格剖象、三才五行 |
| 塔羅占卜 | 78 張標準牌庫 | 牌陣抽牌、正逆位解讀 |

---

## 🚀 快速開始

### 1. 環境安裝

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 為 `.env`，填入 Gemini API Key：

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 啟動後端

```bash
python run.py
# API → http://localhost:5001
# Health → http://localhost:5001/health
```

### 4. 啟動前端

```bash
cd webapp
npm install
npm run dev
# UI → http://localhost:5173
```

打開瀏覽器訪問 **http://localhost:5173**，即可開始對話！

---

## 📡 API 端點

### 對話
| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/chat/consult-stream` | 主對話（SSE 串流） |
| `GET`  | `/api/chat/sessions` | 會話列表 |
| `GET`  | `/api/chat/messages` | 歷史訊息（`?session_id=xxx`） |
| `DELETE` | `/api/chat/sessions/<id>` | 刪除會話 |
| `POST` | `/api/chat/feedback` | 用戶回饋（👍👎） |

### 認證
| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/auth/register` | 註冊 |
| `POST` | `/api/auth/login` | 登入 |
| `POST` | `/api/auth/logout` | 登出 |

### 命理計算
| 方法 | 路徑 | 說明 |
|------|------|------|
| `POST` | `/api/calculate/ziwei` | 紫微斗數 |
| `POST` | `/api/calculate/bazi` | 八字 |
| `POST` | `/api/calculate/astrology` | 西洋占星 |
| `POST` | `/api/calculate/numerology` | 生命靈數 |
| `POST` | `/api/calculate/name` | 姓名學 |
| `POST` | `/api/calculate/tarot` | 塔羅牌 |

### 用戶 & 管理
| 方法 | 路徑 | 說明 |
|------|------|------|
| `GET`    | `/api/profile` | 用戶資料 |
| `GET`    | `/api/admin/metrics` | 系統監控 |
| `POST`   | `/api/admin/quality-evaluation` | 對話品質評估 |
| `DELETE` | `/api/privacy/delete-my-data` | GDPR 資料刪除 |

完整規範 → [docs/STRATEGIC_API.md](docs/STRATEGIC_API.md)

---

## 🗂️ 專案結構

```
Aetheria_Core/
├── run.py                              # 啟動入口
├── requirements.txt                    # Python 依賴
├── pytest.ini                          # pytest 設定
├── .env.example                        # 環境變數範本
│
├── src/
│   ├── api/
│   │   ├── server.py                   # Flask API 主程式（~10,000 行）
│   │   ├── schemas.py                  # 請求/回應 Schema
│   │   └── blueprints/
│   │       └── auth.py                 # 認證 Blueprint
│   │
│   ├── calculators/                    # 六大命理計算引擎
│   │   ├── bazi.py                     # 八字（四柱、十神、大運）
│   │   ├── astrology.py                # 西洋占星（行星、宮位、相位）
│   │   ├── numerology.py               # 靈數（生命數、天賦數）
│   │   ├── name.py                     # 姓名學（五格、三才）
│   │   ├── tarot.py                    # 塔羅（78 牌、正逆位）
│   │   ├── ziwei_hard.py               # 紫微斗數核心排盤
│   │   ├── fortune.py                  # 運勢引擎（大限、流年、流月）
│   │   ├── chart_extractor.py          # 命盤資料擷取器
│   │   └── async_calculator.py         # 非同步排盤
│   │
│   ├── prompts/                        # Gemini 提示詞模板
│   │   ├── agent_persona.py            # Agent 人設 + 狀態機（敘事型人設）
│   │   ├── intelligence_core.py        # 智慧核心（情緒感知 + 離題偵測）
│   │   ├── strategic.py                # 策略諮詢
│   │   ├── synastry.py                 # 合盤分析
│   │   ├── integrated.py               # 跨系統整合
│   │   ├── fortune.py                  # 運勢提示詞
│   │   ├── date_selection.py           # 擇日提示詞
│   │   ├── bazi.py / astrology.py      # 各系統專屬提示詞
│   │   ├── name.py / numerology.py / tarot.py
│   │   └── registry/                   # 提示詞註冊表
│   │       ├── persona.py              # 人格設定（敘事型 System Prompt）
│   │       ├── emotional_intelligence.py # 情緒智能
│   │       ├── conversation_strategies.py # 對話策略
│   │       └── safety_policy.py        # 安全政策
│   │
│   └── utils/
│       ├── memory.py                   # 三層記憶管理器
│       ├── auto_summary.py             # 自動摘要引擎
│       ├── conversation_summarizer.py  # 對話摘要
│       ├── tools.py                    # Tool Use 定義 + 執行器
│       ├── database.py                 # SQLite 資料庫
│       ├── gemini_client.py            # Gemini API 客戶端
│       ├── sensitive_topics.py         # 敏感話題偵測
│       ├── task_manager.py             # 背景任務管理
│       ├── auth_utils.py               # 認證工具
│       ├── api_versioning.py           # API 版本管理
│       ├── geonames_cache.py           # 地理資料快取
│       ├── logger.py                   # 日誌系統
│       └── errors.py                   # 統一錯誤處理
│
├── webapp/                             # React 19 前端（Vite 7）
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx                     # 主應用（認證 + 佈局）
│       ├── ChatContainer.jsx           # 對話容器（SSE 串流 + Tool Use 進度）
│       ├── MessageRenderer.jsx         # 訊息渲染（Markdown + 回饋按鈕）
│       ├── SessionSidebar.jsx          # 對話歷史側邊欄（切換/刪除/收合）
│       ├── SessionSidebar.css          # 側邊欄樣式
│       ├── VoiceChat.jsx               # 語音對話（實驗性）
│       ├── main.jsx                    # React 入口
│       ├── contexts/
│       │   └── AetheriaContext.jsx     # 全域狀態管理
│       └── widgets/
│           ├── ChartWidget.jsx         # 命盤卡片（紫微/八字/占星結構化呈現）
│           └── ChartWidget.css
│
├── tests/                              # pytest 測試套件
│   ├── conftest.py                     # 共用 fixtures
│   ├── golden_set/                     # Golden Set 回歸驗證（6 模組）
│   ├── test_bazi.py                    # 八字計算驗證
│   ├── test_calculator_bazi.py         # 八字計算器單元測試
│   ├── test_astrology.py              # 占星計算驗證
│   ├── test_ziwei.py                  # 紫微排盤驗證
│   ├── test_ziwei_hard_reference.py   # 紫微參照驗證
│   ├── test_chart_locks_schema.py     # 命盤鎖定 Schema 驗證
│   ├── test_numerology.py             # 靈數驗證
│   ├── test_name.py                   # 姓名學驗證
│   ├── test_tarot.py                  # 塔羅驗證
│   ├── test_fortune.py                # 運勢驗證
│   ├── test_tool_use.py               # Tool Use 驗證
│   ├── test_sensitive_topics.py       # 敏感話題偵測
│   ├── test_sensitive_api_intercept.py # API 層敏感攔截
│   ├── test_ai_memory_recall.py       # AI 記憶回溯驗證
│   ├── test_memory_poc.py             # 記憶系統驗證
│   ├── test_database.py               # 資料庫操作
│   ├── test_api_errors.py             # API 錯誤處理
│   ├── test_api_health.py             # 健康檢查
│   ├── test_api_versioning.py         # API 版本管理
│   └── ...                             # 共 26 個測試模組 + 6 Golden Set
│
├── data/                               # 運行時資料
│   ├── aetheria.db                     # SQLite 主資料庫
│   ├── geonames_cache.db              # 地理資料快取
│   ├── tarot_cards.json                # 塔羅牌資料（78 張）
│   ├── numerology_data.json            # 靈數參照表
│   ├── name_analysis.json              # 姓名學字庫
│   ├── kangxi_strokes.json             # 康熙字典筆劃表
│   └── ziwei_reference_chen.json       # 紫微參照命盤
│
├── docs/                               # 技術文檔（10 份）
│   ├── STRATEGIC_API.md                # API 策略規範
│   ├── 01_Technical_Whitepaper.md      # 技術架構白皮書
│   ├── 02_UMF_Schema_Definition.md     # 統一命理格式
│   ├── 03_AI_Workflow_Guidelines.md    # AI 工作流指引
│   ├── 04_Architecture_Decision_LLM_First.md  # LLM-First 架構決策
│   ├── 05_Gemini_Prompt_Templates.md   # 提示詞範本
│   ├── 06_Chart_Locking_System.md      # 命盤鎖定系統
│   ├── 18_Tool_Use_Implementation.md   # Tool Use 實作
│   ├── 18_Widget_System_Implementation.md  # Widget 系統
│   └── 20_Agent_Transformation_Plan.md # Agent 2.0 轉型計畫
│
└── scripts/                            # 工具腳本
    ├── start_api_and_test.sh           # API 啟動 + 測試
    └── test_database.py                # 資料庫驗證
```

---

## 🧪 測試

```bash
# 完整測試套件（排除 Golden Set，因其需要 Gemini API）
python -m pytest tests/ --ignore=tests/golden_set -v

# 快速驗證
python -m pytest tests/ --ignore=tests/golden_set -q --tb=line

# 單一模組
python -m pytest tests/test_bazi.py -v

# Golden Set 回歸（需要 Gemini API Key）
python -m pytest tests/golden_set/ -v
```

**測試結果**：187 通過 · 9 跳過 · 0 失敗（需啟動 API server）  
涵蓋：六大命理計算 · Agent 狀態機 · Tool Use · 三層記憶 · 敏感話題 · 離題偵測 · API 錯誤處理 · API 版本管理 · 命盤鎖定

---

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| AI 模型 | Gemini 2.0 Flash（`google-genai` SDK） |
| 後端 | Flask 3.0 · Python 3.9+ |
| 前端 | React 19.2 · Vite 7 |
| 資料庫 | SQLite（可擴展至 PostgreSQL） |
| 串流 | Server-Sent Events (SSE) |
| 命理引擎 | `sxtwl`（天文曆）· `iztro-py`（紫微）· `kerykeion`（占星） |
| 測試 | pytest · 187+ cases |

---

## 📚 技術文檔

| 文檔 | 說明 |
|------|------|
| [Agent 轉型計畫](docs/20_Agent_Transformation_Plan.md) | 三層記憶 · 狀態機 · Tool Use · 81 項實作清單 |
| [API 策略規範](docs/STRATEGIC_API.md) | 端點設計 · 認證 · 錯誤碼 |
| [技術架構白皮書](docs/01_Technical_Whitepaper.md) | 系統架構 · 部署方式 |
| [UMF Schema](docs/02_UMF_Schema_Definition.md) | 統一命理資料格式 |
| [Tool Use 實作](docs/18_Tool_Use_Implementation.md) | 11 個工具 · Function Calling |
| [Widget 系統](docs/18_Widget_System_Implementation.md) | 命盤卡片 · SSE 事件格式 |
| [命盤鎖定系統](docs/06_Chart_Locking_System.md) | 排盤快取 · 資料一致性 |
| [LLM-First 架構](docs/04_Architecture_Decision_LLM_First.md) | 設計決策與取捨 |

---

## 📄 授權

GPL v2

---

**Built with ❤️ — Aetheria Core 2.0**
