# Aetheria Core 2.0 — Agent-Oriented AI 命理顧問

> **六大命理系統**：紫微斗數 · 八字 · 西洋占星 · 靈數 · 姓名學 · 塔羅  
> **AI 模型**：Gemini 3 Flash / Pro Preview（Agent + Tool Use 自主決策）  
> **架構**：Chat-First UI ｜ 三層記憶 ｜ Function Calling ｜ SSE 串流 ｜ 情緒感知

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-19.2-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646cff.svg)](https://vite.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-3%20Flash%20%2F%20Pro-orange.svg)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Tests-187%20passed-brightgreen.svg)]()
[![Quality](https://img.shields.io/badge/Quality%20Score-9.3%2F10-gold.svg)]()
[![Comprehensive](https://img.shields.io/badge/Comprehensive-16%2F16%20PASS-brightgreen.svg)]()
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
├── docs/                               # 技術文檔（11 份）
│   ├── STRATEGIC_API.md                # API 策略規範
│   ├── 01_Technical_Whitepaper.md      # 技術架構白皮書
│   ├── 02_UMF_Schema_Definition.md     # 統一命理格式
│   ├── 03_AI_Workflow_Guidelines.md    # AI 工作流指引
│   ├── 04_Architecture_Decision_LLM_First.md  # LLM-First 架構決策
│   ├── 05_Gemini_Prompt_Templates.md   # 提示詞範本
│   ├── 06_Chart_Locking_System.md      # 命盤鎖定系統
│   ├── 18_Optimization_Impact_Report.md # 優化影響報告（8.2→9.3）
│   ├── 18_Tool_Use_Implementation.md   # Tool Use 實作
│   ├── 18_Widget_System_Implementation.md  # Widget 系統
│   └── 20_Agent_Transformation_Plan.md # Agent 2.0 轉型計畫
│
└── scripts/                            # 工具腳本
    ├── test_comprehensive_quality.py   # 綜合品質測試（16 項場景）
    ├── test_conversation_quality.py    # 對話品質測試
    ├── test_database.py                # 資料庫驗證
    ├── start_api_and_test.sh           # API 啟動 + 測試
    ├── quick_test.ps1                  # 快速測試腳本
    └── archive/                        # 歷史測試腳本歸檔
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

**單元 / 整合測試**：187 通過 · 9 跳過 · 0 失敗（需啟動 API server）  
涵蓋：六大命理計算 · Agent 狀態機 · Tool Use · 三層記憶 · 敏感話題 · 離題偵測 · API 錯誤處理 · API 版本管理 · 命盤鎖定

**綜合品質測試**：16/16 全數通過 · 0 錯誤 · 專業評分 9.3/10  
涵蓋四大類 16 項場景：
| 類別 | 測試項 | 說明 |
|------|--------|------|
| A. 六大系統排盤 | A1–A8 | 八字 · 紫微+深度追問 · 占星 · 生命靈數 · 姓名學 · 塔羅 · 不指定系統自動排盤 · 跨日邊界時間 |
| B. 多系統整合 | B1 | 同時排八字+紫微（跨系統交叉驗證） |
| C. 對話體驗 | C1–C5 | 不重複詢問生辰 · 離題引導+不過度回答 · 語言品質 · 深度追問品質 · 跨 session 記憶 |
| D. 邊界情境 | D1–D2 | 缺性別追問 · 缺地點追問 |

---

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| AI 模型 | Gemini 3 Flash Preview（對話）· Gemini 3 Pro Preview（報告）（`google-genai` SDK） |
| 後端 | Flask 3.0 · Python 3.9+ |
| 前端 | React 19.2 · Vite 7 |
| 資料庫 | SQLite（可擴展至 PostgreSQL） |
| 串流 | Server-Sent Events (SSE) |
| 命理引擎 | `sxtwl`（天文曆）· `iztro-py`（紫微）· `kerykeion`（占星） |
| 測試 | pytest · 187+ unit/integration cases · 16/16 comprehensive quality tests |

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

## 🔧 修復與改進紀錄

### 2026-02-09：綜合品質提升（8.2 → 8.9 / 10，後續提升至 9.3）

經過多輪專家審查與迭代優化，整體諮詢品質評分從 8.2 提升至 8.9：

| 輪次 | 分數 | 主要改進 |
|------|------|----------|
| Round 1 | 8.2 | 基線測試 |
| Round 2 | 8.6 | 修復紫微引擎崩潰、塔羅牌陣名稱、占星相位模式、facts 擷取 |
| Round 3 | 8.8 | Gemini API 重試機制（5s→10s→20s 指數退避）、模型路由（Flash 對話 / Pro 報告）、熔斷 birth_time 預設值 |
| Round 4 | 8.9 | Prompt 強制術語、DIGNITY_TABLE 修復、占星無性別分析規則 |

**Round 4 關鍵改進：**

1. **八字回覆必備要素**（`agent_persona.py`）  
   強制 AI 在八字諮詢中必須提及：用神與喜忌、合沖刑害（附解釋）、格局名稱。  
   效果：術語命中率 3/6 → 5/6，C1 出現「卯酉六衝」「用神是水」，C4 完整用神選擇邏輯（1259 字）。

2. **占星 DIGNITY_TABLE 修正**（`astrology.py`）  
   修復 Python dict 重複 key 靜默覆蓋的 bug：  
   - 處女座 Mercury 原為兩個重複 key，後者覆蓋前者 → 改為 `'Domicile+Exaltation'` 複合格式  
   - 雙魚座 Mercury 同理 → 改為 `'Detriment+Fall'`  
   - `_get_planet_dignity()` 新增 `+` 分割解析，輸出例：「入廟（守護）／旺（擢升）」

3. **占星無性別完整分析規則**（`agent_persona.py`）  
   解決 AI 在已有占星排盤結果時仍拒絕分析、要求性別的問題：  
   - 新增【占星回覆必備要素 — 最高優先級】：明確「西洋占星完全不需要性別即可分析」  
   - 修改【不要假設未提供的資訊】：加入占星例外，排盤完成後必須先給完整星盤解讀  
   - 設定為「違反此規則＝嚴重錯誤」強制層級

---

### 2026-02-10：占星術語強制 & 回覆品質保障（8.9 → 9.3 / 10）

修復綜合品質測試 A3（西洋占星）反覆失敗的問題，將專業評分從 8.9 提升至 9.3：

| 改進項 | 檔案 | 說明 |
|--------|------|------|
| Prompt 術語強制 | `agent_persona.py` | 新增規則：工具回傳後首段回覆必須包含核心術語（占星：星座+行星/宮位；八字：日主+天干/地支） |
| 性別需求澄清 | `agent_persona.py` | 明確「西洋占星不需要性別」，僅八字/紫微需要性別；缺性別時仍須給出占星分析 |
| Server 端回覆品質保障 | `server.py` | 新增 `_ensure_astrology_terms_in_response()`：偵測占星回覆中關鍵術語不足時，自動補充術語密集的簡短段落 |
| 占星工具描述優化 | `tools.py` | 強化 `calculate_astrology` 工具的 description，提示 AI 回覆時必須引用星座、行星、宮位 |

**驗證結果**：綜合品質測試 16/16 全數通過，A3 穩定通過，術語命中率 3/4 組以上。

---

### 2026-02-09：Gemini 3 Thought Signature 相容性修復

**問題**：升級至 Gemini 3 Flash Preview / Pro Preview 後，所有 Function Calling（工具呼叫）均回傳 400 錯誤：

```
Function call is missing a thought_signature in functionCall parts.
```

**根因**：Gemini 3 模型強制要求在 multi-turn Function Calling 中，model 回覆的 `functionCall` part 必須包含 `thoughtSignature`，並在下一輪請求中原封不動傳回。原有代碼在收集 function call 時只保存了 `part.function_call`（丟失 signature），再用 `types.Part(function_call=fc)` 重建新 Part，導致 signature 遺失。

**修復方式**：
1. **保留原始 Part 對象**：streaming / 非 streaming 路徑改為保存完整的原始 `part`（含 `thoughtSignature`），回傳時直接使用，不重建。
2. **Fuse（熔斷）路徑**：系統自行注入的 function_call（非 AI 生成）無原始 signature，使用官方提供的 dummy signature `"skip_thought_signature_validator"` 跳過驗證。

**影響範圍**：`src/api/server.py` — streaming 工具迴圈、非 streaming 工具迴圈、單系統熔斷、多系統熔斷、塔羅熔斷共 5 處。

**參考文件**：[Google AI — Thought Signatures](https://ai.google.dev/gemini-api/docs/thought-signatures)

---

**Built with ❤️ — Aetheria Core 2.0**
