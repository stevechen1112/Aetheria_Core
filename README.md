# Aetheria Core 2.0 — Agent-Oriented AI 命理顧問

> **六大命理系統**：紫微斗數 · 八字 · 西洋占星 · 靈數 · 姓名學 · 塔羅  
> **AI 模型**：Gemini 2.0 Flash（Agent + 報告雙模式）  
> **架構**：Chat-First UI ｜ 三層記憶 ｜ Tool Use ｜ SSE 串流 ｜ 情緒感知

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-247%20passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-GPL%20v2-red.svg)]()

---

## 🎯 核心特色

### 💬 Chat-First 對話介面
- 無表單、無選單，全程自然語言對話
- 訪客免註冊即可開始，自動建立匿名身份
- 口語化命理解讀，取代冰冷的制式報告

### 🧠 三層記憶系統
| 層級 | 內容 | 保留期限 |
|------|------|----------|
| Layer 1 | 短期工作記憶（最近 10-20 輪） | 90 天 |
| Layer 2 | 自動摘要（關鍵事件壓縮） | 永久 |
| Layer 3 | 核心知識庫（命盤結構 + 用戶畫像） | 永久 |

### 🤖 Agent 智慧核心
- **5 階段對話狀態機**：初見 → 信任建立 → 收集資料 → 深度諮詢 → 總結
- **情緒感知**：辨識焦慮、迷惘、急迫等訊號，調整回應策略
- **敏感話題保護**：自殺防護 · 隱私保護 · 專業轉介

### 🔧 Tool Use 系統
- **11 個工具**：六大排盤計算、塔羅抽牌、對話歷史搜尋、用戶畫像讀寫
- **Gemini Function Calling**：AI 自主決定調用時機
- **後台運算進度**：SSE 即時推播

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
│   │   ├── server.py                   # Flask API 主程式
│   │   ├── schemas.py                  # 請求/回應 Schema
│   │   └── blueprints/                 # Auth Blueprint
│   │
│   ├── calculators/                    # 六大命理計算引擎
│   │   ├── bazi.py                     # 八字
│   │   ├── astrology.py                # 西洋占星
│   │   ├── numerology.py               # 靈數
│   │   ├── name.py                     # 姓名學
│   │   ├── tarot.py                    # 塔羅
│   │   ├── ziwei_hard.py               # 紫微斗數
│   │   ├── fortune.py                  # 綜合運勢
│   │   ├── chart_extractor.py          # 命盤資料擷取
│   │   └── async_calculator.py         # 非同步排盤
│   │
│   ├── prompts/                        # Gemini 提示詞模板
│   │   ├── agent_persona.py            # Agent 人設 + 狀態機
│   │   ├── intelligence_core.py        # 智慧核心（情緒感知）
│   │   ├── strategic.py                # 策略諮詢
│   │   ├── synastry.py                 # 合盤分析
│   │   └── registry/                   # 提示詞註冊表
│   │
│   └── utils/
│       ├── memory.py                   # 三層記憶管理器
│       ├── conversation_summarizer.py  # 自動摘要
│       ├── tools.py                    # Tool Use 定義 + 執行器
│       ├── database.py                 # SQLite 資料庫
│       ├── gemini_client.py            # Gemini API 客戶端
│       ├── sensitive_topics.py         # 敏感話題偵測
│       ├── task_manager.py             # 背景任務管理
│       ├── auth_utils.py               # 認證工具
│       ├── api_versioning.py           # API 版本管理
│       ├── geonames_cache.py           # 地理資料快取
│       ├── logger.py                   # 日誌系統
│       └── errors.py                   # 錯誤處理
│
├── webapp/                             # React 19 前端
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx                     # 主應用（Chat-First）
│       ├── App.css
│       ├── ChatContainer.jsx           # 對話容器 + SSE 串流
│       ├── ChatContainer.css
│       ├── MessageRenderer.jsx         # 訊息渲染 + 回饋按鈕
│       ├── MessageRenderer.css
│       ├── VoiceChat.jsx               # 語音對話（實驗性）
│       ├── VoiceChat.css
│       ├── index.css                   # 全域樣式（深色主題）
│       ├── main.jsx                    # React 入口
│       ├── contexts/
│       │   └── AetheriaContext.jsx     # 全域狀態管理
│       └── widgets/
│           ├── ChartWidget.jsx         # 命盤卡片組件
│           └── ChartWidget.css
│
├── tests/                              # pytest 測試套件（247 cases）
│   ├── conftest.py                     # 共用 fixtures
│   ├── golden_set/                     # Golden Set 回歸驗證（6 模組）
│   ├── test_bazi.py
│   ├── test_astrology.py
│   ├── test_ziwei.py
│   ├── test_numerology.py
│   ├── test_name.py
│   ├── test_tarot.py
│   ├── test_tool_use.py
│   ├── test_sensitive_topics.py
│   ├── test_memory_poc.py
│   ├── test_api_versioning.py
│   └── ...                             # 共 27 個測試模組
│
├── data/                               # 運行時資料
│   ├── aetheria.db                     # SQLite 主資料庫
│   ├── geonames_cache.db              # 地理資料快取
│   ├── tarot_cards.json                # 塔羅牌資料
│   ├── numerology_data.json            # 靈數參照表
│   └── name_analysis.json              # 姓名學字庫
│
├── scripts/                            # 工具腳本
│   ├── start_api_and_test.sh           # API 啟動 + 測試
│   └── test_database.py                # 資料庫驗證
│
├── docs/                               # 技術文檔（10 份）
│   ├── 20_Agent_Transformation_Plan.md # Agent 2.0 轉型計畫（主文件）
│   ├── STRATEGIC_API.md                # API 策略規範
│   ├── 01_Technical_Whitepaper.md      # 技術架構白皮書
│   ├── 02_UMF_Schema_Definition.md     # 統一命理格式
│   ├── 03_AI_Workflow_Guidelines.md    # AI 工作流指引
│   ├── 04_Architecture_Decision_LLM_First.md  # LLM-First 架構
│   ├── 05_Gemini_Prompt_Templates.md   # 提示詞範本
│   ├── 06_Chart_Locking_System.md      # 鎖盤系統
│   ├── 18_Tool_Use_Implementation.md   # Tool Use 實作
│   └── 18_Widget_System_Implementation.md  # Widget 系統
│
└── logs/                               # 運行時日誌（gitignored）
```

---

## 🧪 測試

```bash
# 完整測試套件
python -m pytest tests/ -v

