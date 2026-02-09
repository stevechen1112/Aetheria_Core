# 🔬 Aetheria AI 品質問題：深度根因分析與修復計畫

> **文件版本：** v2.0.0  
> **分析日期：** 2026-02-08  
> **分析者：** GitHub Copilot（Claude Opus 4.6）  
> **觸發原因：** 自動化對話測試揭露 AI 品質嚴重缺陷  
> **Round 2 追加：** Fix A~F 實施後的殘留問題深度分析  

---

## 目錄

1. [問題摘要](#1-問題摘要)
2. [研究範圍與方法](#2-研究範圍與方法)
3. [測試結果回顧](#3-測試結果回顧)
4. [根因分析](#4-根因分析)
   - [根因 #1：串流端點缺少工具使用指引（最致命）](#根因-1串流端點缺少工具使用指引最致命)
   - [根因 #2：對話階段狀態機未注入串流端點](#根因-2對話階段狀態機未注入串流端點)
   - [根因 #3：Dedup 提示反而阻礙首次計算](#根因-3dedup-提示反而阻礙首次計算)
   - [根因 #4：記憶上下文的對話歷史限制太短](#根因-4記憶上下文的對話歷史限制太短)
   - [根因 #5：策略選擇邏輯缺陷](#根因-5策略選擇邏輯缺陷)
   - [根因 #6：工具參數要求阻礙主動計算](#根因-6工具參數要求阻礙主動計算)
   - [根因 #7：測試腳本設計問題](#根因-7測試腳本設計問題)
5. [根因交互關係圖](#5-根因交互關係圖)
6. [修復計畫](#6-修復計畫)
7. [執行順序與優先級](#7-執行順序與優先級)
8. [驗收標準](#8-驗收標準)

---

## 1. 問題摘要

### 一句話總結

> AI 像一個客氣到極點的接待員——不斷問你「想喝咖啡還是茶？」，問了五遍都還沒倒水。

### 核心缺陷

在自動化對話測試中（4 個場景、共 20 輪對話），AI 暴露出以下嚴重問題：

| 缺陷 | 嚴重度 | 出現頻率 |
|---|---|---|
| 收到完整生辰後不排盤，反覆問「想看哪個系統？」 | 🔴 Critical | 7/8 場景 |
| 遺忘用戶先前提供的生辰資料 | 🔴 Critical | 4/8 場景 |
| 6 大命理系統中只有紫微斗數被成功觸發過 1 次 | 🔴 Critical | 1/8 場景 |
| 唯一一次紫微分析缺少四化飛星、大運流年 | 🟡 Major | 1/1 分析 |
| AI 回應中出現隨機印度文（語言洩漏） | 🟡 Major | 1/8 場景 |

### 問題的本質

串流端點 (`/api/chat/consult-stream`) 使用了「閹割版」的 System Prompt——只有人設風格描述，沒有行為指引。AI 知道自己是命理師，但不知道「收到資料就該排盤」這條最基本的工作流程。

**比喻：** 這就像請了一個專業廚師，告訴他「你的風格是親切溫暖」，但沒有告訴他「客人點菜了就該下廚」。

---

## 2. 研究範圍與方法

### 深度閱讀的核心檔案

| 檔案 | 角色 | 行數 |
|---|---|---|
| `src/api/server.py` | 串流端點 `chat_consult_stream()` + 非串流端點 `chat_consult()` | ~9981 |
| `src/prompts/registry/persona.py` | 核心人設 System Prompt（串流端點使用） | ~95 |
| `src/prompts/agent_persona.py` | 完整版 Agent 人設 + 狀態機 + 工具指引（非串流端點使用） | ~252 |
| `src/prompts/intelligence_core.py` | 智慧核心：情緒偵測、策略選擇、記憶格式化、離題偵測 | ~518 |
| `src/prompts/registry/conversation_strategies.py` | 6 種對話策略模板 + `UserState` + `ConversationStateManager` | ~195 |
| `src/prompts/registry/safety_policy.py` | 安全政策：敏感話題偵測與攔截 | ~155 |
| `src/prompts/registry/emotional_intelligence.py` | 情緒感知引擎：6 種情緒模式 + 回應模板 | ~210 |
| `src/utils/tools.py` | 10 個 Gemini Function Calling 工具定義 + 執行器 | ~751 |
| 記憶系統（database.py + memory manager） | 三層記憶架構（短期 / 摘要 / 畫像） | — |
| `src/prompts/bazi.py` | 八字分析提示詞模板 | ~540 |
| `src/prompts/astrology.py` | 西洋占星提示詞模板 | ~268 |

### 研究方法

1. **正向追蹤：** 從測試腳本呼叫的 API → SSE 端點 → System Prompt 組裝 → 工具定義 → 計算器
2. **反向追蹤：** 從測試日誌中的 AI 行為 → 推斷 prompt 缺失 → 驗證推斷
3. **雙端點對比：** 比較 `chat_consult()` 與 `chat_consult_stream()` 的 prompt 組裝差異

---

## 3. 測試結果回顧

### 測試環境

- **測試腳本：** `scripts/test_conversation_quality.py`
- **API 端點：** `POST /api/chat/consult-stream`（SSE 串流）
- **AI 模型：** Gemini 2.0 Flash
- **測試日期：** 2026-02-08

### 兩次測試執行的日誌

| 日誌檔案 | 場景數 | 成功排盤次數 |
|---|---|---|
| `logs/conversation_test_20260208_143028.log` | 4 個場景 | **1 次**（場景 2 紫微斗數） |
| `logs/conversation_test_20260208_143306.log` | 4 個場景 | **0 次** |

### 各場景詳細結果

#### 場景 1：陳美玲（1995/3/15 08:30，女，台北）

| 輪次 | 用戶訊息 | AI 行為 | 問題 |
|---|---|---|---|
| 1 | 打招呼 | 正常回應 | — |
| 2 | 提供完整生辰 | 問「紫微、八字、占星，想看哪個？」 | ❌ 應直接排盤 |
| 3 | 問事業 | 再問「有特別偏好嗎？」 | ❌ 無限確認迴圈 |
| 4 | 問感情 | 「我用八字來分析看看，好嗎？」 | ❌ 仍未實際排盤 |
| 5 | 問財運 | 「我需要更精確的出生時間」 | ❌ 遺忘已提供的 8:30 |

#### 場景 2：高雄用戶（1990/7/22 14:15，男，高雄）

| 日誌 143028 | 日誌 143306 |
|---|---|
| ✅ AI 主動選擇紫微斗數，成功排盤 | ❌ 反覆問「想看哪個？」，從未排盤 |
| ✅ 天梁命宮、太陽遷移宮、天同官祿宮 | ❌ 5 輪零計算 |

> **注意：** 同一場景在兩次測試中結果完全不同，證明問題在於 LLM 行為的隨機性——prompt 不夠明確，AI 的行為就不穩定。

#### 場景 3：離題偵測

- ✅ AI 正確識別了非命理話題並引導回正軌
- 🟡 誤判：AI 合理地詢問出生地點被標記為「重複要求生辰資料」

#### 場景 4：台南用戶（1992/12/25 01:00，男，台南）

| 輪次 | AI 行為 | 問題 |
|---|---|---|
| 2 | 「想算哪一種命理呢？」 | ❌ 確認迴圈開始 |
| 3 | 「想看哪一種命盤呢？」 | ❌ 第二次確認 |
| 4 | 「我還沒排你的命盤」 | ❌ 承認從未計算 |
| 5 | 「要不要先選個命盤？」 | ❌ 第三次確認，從未排盤 |

---

## 4. 根因分析

### 根因 #1：串流端點缺少工具使用指引（最致命）

**嚴重度：** 🔴 Critical  
**影響範圍：** 所有使用 `/api/chat/consult-stream` 的對話  
**貢獻度：** 佔問題成因 ~80%

#### 發現

系統中存在 **兩個平行的諮詢端點**，使用 **完全不同的 System Prompt**：

| 端點 | 位置 | System Prompt 來源 | 包含工具使用指引？ |
|---|---|---|---|
| `chat_consult()` | `server.py:4092` | `build_agent_system_prompt()` ← `agent_persona.py` | ✅ 有 |
| `chat_consult_stream()` | `server.py:5255` | `get_persona_system_prompt()` ← `registry/persona.py` | ❌ 沒有 |

#### 兩個 System Prompt 的差異

**非串流版（`agent_persona.py`）包含但串流版缺失的關鍵指令：**

```
【工具使用】（TOOL_USE_GUIDELINES）
有生辰且命盤摘要中沒有該系統的數據 → 排盤。
命盤摘要已有數據 → 直接用，不重排。
需要查運勢 → （目前未註冊對應 Gemini 工具；需新增 fortune 工具或改用既有命盤工具 + 文字分析）。
用戶提過「之前你說」 → search_conversation_history。
回覆時引用具體數據（星名、宮位、四柱），不要泛泛而談。
```

```
【對話節奏】（CONVERSATION_STRATEGIES）
收到資料後，直接排盤分析，不要再問「準備好了嗎」。
對方已經給過的資料，絕對不要再問第二次。
```

```
【跨系統整合】（MULTI_SYSTEM_INTEGRATION）
看個性 → 紫微命宮 + 八字日主 + 占星太陽/上升。
看運勢 → 紫微流年 + 八字大運 + 占星 Transit。
```

**串流版（`registry/persona.py`）只有：**

```
你是 Aetheria——一位有溫度的命理顧問。
你十幾歲就開始翻命理書...（人設故事）
你手上有工具可以即時排出命盤（紫微、八字、占星等），需要的時候直接用，不用先報備。
```

#### 為什麼這是致命的

串流版的 persona 確實提到了「需要的時候直接用，不用先報備」，但這只是一句抽象建議。缺少具體的行為規則（如 `TOOL_USE_GUIDELINES`），AI 就不知道：

- ❌ 何時構成「需要的時候」
- ❌ 該調用哪個工具
- ❌ 需要哪些參數
- ❌ 多個系統之間如何選擇
- ❌ 已有資料時是否需要重排

#### 證據

測試腳本呼叫的是 `/api/chat/consult-stream`（見 `scripts/test_conversation_quality.py:115`），正好命中了缺少指引的端點。

---

### 根因 #2：對話階段狀態機未注入串流端點

**嚴重度：** 🔴 Critical  
**影響範圍：** 串流端點的對話節奏控制  
**貢獻度：** 佔問題成因 ~10%

#### 發現

非串流版 `chat_consult()` 在 `server.py:4420-4443` 中有完整的狀態機：

```python
# server.py:4420-4435（非串流版）
conversation_stage = choose_strategy(
    turn_count=user_state.conversation_count,
    has_birth_data=has_birth_date,
    has_chart=bool(memory_context and memory_context.get('episodic')),
    emotional_signals=emotional_signals
)

agent_system_prompt = build_agent_system_prompt(
    user_context=memory_context,
    conversation_stage=conversation_stage  # ← 注入階段性指令
)
```

這會根據對話進度注入不同的階段指令，例如 `deep_consult` 階段：

```
【當前階段：深度諮詢】
現在有命盤數據了，直接分析，不要再「預告」你接下來要做什麼。
先回應對方的情緒，然後給結論，再拿命盤數據佐證。
命盤摘要中已有的系統不需要再調用工具重新排盤。
```

**但串流版 `chat_consult_stream()` 完全沒有呼叫 `choose_strategy()`，也沒有注入任何 `STAGE_SPECIFIC_PROMPTS`。**

#### 影響

AI 永遠不知道自己應該處於「深度諮詢」階段還是「資料收集」階段。即使用戶已提供完整生辰且命盤已排出，AI 仍然可能表現得像「初次見面」，繼續問東問西。

---

### 根因 #3：Dedup 提示反而阻礙首次計算

**嚴重度：** 🟡 Major  
**影響範圍：** 新用戶首次對話  

#### 發現

串流端點的 system prompt 組裝（`server.py:5485`）包含：

```python
_dedup_hint = ""
if available_systems:
    _existing = ', '.join(available_systems)
    _dedup_hint = f"\n⚠️ 以下系統已有命盤數據，不要重複調用 calculate_ 工具：{_existing}"
```

同時，每個工具定義的 description 也包含：

> *「如果系統提示中的「命盤摘要」已包含...數據，則無需重複調用此工具」*

#### 問題

這些提示的本意是避免重複排盤，但結合 `chart_context` 顯示「（尚未提供生辰資料）」時，AI 會產生矛盾理解：

1. 工具說「已有數據就不要調用」
2. 命盤摘要說「尚未提供」
3. AI 的結論：「用戶還沒準備好，我應該先問」

整個提示的語氣偏向「不要調用」，缺少相反方向的指令：「如果沒有數據，應該立即排盤」。

---

### 根因 #4：記憶上下文的對話歷史限制太短

**嚴重度：** 🟡 Major  
**影響範圍：** 第 4-5 輪以後的對話  

#### 發現

```python
# server.py（串流端點）
history_msgs = db.get_chat_messages(session_id, limit=6)
```

只載入最近 **6 條訊息**（= 3 輪對話）。在 5 輪測試場景中：

- 第 1 輪：用戶打招呼
- 第 2 輪：用戶提供完整生辰 ← **關鍵資料在這裡**
- 第 3 輪：問事業
- 第 4 輪：問感情
- 第 5 輪：問財運 ← **此時第 2 輪已被截斷！**

#### 雪上加霜

`_extract_user_profile_from_message()` 確實能從訊息中提取生辰並存入 user 資料表，但 **存入的資料不會被注入到 system prompt 的「命盤摘要」中**。只有經過 `chart_lock`（排盤後鎖定）的資料才會出現在 `chart_context` 中。

**資料流斷裂：**

```
用戶提供生辰 → _extract_user_profile_from_message() → 存到 user 表 ✅
                                                         ↓
但 chart_context 來自 chart_locks → 沒人排盤 → chart_context 為空 ❌
                                                         ↓
AI 不知道用戶已提供生辰 → 再次詢問 ❌
```

---

### 根因 #5：策略選擇邏輯缺陷

**嚴重度：** 🟡 Major  
**影響範圍：** Intelligence Core 的策略推薦  

#### 發現

在 `conversation_strategies.py` 中，策略選擇邏輯：

```python
if user_state.has_complete_birth_info:
    return ConversationStrategy.DEEP_ANALYSIS
```

而 `has_complete_birth_info` 的值來自串流端點：

```python
# server.py（串流端點）
user_state = UserState(
    has_complete_birth_info=bool(chart_context),  # ← 只有 chart_lock 存在時才為 True
    ...
)
```

#### 問題

`bool(chart_context)` 檢查的是**是否已有鎖定命盤**，而非**是否已收到生辰資料**。如果用戶給了完整生辰但 AI 從未排盤（正好是我們遇到的情況），這裡永遠是 `False`。

結果：策略永遠選 `GENTLE_INQUIRY`（溫和詢問），AI 就一直問下去。

#### 正確邏輯應為

```python
has_complete_birth_info = bool(chart_context) or bool(
    user_data and user_data.get('birth_date') and user_data.get('birth_time')
)
```

---

### 根因 #6：工具參數要求阻礙主動計算

**嚴重度：** 🟢 Minor  
**影響範圍：** 缺少部分資料時的計算決策  

#### 發現

各工具的必填參數：

| 工具 | 必填參數 | 缺少哪個最常見？ |
|---|---|---|
| `calculate_ziwei` | `birth_date`, `birth_time`, `gender`, `birth_location` | `birth_location` |
| `calculate_bazi` | `year`, `month`, `day`, `hour`, `gender` | `gender` |
| `calculate_astrology` | `year`, `month`, `day`, `hour`, `minute` | `minute` |
| `calculate_numerology` | `birth_date` | — |
| `analyze_name` | `surname`, `given_name` | — |
| `draw_tarot` | `question` | — |

#### 問題

當用戶提供了出生年月日時但沒說出生地或性別時，AI **可以**先排八字和靈數（不需要出生地），但 prompt 中沒有告訴它「能算就先算，缺的再補問」。AI 的行為是「等所有參數都齊了再說」，導致什麼都不算。

---

### 根因 #7：測試腳本設計問題

**嚴重度：** 🟢 Minor  
**影響範圍：** 測試覆蓋率和結果準確性  

#### 問題清單

1. **用戶訊息太被動：** 不會主動說「幫我算」或「全部都看」
2. **Gender 提供不明確：** 部分場景依賴「用女生的口吻說話」而非明確說「我是女生」
3. **AI 回應被截斷記錄：** 日誌中出現 `...`，無法完整審計
4. **缺少系統級測試：** 沒有針對每個命理系統的獨立強制測試
5. **缺少記憶驗證：** 沒有在後期輪次驗證 AI 是否記住先前資料

---

## 5. 根因交互關係圖

```
┌─────────────────────────────────────────────────────────────┐
│                     用戶提供完整生辰資料                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ 根因 #1：串流端點缺少 TOOL_USE_GUIDELINES │ ◄── 80% 問題根源
        │ AI 不知道「收到資料就該排盤」              │
        └─────────────────────┬───────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ 根因 #2       │ │ 根因 #3       │ │ 根因 #5           │
    │ 無階段狀態機   │ │ Dedup 提示    │ │ 策略判斷錯誤       │
    │ AI 不知當前    │ │ 偏向「不調用」 │ │ has_birth_info    │
    │ 該做什麼      │ │ 缺「該調用」   │ │ = bool(chart_lock)│
    └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘
           │                │                   │
           └────────┬───────┘                   │
                    ▼                           ▼
          ┌──────────────────┐       ┌────────────────────┐
          │  AI 反覆確認      │       │  策略 = GENTLE_INQUIRY│
          │ 「想看哪個系統？」  │ ◄─── │ （一直問，不分析）    │
          └────────┬─────────┘       └────────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  AI 從未排盤      │
          │  chart_lock 為空   │
          └────────┬─────────┘
                   │
        ┌──────────┼──────────┐
        ▼                     ▼
┌──────────────┐     ┌──────────────────┐
│ 根因 #4       │     │ chart_context 空   │
│ history=6 條  │     │ has_birth_info=F   │
│ 生辰被截斷    │     │ → 回到根因 #5 迴圈 │
│ AI 忘記資料   │     └──────────────────┘
└──────────────┘
```

**核心惡性循環：** 根因 #1（缺少指引）→ AI 不排盤 → chart_lock 為空 → 根因 #5 判斷「沒有命盤」→ 策略選「繼續問」→ AI 繼續不排盤 → ∞

---

## 6. 修復計畫

### 修復 A：串流端點統一使用完整 System Prompt（對應根因 #1 + #2）

**目標：** 讓 `chat_consult_stream()` 使用與 `chat_consult()` 同等品質的 System Prompt。

**修改檔案：** `src/api/server.py` — `chat_consult_stream()` 函式

**具體步驟：**

1. 將 `intelligence_core.build_enhanced_system_prompt()` 的 base prompt 來源，從 `get_persona_system_prompt()` 改為 `build_agent_system_prompt()`
2. 加入 `choose_strategy()` 狀態機判斷
3. 將 `choose_strategy()` 回傳的 `conversation_stage` 傳入 `build_agent_system_prompt()`
4. 確保 `TOOL_USE_GUIDELINES`、`MULTI_SYSTEM_INTEGRATION`、`CONVERSATION_STRATEGIES`、`STAGE_SPECIFIC_PROMPTS` 全部被注入

**修改範圍：** `server.py` 串流端點中 system prompt 組裝段落（約 5440-5490 行附近）

**修改方式：**

```python
# 修改前（串流版）
enhanced_prompt = intelligence_core.build_enhanced_system_prompt(
    intelligence_context=intelligence_context,
    include_strategy_hints=True
)

# 修改後（串流版）
from src.prompts.agent_persona import build_agent_system_prompt, choose_strategy

emotional_signals = {
    'distress': intelligence_context.emotional_signal.distress_level > 0.7,
    'curiosity': intelligence_context.emotional_signal.emotion == 'excited',
    'closing': any(kw in message for kw in ['掰掰', '再見', '拜拜', '謝謝', '結束'])
}

conversation_stage = choose_strategy(
    turn_count=user_state.conversation_count,
    has_birth_data=bool(chart_context) or bool(user_data and user_data.get('birth_date')),
    has_chart=bool(chart_context),
    emotional_signals=emotional_signals
)

agent_system_prompt = build_agent_system_prompt(
    user_context=memory_context,
    conversation_stage=conversation_stage
)

# 附加 Intelligence Core 的情緒/策略提示
enhanced_hints = intelligence_core.build_enhanced_system_prompt(
    intelligence_context=intelligence_context,
    include_strategy_hints=True
)
from src.prompts.registry.persona import get_persona_system_prompt
_base = get_persona_system_prompt()
extra_hints = enhanced_hints[len(_base):] if enhanced_hints.startswith(_base) else ""
enhanced_prompt = agent_system_prompt + extra_hints
```

---

### 修復 A2：統一兩個端點的「has_chart / has_birth_data」語意（避免行為分裂）

**目標：** 讓 `chat_consult()`（非串流）與 `chat_consult_stream()`（串流）對「有生辰」「有命盤」的判定一致，避免同一用戶在兩個端點得到不同節奏與策略。

**問題點：** 非串流端點目前常用 `bool(memory_context.get('episodic'))` 之類訊號來推定 `has_chart`，但「有摘要」不等於「有命盤」，容易導致策略誤判。

**建議統一口徑（工程上可驗證）：**

- `has_birth_data`：`user_data` 內已具備足以排至少一套命盤的欄位（例如：生日 + 出生時間 + 性別）。
- `has_chart`：`chart_context` 非空（表示至少有一套 `chart_lock` 已存在、可引用）。

**建議判定示意：**

```python
has_birth_data = bool(
    user_data
    and (user_data.get('birth_date') or user_data.get('gregorian_birth_date'))
    and user_data.get('birth_time')
    and user_data.get('gender')
)

has_chart = bool(chart_context)
```

---

### 修復 B：強化「主動排盤」指令（對應根因 #3 + #6）

**目標：** AI 在收到足夠生辰資料時，立即排盤，不再反覆確認。

**修改檔案：** `src/prompts/agent_persona.py`

**具體步驟：**

1. 在 `TOOL_USE_GUIDELINES` 中加入明確的主動排盤規則：

```python
TOOL_USE_GUIDELINES = """
【工具使用】
有生辰且命盤摘要中沒有該系統的數據 → 排盤。
命盤摘要已有數據 → 直接用，不重排。
需要查運勢 → （目前未註冊對應 Gemini 工具；需新增 fortune 工具或改用既有命盤工具 + 文字分析）。
用戶提過「之前你說」 → search_conversation_history。

回覆時引用具體數據（星名、宮位、四柱），不要泛泛而談。

【主動排盤規則（必須遵守）】
當用戶提供了出生年月日 + 時間 + 性別後：
1. 如果有出生地 → 同時調用 calculate_ziwei 和 calculate_bazi
2. 如果沒有出生地 → 先調用 calculate_bazi（不需要出生地），同時詢問出生地以便排紫微和占星
3. 絕對不要問「想看哪個系統」——直接多系統並排分析
4. 絕對不要問「準備好了嗎」——對方既然提供了資料，就是準備好了
5. 能算的先算，缺的參數再補問，不要等所有參數都齊全才開始

【工具調用判斷優先順序】
A. 命盤摘要已有數據 → 直接引用，不重排
B. 用戶已提供完整生辰 → 立即排盤（至少排八字）
C. 用戶只提供部分資料 → 先排能排的（如靈數只需生日），再補問缺的
D. 用戶完全沒提供資料 → 自然地詢問生辰（融入對話，不像填表單）
"""
```

2. 修改工具定義中的 description（`src/utils/tools.py`）：

```python
# 修改前
"description": "计算紫微斗数命盘。...如果系统提示中的「命盘摘要」已包含紫微数据，则无需重复调用此工具..."

# 修改後
"description": "计算紫微斗数命盘。...如果系统提示中的「命盘摘要」已包含紫微数据，则直接引用已有数据分析即可，无需重复调用。如果命盘摘要中没有紫微数据但用户已提供完整生辰资料，应立即调用此工具排盘。"
```

---

### 修復 C：System Prompt 注入用戶已知資料（對應根因 #4）

**目標：** AI 永遠不會忘記用戶已提供的生辰資料。

**修改檔案：** `src/api/server.py` — `chat_consult_stream()` 函式

**具體步驟：**

1. 在 system prompt 組裝時加入 `user_data` 的生辰欄位：

```python
# 新增：組裝用戶已知資料
user_known_info = ""
if user_data:
    parts = []
    if user_data.get('name') or user_data.get('full_name'):
        parts.append(f"姓名：{user_data.get('name') or user_data.get('full_name')}")
    if user_data.get('birth_date') or user_data.get('gregorian_birth_date'):
        parts.append(f"出生日期：{user_data.get('birth_date') or user_data.get('gregorian_birth_date')}")
    if user_data.get('birth_time'):
        parts.append(f"出生時間：{user_data.get('birth_time')}")
    if user_data.get('gender'):
        parts.append(f"性別：{user_data.get('gender')}")
    if user_data.get('birth_location'):
        parts.append(f"出生地：{user_data.get('birth_location')}")
    if parts:
        user_known_info = "\n【用戶已知資料】\n" + "\n".join(parts)

consult_system = enhanced_prompt + f"""
{user_known_info}

【可用命盤系統】
...
```

2. 增加 history 限制到 12 條（6 輪完整對話）：

```python
# 修改前
history_msgs = db.get_chat_messages(session_id, limit=6)

# 修改後
history_msgs = db.get_chat_messages(session_id, limit=12)
```

---

### 修復 D：修正策略選擇邏輯（對應根因 #5）

**目標：** 策略判斷能正確區分「有生辰但沒命盤」和「沒有生辰」。

**修改檔案：** `src/api/server.py` — `chat_consult_stream()` 中 `UserState` 建構

**具體步驟：**

```python
# 修改前
user_state = UserState(
    is_first_visit=(len(history_msgs) == 0),
    has_complete_birth_info=bool(chart_context),
    ...
)

# 修改後
_has_user_birth_data = bool(chart_context) or bool(
    user_data and (user_data.get('birth_date') or user_data.get('gregorian_birth_date'))
    and user_data.get('birth_time')
)

user_state = UserState(
    is_first_visit=(len(history_msgs) == 0),
    has_complete_birth_info=_has_user_birth_data,
    ...
)
```

---

### 修復 F：加入「伺服器端保險絲」以消除非決定性（強烈建議）

**目標：** 即使 LLM 偶發不發出 tool call，也能保證在資料足夠時至少排出一套命盤，避免再次出現 log 中的「連續 5 輪都在問系統」情況。

**動機：** Prompt 修復能顯著提升成功率，但仍難 100% 保證模型每次都會呼叫工具。加入 deterministic fallback 能把關鍵流程從「模型意願」收回到「工程可保證」。

**建議策略（最小侵入）：**

在 `chat_consult_stream()` 的 tool-use loop 第 0 輪 streaming 完成後：

1. 若 `_iter_function_calls` 為空（模型未呼叫任何工具）
2. 且已從 `user_data` 或 `_extract_user_profile_from_message()` 得到足以排盤的欄位
3. 且 `chart_context` 仍為空（代表尚無可引用命盤）

→ 由 server 直接執行最穩定、需求最少的工具（建議優先 `calculate_bazi`），把結果以 `function_response` 注入 `contents`，然後讓模型進入下一輪（非 streaming）進行解讀。

**保險絲優先順序（務實版）：**

- 若有 `birth_date + birth_time + gender`：先排 `calculate_bazi`
- 若另有 `birth_location`：再排 `calculate_ziwei`
- 若缺 `minute`：先不排占星（或把 minute 視為 0，但需明示「以整點近似」並標示不確定性）

**偽碼示意：**

```python
if _tool_iter == 0 and not _iter_function_calls:
    if has_birth_data and not has_chart:
        # 直接保底排盤（至少八字）
        bazi_args = {
            "year": ..., "month": ..., "day": ...,
            "hour": ..., "minute": 0,
            "gender": ...,
            "longitude": 120.0,
        }
        result = execute_tool("calculate_bazi", bazi_args)
        contents.append(types.Content(
            role="tool",
            parts=[types.Part(function_response=types.FunctionResponse(
                name="calculate_bazi",
                response=result
            ))]
        ))
        # 下一輪讓模型解讀 tool 結果
        continue
```

**注意：** 這個保險絲不取代 prompt，而是「只在模型沒動作時」介入，因此不會讓系統變得過度強制。

---

### 修復 E：改進測試腳本（對應根因 #7）

**目標：** 測試腳本能準確反映真實使用場景並全面驗證所有系統。

**修改檔案：** `scripts/test_conversation_quality.py`

**具體步驟：**

1. **用戶訊息更主動：**
   ```python
   # 修改前
   {"role": "user", "content": "我是1995年3月15日早上8點30分出生的"}
   
   # 修改後
   {"role": "user", "content": "我是女生，1995年3月15日早上8點30分出生在台北，幫我全部系統都看一下"}
   ```

2. **增加 6 個系統的獨立強制測試場景**

3. **AI 回應不截斷**，完整記錄到日誌

4. **增加記憶驗證場景：** 在第 5 輪問「我之前告訴你的生辰資料是什麼？」

5. **增加 tool call 追蹤：** 記錄每次回應中 AI 是否觸發了工具調用

---

## 7. 執行順序與優先級

| 順序 | 修復項 | 根因 | 預期效果 | 影響檔案 | 風險 |
|---|---|---|---|---|---|
| **1** | 修復 A：統一 System Prompt | #1 + #2 | 解決 AI 不主動排盤的核心問題 | `server.py` | 中（需確保不影響非串流端點） |
| **1.5** | 修復 F：伺服器端保險絲 | #1 + #4 + #6 | 把「至少一套排盤」變成工程保證 | `server.py` | 中（需小心避免重複排盤與無限迴圈） |
| **2** | 修復 B：強化主動排盤規則 | #3 + #6 | AI 收到生辰後立即計算 | `agent_persona.py`, `tools.py` | 低 |
| **3** | 修復 C：注入用戶已知資料 | #4 | AI 不再忘記已提供的資料 | `server.py` | 低 |
| **4** | 修復 D：修正策略邏輯 | #5 | 策略選擇更準確 | `server.py` | 低 |
| **5** | 修復 E：改進測試腳本 | #7 | 全面驗證修復效果 | `test_conversation_quality.py` | 無 |

### 預估工作量

| 修復項 | 改動量 | 預估時間 |
|---|---|---|
| 修復 A | ~30 行改動 | 20 分鐘 |
| 修復 F | ~25-50 行改動 | 20-30 分鐘 |
| 修復 B | ~20 行改動 | 10 分鐘 |
| 修復 C | ~20 行改動 | 10 分鐘 |
| 修復 D | ~5 行改動 | 5 分鐘 |
| 修復 E | ~100 行改動 | 30 分鐘 |
| **合計** | **~200-225 行** | **~95-105 分鐘** |

---

## 8. 驗收標準

### 工程必達（功能性驗收）

| # | 驗收項目 | 判定標準 |
|---|---|---|
| 1 | 用戶提供完整生辰後，AI 在同一輪次內排盤 | tool call 記錄中出現 `calculate_*` |
| 2 | 至少排出 2 個系統的命盤（如紫微 + 八字） | 回應中包含具體星曜/四柱數據 |
| 3 | AI 不再問「想看哪個系統？」 | 連續 10 次測試中不出現此問句 |
| 4 | 第 5 輪時 AI 仍記得第 2 輪提供的生辰 | AI 不再重複要求生辰資料 |
| 5 | 離題偵測正常運作 | 非命理話題被正確識別並引導 |

### 品質門檻（生成品質驗收）

| # | 驗收項目 | 判定標準 |
|---|---|---|
| Q1 | 紫微分析包含四化飛星（若已排紫微） | 回應中提及化祿/化權/化科/化忌；或明確說明資料不足/未提供年干導致無法細算 |
| Q2 | 八字分析包含用神/忌神（若已排八字） | 回應中提及用神系統，且能對應到四柱/強弱 |
| Q3 | 所有 6 個系統至少被觸發 1 次（在測試組合中） | 6 個獨立場景各觸發對應系統 tool call |

### 回歸測試

- 非串流端點 `chat_consult()` 行為不受影響
- 現有 pytest 測試全部通過
- 敏感話題攔截功能正常

---

## 附錄 A：系統架構圖

```
┌───────────────────────────────────────────────────────────┐
│                    前端 (Vue.js / Web)                      │
│         POST /api/chat/consult-stream (SSE)                │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                    server.py                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ chat_consult_stream()                                │  │
│  │  1. 敏感話題偵測                                      │  │
│  │  2. 提取用戶 Profile                                  │  │
│  │  3. 載入 chart_locks + memory + fortune_profile       │  │
│  │  4. Intelligence Core 分析                            │  │
│  │  5. ★ 組裝 System Prompt ← 問題在此                   │  │
│  │  6. Gemini 串流生成 + Tool Use 迴圈 (max 5)           │  │
│  │  7. 記憶更新 + 自動摘要                                │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
┌──────────────────┐ ┌───────────┐ ┌──────────────────┐
│  Prompt System    │ │ Tools     │ │ Memory System    │
│                   │ │           │ │                  │
│ persona.py    ←─┐ │ │ 10 tools  │ │ Layer 1: 短期    │
│ agent_persona ←─┤ │ │ 6 calcs   │ │ Layer 2: 摘要    │
│ intelligence  ←─┤ │ │ 4 utils   │ │ Layer 3: 畫像    │
│ strategies    ←─┤ │ │           │ │                  │
│ safety_policy ←─┤ │ │           │ │                  │
│ emotional_intel←─┘ │ │           │ │                  │
└──────────────────┘ └───────────┘ └──────────────────┘
```

## 附錄 B：兩個端點的 Prompt 組裝對比

### 非串流版 `chat_consult()`（正確版本）

```
System Prompt = 
    AGENT_CORE_IDENTITY          ← 核心人設
  + STAGE_SPECIFIC_PROMPTS[stage] ← 階段性指令（動態）
  + CONVERSATION_STRATEGIES       ← 對話節奏
  + EMOTIONAL_INTELLIGENCE_GUIDE  ← 情緒感知
  + ETHICAL_BOUNDARIES            ← 倫理邊界
  + UNCERTAINTY_HANDLING          ← 不確定性處理
  + MULTI_SYSTEM_INTEGRATION      ← 多系統整合
  + TOOL_USE_GUIDELINES           ← 工具使用指引 ⚠️ 關鍵
  + user_context (memory)         ← 用戶上下文
  + Intelligence Core hints       ← 情緒/策略提示
  + off_topic steering            ← 離題引導
  + chart_context                 ← 命盤摘要
  + memory_context                ← 記憶上下文
  + facts                         ← 參考事實
```

### 串流版 `chat_consult_stream()`（缺陷版本）

```
System Prompt = 
    registry/persona.py template  ← 只有人設故事
  + Intelligence Core hints       ← 情緒/策略提示
  + off_topic steering            ← 離題引導
  + chart_context                 ← 命盤摘要
  + memory_context                ← 記憶上下文
  + facts                         ← 參考事實

缺少：
  ❌ STAGE_SPECIFIC_PROMPTS       ← 不知道該做什麼
  ❌ CONVERSATION_STRATEGIES       ← 不知道對話節奏
  ❌ TOOL_USE_GUIDELINES           ← 不知道何時排盤
  ❌ MULTI_SYSTEM_INTEGRATION      ← 不知道如何整合
  ❌ ETHICAL_BOUNDARIES             ← 倫理邊界缺失
  ❌ UNCERTAINTY_HANDLING           ← 不確定性處理缺失
```

---

## 附錄 C：10 個 Gemini Tool 定義總覽

| # | 工具名稱 | 用途 | 必填參數 |
|---|---|---|---|
| 1 | `calculate_ziwei` | 紫微斗數命盤 | birth_date, birth_time, gender, birth_location |
| 2 | `calculate_bazi` | 八字四柱/大運/流年 | year, month, day, hour, gender |
| 3 | `calculate_astrology` | 西洋占星本命盤 | year, month, day, hour, minute |
| 4 | `calculate_numerology` | 生命靈數 | birth_date |
| 5 | `analyze_name` | 姓名學（五格/三才） | surname, given_name |
| 6 | `draw_tarot` | 塔羅牌占卜 | question |
| 7 | `get_location` | 地點經緯度查詢 | location_name |
| 8 | `get_user_profile` | 用戶資料查詢 | user_id |
| 9 | `save_user_insight` | 保存用戶洞察 | user_id, insight_type, content |
| 10 | `search_conversation_history` | 搜索對話歷史 | user_id, keyword |

> **注意：** `FortuneTeller`（流年運勢）和 `ChartExtractor` 在 calculators 中有實作，但**未註冊為 Gemini 工具**，AI 無法調用。

---

*Round 1 分析結束。以下為 Round 2 追加分析。*

---

## Round 2：Fix A~F 實施後的殘留問題分析

> **分析時間：** 2026-02-08 17:00  
> **基準測試：** `logs/conversation_test_20260208_163849.log`  
> **對比基準：** Round 1 修復前 7 個問題 → Round 1 修復後 9 個問題  

### Round 1 修復成效總結

| 修復項 | 解決的問題 | 效果 |
|--------|-----------|------|
| Fix A：統一 System Prompt | AI 不知道「收到資料就該排盤」 | ✅ 有效 — 場景 1 從 3→0 問題 |
| Fix A2：統一狀態判定 | `has_birth_data` 兩端點語意不一 | ✅ 有效 |
| Fix B：強化主動排盤指令 | AI 反覆問「想看哪個系統？」 | ✅ 有效 — 0 次出現 |
| Fix C：工具描述雙向化 | Dedup 提示偏「不調用」 | ✅ 有效 |
| Fix D：歷史窗口 6→12 | AI 忘記第 2 輪的生辰 | ✅ 有效 — 重複詢問生辰 0 次 |
| Fix F：伺服器端熔斷機制 | LLM 不發 tool call 的保底 | ⚠️ 部分有效 — 觸發但結果未整合 |

### Round 2 測試結果 vs Round 1

| 指標 | 修復前 | 修復後 (16:38) | 變化 |
|------|--------|---------------|------|
| 「想看哪個系統？」迴圈 | 7/8 場景 | **0 次** | ✅ 根治 |
| 重複詢問生辰 | 多次 | **0 次** | ✅ 根治 |
| 場景 1（完整生辰流程） | 3 問題 | **0 問題** | ✅ 完美 |
| 缺乏具體命理內容 | 2 次 | **6 次** | 🔴 惡化 |
| 回應過短 | 2 次 | **3 次** | 🟡 微增 |
| 俄語亂碼混入 | 1 次 | **多處** | 🟡 未解 |
| `tool_code` 文字洩漏 | 未觀測 | **出現** | 🔴 新問題 |

### 9 個問題逐一分類（真 Bug vs 假陽性）

| # | 場景-輪 | 用戶訊息 | 問題類型 | 判定 | 理由 |
|---|---------|---------|---------|------|------|
| 1 | 2-1 | "工作壓力好大" | 缺乏具體命理內容 | ❌ 假陽性 | 尚無生辰，AI 正確引導 |
| 2 | 2-2 | "工作適不適合我" | 缺乏具體命理內容 | ❌ 假陽性 | 同上，仍在對話初期 |
| 3 | 2-3 | "1990年7月22日下午2點15分" | 缺乏具體命理內容 | ✅ **真 Bug** | 提供生辰後回應含 `tool_code` 文字 |
| 4 | 3-1 | "你好" | 回應過短 (71字) | ❌ 假陽性 | 問候語，短回覆正確 |
| 5 | 3-2 | "天氣怎麼樣" | 回應過短 (40字) | ❌ 假陽性 | 離題問題，短回覆正確 |
| 6 | 3-3 | "推薦電影" | 回應過短 (49字) | ⚠️ 半真 | AI 不應回答離題內容（推薦了《奧本海默》） |
| 7 | 3-4 | "幫我算算命，1988年5月10日" | 缺乏具體命理內容 | ✅ **真 Bug** | AI 試圖排盤但失敗 |
| 8 | 4-2 | "1992年12月25日凌晨1點" | 缺乏具體命理內容 | ✅ **真 Bug** | AI 不必要地反問日期確認 |
| 9 | 4-3 | "我的事業運如何？" | 缺乏具體命理內容 | ✅ **真 Bug** | 連續 2 輪未排盤 |

**實際有效問題：4 個真 Bug + 1 個半真 + 4 個假陽性**

---

### 根因 #8：Gemini 輸出 `tool_code` 文字取代正式 function_call

**嚴重度：** 🔴 Critical  
**影響場景：** 場景 2 第 3 輪  
**對應修復：** Fix G  

#### 現象

場景 2 第 3 輪 AI 回應中出現：

```
（正在為您排盤中...）

```tool_code
print(default_api.calculate_bazi(year=1990, month=7, day=22, hour=14, minut...
```

這**不是**伺服器程式碼產生的——搜遍整個 codebase 完全沒有 `tool_code` 或 `default_api` 字串。

#### 根因

這是 **Gemini 2.0 Flash 的已知行為**：模型有時會把工具呼叫以「程式碼執行」文字形式輸出（類似 Google AI Studio 的 code execution 功能），而非使用正規的 `function_call` API 機制。

當前 streaming 迴圈的處理邏輯（`server.py:5610-5621`）：

```python
for part in chunk.candidates[0].content.parts:
    if hasattr(part, 'function_call') and part.function_call:
        _iter_function_calls.append(part.function_call)    # ← 正規 function_call
    elif hasattr(part, 'text') and part.text:
        text_chunk = part.text                              # ← tool_code 被當正常文字！
        accumulated_text += text_chunk
        yield f"event: text\ndata: ..."                     # ← 直接串流給用戶
```

**結果：**
1. `tool_code` 垃圾文字直接串流給用戶看到
2. 沒有實際執行任何工具
3. AI 「以為」自己已經呼叫了工具，不會再發出真正的 function_call

#### 修復方案 Fix G

在文字輸出前攔截 `tool_code` 片段：
1. 偵測到 `tool_code` 或 `default_api.calculate_` 模式時，不串流該文字
2. 嘗試從文字中解析出工具名稱和參數，轉為真正的工具呼叫
3. 若解析失敗，至少不洩漏技術垃圾給用戶

---

### 根因 #9：`_extract_birth_time_from_message` 無法解析中文時間表述

**嚴重度：** 🟠 High  
**影響場景：** 場景 2-3、場景 3-4、場景 4-2  
**對應修復：** Fix H  

#### 現象

所有測試場景使用中文時間表述，但伺服器完全無法解析：

| 測試輸入 | 期望解析結果 | 實際解析結果 |
|---------|-------------|-------------|
| "早上8點30分" | `08:30` | `None` ❌ |
| "下午2點15分" | `14:15` | `None` ❌ |
| "凌晨1點" | `01:00` | `None` ❌ |
| "早上9點" | `09:00` | `None` ❌ |

#### 根因

`_extract_birth_time_from_message()`（`server.py:2063`）的正則只匹配 `HH:MM` 格式：

```python
def _extract_birth_time_from_message(message: str) -> Optional[str]:
    match = re.search(r'(\d{1,2})[:：](\d{2})', message)
    if not match:
        return None
```

完全不支援中文時間表述：`早上X點Y分`、`下午X點`、`凌晨X點`。

#### 連鎖影響

1. `_extract_user_profile_from_message()` 提取 `birth_time = None`
2. `save_user()` 儲存 `birth_hour = None, birth_minute = None`
3. 熔斷機制 Fix F 需要 `user_data.get('birth_hour')`，取到 `None` → 使用預設值 12
4. `has_birth_date` 判定：部分邏輯依賴 `birth_time` 存在才算「完整」
5. `choose_strategy()` 可能選錯階段

#### 修復方案 Fix H

擴展正則匹配，支援中文時間表述：
- 基本格式：`X點`、`X點Y分`
- 時段前綴：`早上/上午/中午/下午/晚上/凌晨/半夜`
- 12→24 小時轉換：`下午2點` → `14:00`

---

### 根因 #10：System Prompt 未限制回應語言

**嚴重度：** 🟡 Medium  
**影響場景：** 場景 2-4、2-5、場景 4-4、4-5  
**對應修復：** Fix I  

#### 現象

多處 AI 回應混入俄語詞彙：

| 位置 | 混入的俄語 | 正確中文 |
|------|-----------|---------|
| 場景 2-4 | `обладают`（擁有） | 具備 |
| 場景 2-4 | `нестабильность`（不穩定性） | 不穩定 |
| 場景 2-4 | `творческий подход`（創造性方法） | 創意思維 |
| 場景 2-4 | `гибкость`（彈性） | 彈性 |
| 場景 2-5 | `нестабильность`（不穩定性） | 不穩定 |
| 場景 4-4 | `проявляться`（表現出） | 表現 |
| 場景 4-5 | `очень`（非常） | 非常 |

#### 根因

1. Gemini 2.0 Flash 是多語言模型，訓練語料包含大量俄語
2. System Prompt（`agent_persona.py`）中**沒有任何語言限制**指令
3. 當模型生成命理術語的類比表述時，有時會「漏出」其他語言的詞彙

#### 修復方案 Fix I

在 `AGENT_CORE_IDENTITY` 中加入明確語言限制：
- 全程使用繁體中文回覆
- 禁止混入任何非中文詞彙（除專有名詞外）

---

### 根因 #11：品質檢測邏輯產生假陽性

**嚴重度：** 🟡 Medium  
**影響場景：** 場景 2-1、2-2、3-1、3-2  
**對應修復：** Fix J  

#### 假陽性來源 1：未提供生辰時觸發「缺乏具體命理內容」

檢測邏輯（`test_conversation_quality.py:162-168`）：

```python
if mentions_systems and not has_chart_terms and len(ai_response) > 100:
    issue = "缺乏具體命理內容"
```

問題：當用戶尚未提供生辰資料時，AI 回應中提及命理系統名稱（`紫微`、`八字`等）但自然不會有具體術語（`命宮`、`日主`等）。這是**正常行為**：AI 在引導用戶時會說「我可以用紫微或八字幫你看看」，被誤判為「缺乏具體內容」。

#### 假陽性來源 2：問候/離題回應觸發「回應過短」

檢測邏輯（`test_conversation_quality.py:140-143`）：

```python
if len(ai_response) < 80:
    issue = f"回應過短：僅 {len(ai_response)} 字"
```

問題：對「你好」（71字）、「天氣怎麼樣」（40字）這類訊息，短回覆是正確且期望的行為。

#### 修復方案 Fix J

1. 「缺乏具體命理內容」：增加前提條件——僅在用戶已提供生辰資料的對話輪次中觸發
2. 「回應過短」：豁免問候語和離題問答的短回覆

---

### 根因 #12：AI 對明確時間做不必要的澄清

**嚴重度：** 🟢 Low  
**影響場景：** 場景 4-2、4-3  
**對應修復：** Fix I（合併處理）  

#### 現象

用戶說「1992年12月25日凌晨1點在台南出生」，AI 反問：
> 「你說的凌晨一點，是指12月25日的凌晨一點，還是12月26日的凌晨一點呢？」

這導致連續 2 輪無法排盤。

#### 根因

「12月25日凌晨1點」在中文語境下語義明確——就是 12 月 25 日 01:00。AI 過度「負責」地想確認跨日問題，但這在用戶看來是多餘的。

#### 修復方案

在 System Prompt 加入「不要反問用戶已明確表述的時間」指令。

---

### Round 2 修復計畫總覽

| Fix | 根因 | 目標 | 修改檔案 | 風險 |
|-----|------|------|---------|------|
| **G** | #8 | 攔截 `tool_code` 文字 + 嘗試解析為工具呼叫 | `server.py` | 中 |
| **H** | #9 | 支援中文時間解析（`早上X點Y分`） | `server.py` | 低 |
| **I** | #10 + #12 | System Prompt 加語言限制 + 禁止無謂澄清 | `agent_persona.py` | 低 |
| **J** | #11 | 修正品質檢測假陽性邏輯 | `test_conversation_quality.py` | 低 |

---

*Round 2 分析結束。以下開始實施修復。*
---

## Round 3：Streaming 架構修復（2026-02-08）

### Round 2 測試結果

| 場景 | 對話輪數 | 品質問題 | 問題類型 |
|------|---------|---------|---------|
| 場景 1: 直接提供生辰 | 5 | ✅ 0 | — |
| 場景 2: 事業諮詢 | 5 | ❌ 3 | 俄文混入 ×2, 缺乏命理內容 ×1 |
| 場景 3: 離題偵測 | 4 | ❌ 1 | 重複詢問生辰 |
| 場景 4: 記憶與上下文 | 5 | ❌ 2 | tool_code 洩漏 ×2 |
| **總計** | 19 | **6** | — |

**改善**: Round 1 的 9 個問題降至 6 個（-33%），但仍有 3 類核心問題。

### Round 2 Fix G/I 失效根因分析

#### 為何 Fix G（tool_code 過濾）無效

Fix G 的攔截邏輯在**逐 chunk 檢查**時有 3 個致命缺陷：

1. **跨 chunk 邊界切割**：Gemini streaming 的 chunks 是任意字節切割的，`` ```tool_code `` 可能被拆成 ```` ```tool ```` 和 `_code`，第一個 chunk 不包含完整關鍵字，直接 yield 給使用者
2. **Once yielded, cannot un-send**：SSE 是 fire-and-forget，一旦 yield 出去就無法回收
3. **熔斷 followup 迴圈零過濾**：`followup_response` 的 streaming loop 完全沒有任何 tool_code 攔截

#### 為何 Fix I（語言限制）無效

Fix I 僅在 Prompt 中加入「請用繁體中文」指令，但：

1. Gemini 2.0 Flash 的 multilingual 能力會在長回覆中**自發切換語言**
2. Prompt 指令無法 100% 控制模型輸出
3. **streaming 路徑中的 8 個 yield 點全部未呼叫 `zh_clean_text()`**——此函式只用在非 streaming 路徑

### 根因 #13：Streaming 架構缺乏統一清理層

**嚴重度：** 🔴 Critical  
**影響：** tool_code 洩漏、俄文混入、所有 streaming 品質問題  

streaming endpoint 的架構是 **fire-and-forget**：
```
Gemini chunk → yield 給 client（立即） → 累積到 accumulated_text（僅供儲存）
```

沒有中間層可以做 post-processing。`zh_clean_text()`、`strip_birth_request()` 等清理函式都無法介入。

**修復方案：** 建立 **buffered streaming** 架構 + 統一清理函式。

---

### Fix K：統一 Streaming 清理函式 + 滑動緩衝

**目標：** 解決 tool_code 洩漏 + 俄文混入 + 所有 streaming 文字品質問題

**新增函式：** `_stream_clean_chunk(text)`

清理步驟：
1. 移除 `` ```tool_code...``` `` 區塊
2. 移除散落的 `default_api.xxx()` 呼叫
3. 移除 Cyrillic 字元（U+0400-U+04FF）
4. 移除其他非中英日韓常用字元
5. 清理因移除產生的多餘標點/空白

**架構改造：**

舊架構（Fix G）：
```
chunk → 逐 chunk 檢查關鍵字 → yield（可能遺漏跨邊界的 tool_code）
```

新架構（Fix K）：
```
chunk → 累積到 _stream_buffer（60 字閾值）→ _stream_clean_chunk() → yield 清理後文字
         ↘ 偵測到 tool_code → 等待區塊結束 → 解析為 function_call → 清理殘餘後 yield
```

**修改點：**
- `server.py` 新增 `_stream_clean_chunk()` 函式
- 主 streaming 迴圈（iter 0）：逐 chunk 累積 → 閾值 flush → 清理後 yield
- 非 streaming 迴圈（iter 1+）：整批收集 → 統一清理 → yield

### Fix L：熔斷 Followup 過濾

**目標：** 修復熔斷 followup streaming 迴圈的零過濾問題

舊代碼：`followup_response` 的 chunks 直接 yield，無任何清理。
新代碼：使用同樣的 `_stream_buffer` + `_stream_clean_chunk()` 機制。

---

### Round 3 修復計畫總覽

| Fix | 根因 | 目標 | 修改檔案 | 風險 |
|-----|------|------|---------|------|
| **K** | #13 | 統一 streaming 清理函式 + 滑動緩衝架構 | `server.py` | 中 |
| **L** | #13 | 熔斷 followup 迴圈加入清理 | `server.py` | 低 |

---

*Round 3 分析結束。以下開始實施修復。*

---

## Round 4：工具呼叫核心修復 + 多系統支援（2026-02-08）

### Round 3 測試結果

| 場景 | 問題數 | R2→R3 | 問題類型 |
|------|--------|-------|---------|
| 場景 1 | ✅ 0 | 0→0 | — |
| 場景 2 | ❌ 2 | 3→2 | 重複詢問+缺乏命理 |
| 場景 3 | ❌ 1 | 1→1 | 重複詢問 |
| 場景 4 | ❌ 4 | 2→4 | 缺乏命理×4（工具完全失效） |
| **總計** | **7** | 6→7 | |

**Round 3 成效**：
- ✅ 俄文混入完全消除（Fix K `_stream_clean_chunk` 生效）
- ✅ tool_code 原始格式消除（但殘留清理後骨架文字）
- ❌ AI 仍無法成功排盤——根因在工具呼叫機制本身

### 深度根因分析

#### 根因 #14：熔斷機制參數名稱不匹配（Critical Bug）

**嚴重度：** 🔴 Critical

熔斷機制（Fix F）構建的參數 key 與 executor 期望的 key 不匹配：
- 熔斷送 `birth_year` → executor 期望 `year`
- `_build_user_response()` 回傳 `birth_date="YYYY-MM-DD"` 字串，不是 `birth_year` 數字

`_build_tool_args()` 函式早就正確處理了轉換，但熔斷機制完全沒用它。

#### 根因 #15：熔斷只固定用 `calculate_bazi`

**嚴重度：** 🟡 Medium — 應動態選擇最適合系統

#### 根因 #16：tool_code 解析成功後仍 yield 殘留文字

**嚴重度：** 🟡 Medium — `toolcode defaultapicalculatebazi` 殘留文字仍出現

#### 根因 #17：Prompt 工具指引不夠具體

**嚴重度：** 🟡 Medium — AI 不知道正確的 function calling 參數格式

### Round 4 修復計畫

| Fix | 根因 | 目標 | 修改檔案 |
|-----|------|------|---------|
| **N** | #14, #15 | 熔斷用 `_build_tool_args()` + 多系統選擇 | `server.py` |
| **O** | #16 | 解析成功後不 yield 殘留文字 | `server.py` |
| **P** | #17 | 強化 prompt 工具指引 + 禁止 tool_code + 提供具體呼叫範例 | `agent_persona.py`, `server.py` |

---

*Round 4 分析結束。以下開始實施修復。*