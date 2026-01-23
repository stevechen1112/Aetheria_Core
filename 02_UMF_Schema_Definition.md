# 通用命理格式 (UMF) - Schema 定義 v1.0

本文件定義了 **通用命理格式 (Universal Metaphysics Format, UMF)** 的 JSON 架構。理想情況下，AI Agent 永遠不會看到原始的「星象」或「星座」，以避免偏差或幻覺。相反，它接收這些標準化的 **特徵標籤 (Trait Tags)**。

## 1. 核心畫像向量 (靜態 / 本命)
*源自出生資料。代表「原廠設定」。*

```json
{
  "user_id": "hashed_uid_12345",
  "meta": {
    "calculation_engine_version": "1.2.0",
    "primary_archetype": "策略家 (The Strategist)" 
  },
  "traits": {
    "cognitive_style": { // 認知風格
      "value": "邏輯主導", 
      "spectrum": 0.8, // -1.0 (純感性) 到 1.0 (純邏輯)
      "tags": ["分析型", "懷疑論", "細節導向"]
    },
    "risk_profile": { // 風險畫像
      "value": "保守",
      "spectrum": -0.6, // -1.0 (風險趨避) 到 1.0 (風險愛好)
      "tags": ["尋求安全", "損失厭惡"]
    },
    "social_battery": { // 社交能量
      "value": "選擇性",
      "spectrum": -0.2, // -1.0 (內向) 到 1.0 (外向)
      "tags": ["深度連結", "小群體"]
    },
    "communication_style": { // 溝通風格
      "value": "直接",
      "spectrum": 0.5, // -1.0 (被動/婉轉) 到 1.0 (強勢/直接)
      "tags": ["直率", "誠實", "沒耐心"]
    }
  }
}
```

## 2. 動態能量向量 (時序 / 週期)
*源自當前日期 vs 出生資料。代表「天氣預報」。*

```json
{
  "time_window": "2026-01-23",
  "cycle_type": "Daily",
  "energy_forecast": {
    "general_energy": { // 整體能量
      "level": "低", 
      "description": "修復期",
      "action_advice": "專注於規劃，避免執行。"
    },
    "wealth_luck": { // 財運
      "trend": "波動",
      "score": 3, // 1-10 分
      "warning": "衝動消費風險高。"
    },
    "social_luck": { // 社交運
      "trend": "易衝突",
      "score": 2, // 1-10 分
      "warning": "容易產生誤會。多聽少說。"
    }
  }
}
```

## 3. 映射邏輯範例 ("翻譯機")

### 3.1 輸入：占星 (Astrology)
- **原始資料：** 火星在牡羊座 (第一宮)
- **UMF 輸出：** 
  - `traits.risk_profile.spectrum` += 0.4
  - `traits.communication_style.tags` 加入 "精力充沛", "發起者"

### 3.2 輸入：八字 (BaZi)
- **原始資料：** 日主 = 甲木 (陽木), 身弱, 七殺重
- **UMF 輸出：**
  - `traits.cognitive_style.tags` 加入 "自律", "壓力敏感"
  - `traits.risk_profile.spectrum` -= 0.3 (因為「身弱」需要支持)

### 3.3 輸入：紫微斗數 (Purple Star)
- **原始資料：** 命宮 = 七殺, 遷移宮 = 紫微
- **UMF 輸出：**
  - `traits.risk_profile.spectrum` += 0.8 (權重覆寫：七殺 Action-driven)
  - `traits.communication_style.tags` 加入 "發號施令", "獨來獨往"
  - `traits.social_battery.value` 改為 "High Output" (因遷移宮強勢)

### 3.4 輸入：塔羅 (Tarot) - *臨時上下文*
*塔羅不修改靜態畫像，而是產生一個有效期為 24小時的 `context_modifier`。*
- **原始資料：** 抽牌 = 隱士 (The Hermit, 逆位)
- **UMF 輸出 (Session Context)：**
  - `current_mood`: "Isolation/Loneliness"
  - `modifiers`: 
    - `social_battery.spectrum` -= 0.5 (臨時覆寫：不想說話) 
    - `response_style`: "Gentle/Low-Energy" (指示 AI 降低能量)

---
**注意：** AI Agent 的邏輯使用 `trends` (趨勢)、`scores` (分數) 和 `tags` (標籤) 來生成自然語言建議，它並不知道來源是火星、甲木還是七殺。