# 快速驗證
python -m pytest tests/ -q --tb=line

# 單一模組
python -m pytest tests/test_bazi.py -v

# Golden Set 回歸
python -m pytest tests/golden_set/ -v
```

**測試覆蓋**：247 項通過  
六大命理計算 · Agent 狀態機 · Tool Use · 三層記憶 · 敏感話題 · API 版本管理 · Golden Set 回歸

---

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| AI 模型 | Gemini 2.0 Flash |
| 後端 | Flask 3.0 · Python 3.9+ |
| 前端 | React 19 · Vite 7 |
| 資料庫 | SQLite（可擴展至 PostgreSQL） |
| 串流 | Server-Sent Events (SSE) |
| 測試 | pytest · 247 cases |

---

## 📚 技術文檔

| 文檔 | 說明 |
|------|------|
| [Agent 轉型計畫](docs/20_Agent_Transformation_Plan.md) | 三層記憶 · 狀態機 · Tool Use · 81 項實作清單 |
| [API 策略規範](docs/STRATEGIC_API.md) | 端點設計 · 認證 · 錯誤碼 |
| [技術架構白皮書](docs/01_Technical_Whitepaper.md) | 系統架構 · 部署方式 |
| [UMF Schema](docs/02_UMF_Schema_Definition.md) | 統一命理資料格式 |
| [Tool Use 實作](docs/18_Tool_Use_Implementation.md) | 11 個工具 · Function Calling |
| [Widget 系統](docs/18_Widget_System_Implementation.md) | 前端命盤卡片 · SSE 事件格式 |

---

## 📄 授權

GPL v2

---

**Built with ❤️ — Aetheria Core 2.0**
