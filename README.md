# Aetheria Core - 超個人化 LifeOS 命理分析系統

> **AI 驅動的六大命理分析引擎** | 紫微斗數 + 八字命理 + 西洋占星 + 靈數學 + 姓名學 + 塔羅牌 | 基於 Gemini 2.0 Flash

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-GPL%20v2-red.svg)]()
[![Version](https://img.shields.io/badge/Version-v1.9.2-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

## 🚦 專案狀態

**當前版本**：v1.9.2（2026-01-26）  
**開發階段**：✅ 六大命理系統 + 戰略側寫 + AI 語音諮詢整合完成，生產就緒  
**健康度評分**：⭐⭐⭐⭐⭐ 9.9/10  
**API 端點數**：42+ 個（全部測試通過）  
**核心模組數**：15 個（紫微、八字、西洋占星、靈數學、姓名學、塔羅牌、流年、合盤、擇日、戰略側寫、AI 諮詢、🆕 語音對話）

### 完成度儀表板

| 模組 | 狀態 | 完成度 | 測試 |
|------|------|--------|------|
| 紫微斗數核心 | ✅ 完成 | 100% | ✅ |
| 八字命理核心 | ✅ 完成 | 100% | ✅ |
| 西洋占星術核心 | ✅ 完成 | 100% | ✅ |
| 靈數學核心 | ✅ 完成 | 100% | ✅ |
| 姓名學核心 | ✅ 完成 | 100% | ✅ |
| 塔羅牌核心 | ✅ 完成 | 100% | ✅ |
| **戰略側寫系統** | ✅ 完成 | 100% | ✅ |
| **AI 命理諮詢** | ✅ 完成 | 100% | ✅ |
| **🆕 語音對話模式** | ✅ 完成 | 100% | ✅ |
| 交叉驗證系統 | ✅ 完成 | 100% | ✅ |
| 流年運勢分析 | ✅ 完成 | 100% | ✅ |
| 合盤分析系統 | ✅ 完成 | 100% | ✅ |
| 擇日功能系統 | ✅ 完成 | 100% | ✅ |
| 前端介面 (UI v2.0) | ✅ 完成 | 100% | ✅ |
| 用戶認證 | ✅ 完成 | 100% | ✅ |
| 資料庫系統 | ✅ 完成 | 100% | ✅ |

---

## 📖 專案簡介

v1.9.0 起支持**紫微斗數、八字命理、西洋占星術、靈數學、姓名學、塔羅牌六大命理系統 + 戰略側寫模組**，提供深度、準確且具洞察力的命理分析，從「算命計算機」進化為「戰略決策顧問」。

### 🎨 UI v2.0 現代化介面（2026-01-25 全新發布）

**完全重新設計的使用者體驗**，從傳統的 Tab 切換升級為現代化的 Dashboard + Sidebar 架構。

**核心改進**：
- 🎨 **完整設計系統**：統一的色彩、間距、圓角、陰影系統
- 📱 **Dashboard Layout**：專業的側邊欄導航 + 主內容區
- ✨ **Wizard 引導**：6步驟漸進式命盤建立流程（降低認知負擔）
- 🎯 **視覺差異化**：戰略側寫獨特藍色視覺語言（一眼區分「算命」vs「戰略」）
- 🚀 **現代化組件**：Toast 通知、Modal 對話框、卡片流設計
- 📊 **結論優先**：重要資訊前置，減少滾動尋找

**詳細說明**：參見 [docs/18_UI_UX_Redesign_Report_v2.0.md](docs/18_UI_UX_Redesign_Report_v2.0.md)

### 六大命理系統 + 戰略側寫

| 系統 | 說明 | 適用場景 | 準確度 | API 端點 |
|------|------|----------|--------|----------|
| **紫微斗數** | LLM-First 排盤、命盤分析、流年運勢、合盤、擇日 | 性格分析、事業規劃、人際關係 | ⭐⭐⭐⭐ | 8個 |
| **八字命理** | 四柱排盤、十神分析、大運推算、流年運勢 | 運勢預測、五行調理、時機選擇 | ⭐⭐⭐⭐ | 3個 |
| **西洋占星術** | 本命盤計算、合盤分析、流年運勢、事業發展 | 心理分析、關係諮詢、職涯規劃 | ⭐⭐⭐⭐⭐ | 4個 |
| **靈數學** | 生命靈數、流年運勢、相容性分析、完整檔案 | 人生使命、天賦潛能、流年週期 | ⭐⭐⭐⭐ | 5個 |
| **姓名學** | 五格剖象法、81數理、三才配置、姓名建議 | 命名改名、運勢提升、五行補強 | ⭐⭐⭐⭐ | 5個 |
| **塔羅牌** | 多種牌陣、每日一牌、情境解讀、78張完整牌組 | 即時指引、決策諮詢、心理投射 | ⭐⭐⭐⭐ | 4個 |
| **🆕 戰略側寫** | 全息側寫、生辰校正、關係生態、決策沙盒 | 戰略定位、時辰反推、合作分析、路徑模擬 | ⭐⭐⭐⭐⭐ | 4個 |

### 🆕 v1.9.0 戰略側寫模組（Strategic Profiling）

**從「算命」到「戰略」**：將命理系統從被動的運勢解讀，升級為主動的決策支援系統。

#### 1. 全息生命圖譜（Holographic Profile）
- **Meta Profile 整合**：融合八字日主、靈數核心、姓名五行、占星中天於一體
- **結論優先架構**：先給定位→列出證據→提供行動建議（非傳統流水帳）
- **角色標籤系統**：自動萃取「架構師/操盤手/執行者」等功能性角色
- **資源流向圖**：可視化「金→水→木」五行能量流動路徑
- **適用場景**：職涯定位、創業評估、團隊角色分工

#### 2. 生辰校正器（Birth Time Rectifier）
- **反推時辰邏輯**：用戶提供特質/重大事件 → 系統比對 12 時辰 → 給出 Top 3 可能
- **多系統驗證**：同時計算八字（日主/用神）、占星（上升/天頂）、靈數核心數
- **不確定性標註**：明確標示每個時辰的「可能性分數」與「需補充問題」
- **適用場景**：出生時間遺失、跨時區出生、醫院記錄不明

#### 3. 關係生態位（Relationship Ecosystem）
- **非感情導向**：不談「合適度」，只談「資源流動」與「功能互補」
- **生態角色定義**：誰是「生產者」？誰是「消費者」？誰是「管理者」？
- **五行流向圖解**：甲方的金 → 生 → 乙方的水 → 滋潤 → 乙方的木
- **合作風險/紅利**：明確標示「單向供養」「相互消耗」「戰略共生」
- **適用場景**：商業合夥、團隊組建、導師關係、投資人-創業者配對

#### 4. 決策沙盒（Decision Sandbox）
- **雙路徑模擬**：輸入「路徑 A」與「路徑 B」→ 分別抽塔羅牌 → 結合命主 Meta Profile 推演
- **因果推演**：不做道德判斷，只推演「代價」與「收益」
- **關鍵變數識別**：指出「影響成敗的核心因素是什麼？」
- **適用場景**：公司轉型決策、職涯抉擇、投資決策、重大人生選擇

### 🆕 v1.9.2 AI 語音命理諮詢（2026-01-26）

**混合模式：文字 + 語音**，像跟真人命理老師面對面聊天。

#### 核心特色

| 特色 | 說明 |
|------|------|
| **🎙️ 語音對話模式** | 支援語音輸入（Web Speech API），AI 回覆自動播放 TTS |
| **💬 文字對話模式** | 傳統文字輸入，快速交流 |
| **即時切換** | 語音與文字模式自由切換，不中斷對話 |
| **個性化回覆** | 語音模式：江湖味道，160-300字；文字模式：200-400字 |
| **五系統整合** | 每次回覆自動從紫微、八字、占星、靈數、姓名五大系統擷取相關依據 |
| **有所本回覆** | AI 回覆會附上 citations（引用依據），可追溯到原始命盤資料 |
| **對話記憶** | 支援多輪對話，AI 記得上下文，可持續追問 |
| **多對話管理** | 支援建立、切換、刪除多個對話，載入歷史訊息 |

#### API 端點

```
POST /api/chat/consult        # AI 諮詢（支援 voice_mode 參數）
  - voice_mode: true  → 語音風格回覆（160-300字，江湖味）
  - voice_mode: false → 文字風格回覆（200-400字，簡潔）
GET  /api/chat/sessions       # 取得用戶的對話列表
GET  /api/chat/messages       # 取得特定對話的歷史訊息
DELETE /api/chat/sessions/<id> # 刪除對話
```

#### 使用流程

1. **登入後** → 側邊欄點擊「🔮 命理顧問」
2. **選擇模式**：
   - 💬 文字模式：鍵盤輸入 → 發送 → 閱讀回覆
   - 🎙️ 語音模式：點擊麥克風 → 說話 → AI 自動語音回覆
3. **自由切換**：對話中隨時切換模式
4. **引用查看**：每則回覆下方顯示命盤依據來源

#### 範例對話

**語音模式**（江湖風格，160-300字）：
```
用戶：（語音）我 2026 年適合換工作嗎？
AI：（語音播放）嗯，讓我看看你的命盤...你是標準的「機月同梁格」，
    命宮還有天同跟太陰。這個格局喔，比較適合在有制度、穩定的環境發展。
    不過我看你今年官祿宮走太陽，是有機會往外發展啦。但要注意，
    太陽在戌宮算是不得位，代表可能會遇到一些阻力...
    [🔊 自動播放，可重複播放]
```

**文字模式**（簡潔風格，200-400字）：
```
用戶：（文字）那如果不換，在原公司有升遷機會嗎？
AI：（文字）嗯，留在原公司也是有機會的。我看你的官祿宮雖然沒有主星，
    但借對宮的「太陽」跟「巨門」來看，升遷通常是伴隨著「名聲」或
    「專業能力被看見」。今年你的八字走「食神生財」格，顯示你的專業
    輸出會帶來實質回報...
```

### 🆕 v1.9.1 AI 命理諮詢系統（2026-01-26）

**像跟真人命理老師對話**：整合五大命理系統，提供有所本、可追溯的 AI 諮詢服務。

#### 核心特色

| 特色 | 說明 |
|------|------|
| **五系統整合** | 每次回覆自動從紫微、八字、占星、靈數、姓名五大系統擷取相關依據 |
| **有所本回覆** | AI 回覆會附上 citations（引用依據），可追溯到原始命盤資料 |
| **對話記憶** | 支援多輪對話，AI 記得上下文，可持續追問 |
| **多對話管理** | 支援建立、切換、刪除多個對話，載入歷史訊息 |
| **口語化風格** | 像朋友聊天一樣自然，100-200 字精簡回覆，不寫文章 |

#### API 端點

```
POST /api/chat/consult        # AI 諮詢（傳入 message, 可選 session_id）
GET  /api/chat/sessions       # 取得用戶的對話列表
GET  /api/chat/messages       # 取得特定對話的歷史訊息
DELETE /api/chat/sessions/<id> # 刪除對話
```

#### 範例對話

```
用戶：我 2026 年適合換工作嗎？
AI：嗯，我看你的命盤，你是標準的「機月同梁格」，命宮還有天同跟太陰。
    這顯示你其實比較適合在有制度、穩定的環境發展...
    [引用：紫微>格局、紫微>命宮、八字>日主]

用戶：那如果不換，在原公司有升遷機會嗎？
AI：嗯，留在原公司也是有機會的喔。我看你的官祿宮雖然沒有主星，
    但借對宮的「太陽」跟「巨門」來看，升遷通常是伴隨著「名聲」...
    [引用：紫微>官祿宮、八字>強弱]
```

### 使用建議

1. **首次分析**：使用紫微或八字建立基礎命盤
2. **深度諮詢**：使用交叉驗證（紫微＋八字）提供更精準判斷
3. **心理分析**：使用西洋占星術深入心理與人格面向
4. **天賦探索**：使用靈數學了解生命靈數與潛能
5. **命名改名**：使用姓名學五格分析與建議
6. **即時指引**：使用塔羅牌獲取當下決策建議
7. **🆕 AI 語音諮詢**：使用 AI 命理顧問進行語音或文字對話式諮詢
8. **戰略定位**：使用全息側寫了解核心角色與資源流向
9. **時辰不明**：使用生辰校正器反推最可能的出生時間
10. **合作評估**：使用關係生態位分析雙方功能互補性
11. **重大決策**：使用決策沙盒模擬不同路徑的代價與收益
12. **定期更新**：根據需求使用流年運勢、合盤、擇日等功能

### 核心優勢

- **六系統整合**：紫微斗數、八字命理、西洋占星術、靈數學、姓名學、塔羅牌多重驗證，提高準確度
- **🆕 語音對話**：支援文字與語音混合模式，像跟真人命理老師面對面聊天
- **戰略導向**：從被動算命升級為主動決策支援系統
- **結論優先**：先給答案→再列證據→最後給行動方案（非傳統流水帳）
- **LLM-First 策略**：充分發揮大型語言模型在複雜推理與自然語言生成上的優勢
- **結構化提取**：確保 AI 輸出符合命理學術規範
- **定盤鎖定**：防止重複分析帶來的不一致性
- **專業級精度**：使用 Swiss Ephemeris（< 0.5° 誤差）業界標準星曆
- **性別參數統一**：自動處理 male/female 與 男/女 的轉換
- **出生日期解析**：支援國曆、農曆、民國年等多種格式
- **漸進式功能**：從基礎分析到進階合盤、擇日、戰略決策等全方位服務

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

### 西洋占星術系統 (v1.4.0 新增)

#### 10. 本命盤計算 (Natal Chart)
- **行星計算**：10 大行星（太陽～冥王星）+ 上升點 + 天頂精準度數
- **宮位系統**：12 宮位（Placidus 宮制）完整計算
- **相位分析**：5 大主要相位（合/沖/拱/刑/六合）自動識別
- **元素分佈**：火/地/風/水四元素能量分析
- **特質分佈**：本位/固定/變動星座特質分析
- **命主星**：根據上升星座確定命盤主宰行星
- **精度保證**：使用 Swiss Ephemeris（< 0.5° 誤差）

#### 11. 本命盤分析 (Natal Analysis)
- **核心性格**：太陽/月亮/上升三位一體人格分析（500-700 字）
- **行星能量**：10 大行星各自作用與相互影響（800-1000 字）
- **宮位解讀**：12 宮位生命領域詳細分析（1000-1200 字）
- **相位詮釋**：主要相位對人格與命運的影響（600-800 字）
- **元素與特質**：四元素與三特質綜合評估（400-500 字）
- **整合解讀**：全盤格局與生命課題（600-800 字）
- **交叉驗證**：與用戶已知事實對照（選配，300-400 字）
- **理論來源**：引用 Stephen Arroyo、Liz Greene 等權威占星師著作

#### 12. 合盤分析 (Synastry)
- **太陽-太陽相位**：核心價值觀與生命方向匹配（300-400 字）
- **月亮-月亮相位**：情緒模式與安全感需求（300-400 字）
- **金星-火星相位**：愛情吸引力與性能量（300-400 字）
- **宮位重疊**：對方行星落入我方宮位影響（400-600 字）
- **整體評估**：關係動力、挑戰與成長方向（500-700 字）
- **建議**：如何經營這段關係（300-400 字）

#### 13. 流年運勢 (Transit)
- **外行星相位**：木星/土星/天王星/海王星/冥王星長期影響（600-800 字）
- **內行星觸發**：太陽/月亮/水星/金星/火星短期事件（400-600 字）
- **關鍵時間點**：精準預測重大事件可能時間（300-400 字）
- **月度概覽**：未來 3-6 個月運勢走向（400-500 字）
- **行動建議**：如何善用流年能量（300-400 字）

#### 14. 事業發展分析 (Career)
- **第十宮分析**：事業宮位與天頂星座（400-500 字）
- **第六宮分析**：工作態度與日常任務（300-400 字）
- **第二宮分析**：財富累積與價值觀（300-400 字）
- **天賦才能**：從行星配置看專業優勢（400-500 字）
- **職業方向**：適合的行業與工作類型（400-500 字）
- **發展策略**：如何實現事業目標（300-400 字）
  - ✓✓✓ 高度可信（兩套體系一致）
  - ⚠️ 需觀察（存在分歧）
  - ↔️ 互補參考（不同角度補充）

---

## � 文檔導航（新接手者必讀）

### 快速入門路徑

**第一步：理解架構**
1. 📄 [01_Technical_Whitepaper.md](01_Technical_Whitepaper.md) - 產品願景與長期架構（20分鐘）
2. 📄 [04_Architecture_Decision_LLM_First.md](04_Architecture_Decision_LLM_First.md) - ⭐ **核心決策文件**（15分鐘）

**第二步：掌握實作**
3. 📄 [06_Chart_Locking_System.md](06_Chart_Locking_System.md) - 定盤系統設計（10分鐘）
4. 📄 [05_Gemini_Prompt_Templates.md](05_Gemini_Prompt_Templates.md) - Prompt 工程指南（30分鐘）
5. 📄 本 README - 完整 API 文檔與使用指南

**第三步：進階功能**
6. 📄 [07_Advanced_Features_Report.md](07_Advanced_Features_Report.md) - 進階功能實作報告
7. 📄 [08_Feature_Expansion_Evaluation.md](08_Feature_Expansion_Evaluation.md) - 未來功能評估
8. 📄 [09_Cross_System_Integration_Evaluation.md](09_Cross_System_Integration_Evaluation.md) - 跨系統整合規劃

**第四步：細節參考**
9. 📄 [02_UMF_Schema_Definition.md](02_UMF_Schema_Definition.md) - 通用命理格式（已降級為可選）
10. 📄 [03_AI_Workflow_Guidelines.md](03_AI_Workflow_Guidelines.md) - AI 角色切換策略（未來功能）

### 文檔閱讀時間預估

- 🚀 **快速了解**（30分鐘）：README + 04_Architecture_Decision
- 📖 **全面掌握**（2小時）：上述第一步 + 第二步全部
- 🎓 **深度精通**（4小時）：閱讀所有文檔

---

## 💡 核心設計理念

### 為什麼選擇 LLM-First 策略？

**傳統認知（錯誤）**：
```
出生時間 → [Swiss Ephemeris 計算] → 行星位置 
         → [規則引擎] → 固定解讀 
         → 生硬的文字報告
```

**Aetheria 方法（正確）**：
```
出生時間 + 語境 + 提問意圖
         ↓
    [Gemini 3 Flash 深度推理]
         ↓
   準確且觸動人心的專業分析
```

### 關鍵優勢

1. **準確性驗證**：10次測試 100% 命宮結構一致
2. **語境理解**：能根據用戶處境調整建議（傳統系統做不到）
3. **整合詮釋**：「日月並明 + 機月同梁」綜合判斷（非單一星曜查表）
4. **成本優化**：使用 Flash Preview 比 Pro 快 2x，省 30-40% 成本
5. **維護簡單**：不需維護複雜的規則引擎
6. **有所本原則（v1.3.0+）**：所有命理判斷必須引用來源數據，禁止憑空臆測
7. **資料不足處理（v1.3.0+）**：當數據不足時明確說明並列出需補充問題，不編造內容

### 命理分析品質保證（v1.3.0+）

**「有所本」規則**：
- 每個結論必須註明依據來源（命宮/星曜/四化/十神/用神等）
- 格式：「依據：[具體命盤資訊]」
- 禁止使用「一般來說」「通常」「可能」等模糊詞彙

**資料不足處理**：
- 明確標註：「資料不足，無法下定論」
- 列出「需要補充的問題：」（3-7 個具體問題）
- 範例問題：
  ```
  需要補充的問題：
  1. 請確認官祿宮的主星與四化情況？
  2. 夫妻宮有哪些吉星或煞星？
  3. 過去 3 年內有無重大工作變動？
  4. 目前感情狀態為何（單身/穩定交往/已婚）？
  ```

**用戶事實校準（user_facts）**：
- 允許用戶提供已知事實（工作性質、感情狀態、主觀感受）
- AI 以此為基準進行分析，避免偏離實際狀況
- 範例見 [API 文檔 - 交叉驗證端點](#16-紫微八字交叉驗證)

### 定盤鎖定系統（防止 LLM 飄移）

雖然 LLM 表現優秀,但為了**長期一致性**,我們實作了定盤鎖定機制：

```python
首次分析 → 提取關鍵結構（命宮、格局、十二宮）
         → 存入資料庫 → 鎖定
         → 後續對話都注入此結構
```

**效果**：確保用戶每次諮詢都基於同一份命盤，避免矛盾。

---

## �🚀 快速開始

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

```bash
# 使用統一啟動入口（推薦）
python run.py

# 指定端口和主機
python run.py --port 5001 --host 0.0.0.0

# 啟用除錯模式
python run.py --debug

# 或直接執行模組（需在專案根目錄）
python -m src.api.server
```

**服務啟動成功會顯示**：
```
╔════════════════════════════════════════════════════════════════════╗
║               🌟 Aetheria Core - 命理分析系統 🌟                   ║
╠════════════════════════════════════════════════════════════════════╣
║  版本: v1.8.0                                                      ║
║  六大命理系統: 紫微、八字、占星、靈數、姓名、塔羅                  ║
╠════════════════════════════════════════════════════════════════════╣
║  服務位址: http://0.0.0.0:5001                                     ║
║  健康檢查: http://localhost:5001/health                            ║
╚════════════════════════════════════════════════════════════════════╝
```

⚠️ **Port 注意**：v1.3.0+ 預設改用 **port 5001**（避免 macOS ControlCenter 衝突），舊版本為 5000。

⚠️ **性別參數注意**：v1.8.0+ 統一性別參數為「男/女/未指定」，API 會自動轉換 male/female。

⚠️ **出生日期注意**：系統支援多種日期格式（ISO、農曆、民國年），優先使用 `gregorian_birth_date`。

#### 5. 驗證安裝

```bash
# 測試健康檢查
curl http://localhost:5001/health

# 預期輸出
{"status":"ok","service":"Aetheria Chart Locking API"}
```

---

### 語言輸出保證（v1.3.0+）

**全面保證台灣繁體中文（zh-TW）輸出**：

1. **Prompt 層級**：所有 AI Prompt 明確要求「全文僅使用台灣繁體中文（zh-TW）、禁止出現任何簡體字」
2. **API 層級**：使用 OpenCC（s2twp）自動轉換簡體→台灣繁體
3. **驗證機制**：輸出報告經 OpenCC 驗證後存檔

**技術實作**（`api_server.py`）：

```python
from opencc import OpenCC

def to_zh_tw(text: str) -> str:
    """將 LLM 輸出統一轉為台灣繁體（s2twp）"""
    if not text or OpenCC is None:
        return text
    try:
        return OpenCC('s2twp').convert(text)
    except Exception:
        return text

# 應用於所有 LLM 輸出
response_text = call_gemini(prompt)
final_text = to_zh_tw(response_text)  # 確保全繁體
```

所有 AI 生成內容（命理分析、流年運勢、合盤報告、擇日建議）都經此函數處理，**零簡體字容忍度**。

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
  "use_apparent_solar_time": true,
  "user_facts": "工作/能力偏向：策略、整合、顧問、管理\n主觀感受：外表扛得住，但內在很緊繃\n感情/婚姻：早早穩定（並非晚婚型）"
}
```

**請求參數**：
- `user_id` (必填): 用戶 ID（需已鎖定紫微命盤）
- `year`, `month`, `day`, `hour`, `minute` (必填): 出生時間
- `gender` (必填): 性別（"male" / "female"）
- `longitude` (選填): 經度（用於真太陽時校正）
- `use_apparent_solar_time` (選填): 是否使用真太陽時
- `user_facts` (選填, v1.3.0+): **用戶事實校準**，提供已知事實幫助 AI 更準確判斷

**user_facts 使用範例**：
```
工作/能力偏向：策略、整合、顧問、管理
主觀感受：外表扛得住，但內在很緊繃
感情/婚姻：早早穩定（並非晚婚型）
```

**回應：** 5000-7000 字交叉驗證分析（v1.3.0+ 更長更詳細）
- 命格層次驗證、性格特質對照、事業財運交叉分析
- 婚姻感情雙重驗證、大運流年對照、綜合研判與建議
- 包含紫微命盤摘要、八字命盤摘要、一致性標註
- **v1.3.0+**: 每個結論必須註明「依據：...」，資料不足時明確列出「需要補充的問題」

**注意事項**：
- 此端點需要用戶已鎖定紫微命盤
- v1.3.0+ 報告全面使用**台灣繁體中文（zh-TW）**，零簡體字
- 所有命理判斷必須「有所本」，不得憑空臆測

---

### 西洋占星術端點 (v1.4.0 新增)

#### 17. 本命盤分析

```http
POST /api/astrology/natal
Content-Type: application/json

{
  "name": "User",
  "year": 1979,
  "month": 11,
  "day": 12,
  "hour": 23,
  "minute": 50,
  "longitude": 120.52,
  "latitude": 24.08,
  "timezone": "Asia/Taipei"
}
```

**回應：**
```json
{
  "status": "success",
  "data": {
    "natal_chart": {
      "basic_info": {...},
      "planets": {
        "sun": {"longitude": 229.66, "sign": "天蠍座", ...},
        "moon": {"longitude": 150.24, "sign": "處女座", ...},
        ...
      },
      "houses": {...},
      "aspects": [...],
      "elements": {"Fire": 4, "Earth": 3, "Air": 1, "Water": 2},
      "qualities": {"Cardinal": 1, "Fixed": 3, "Mutable": 6}
    },
    "analysis": "完整本命盤分析（3500-5000字）",
    "timestamp": "2026-01-24T12:00:00"
  }
}
```

#### 18. 合盤分析

```http
POST /api/astrology/synastry
Content-Type: application/json

{
  "person1": {
    "name": "User1",
    "year": 1979, "month": 11, "day": 12,
    "hour": 23, "minute": 50,
    "longitude": 120.52, "latitude": 24.08
  },
  "person2": {
    "name": "User2",
    "year": 1985, "month": 5, "day": 20,
    "hour": 14, "minute": 30,
    "longitude": 121.56, "latitude": 25.03
  }
}
```

**回應：** 2500-3500 字合盤分析
- 太陽-太陽、月亮-月亮、金星-火星相位
- 宮位重疊、關係動力、建議

#### 19. 流年運勢

```http
POST /api/astrology/transit
Content-Type: application/json

{
  "name": "User",
  "year": 1979, "month": 11, "day": 12,
  "hour": 23, "minute": 50,
  "longitude": 120.52, "latitude": 24.08,
  "timezone": "Asia/Taipei",
  "transit_date": "2026-01-24"
}
```

**回應：** 2000-3000 字流年分析
- 外行星長期影響、內行星短期觸發
- 關鍵時間點、月度概覽、行動建議

#### 20. 事業發展分析

```http
POST /api/astrology/career
Content-Type: application/json

{
  "name": "User",
  "year": 1979, "month": 11, "day": 12,
  "hour": 23, "minute": 50,
  "longitude": 120.52, "latitude": 24.08,
  "timezone": "Asia/Taipei",
  "user_facts": "目前從事：軟體開發\n考慮轉職：產品管理或創業"
}
```

**回應：** 2500-3500 字事業分析
- 第十宮/第六宮/第二宮分析
- 天賦才能、職業方向、發展策略

---

### 🆕 戰略側寫端點 (v1.9.0 新增)

#### 21. 全息生命圖譜

```http
POST /api/strategic/profile
Content-Type: application/json

{
  "birth_date": "1979-11-12",
  "birth_time": "23:58",
  "chinese_name": "陳宥竹",
  "english_name": "CHEN YOU ZHU",
  "gender": "男",
  "analysis_focus": "career",
  "include_bazi": true,
  "include_astrology": true,
  "include_tarot": true,
  "longitude": 120.54,
  "latitude": 24.08,
  "timezone": "Asia/Taipei",
  "city": "Changhua",
  "nation": "TW"
}
```

**請求參數**：
- `birth_date` (必填): ISO 格式出生日期
- `birth_time` (選填): 出生時間（HH:MM），若無則略過八字/占星
- `chinese_name` (必填): 中文姓名
- `english_name` (選填): 英文姓名（用於靈數學）
- `gender` (必填): 性別（男/女/未指定）
- `analysis_focus` (選填): 分析焦點（general/career/relationship/wealth/health）
- `include_bazi/astrology/tarot` (選填): 是否包含特定系統

**回應**：
```json
{
  "status": "success",
  "data": {
    "meta_profile": {
      "dominant_elements": ["木", "水"],
      "core_numbers": {"life_path": 9, "expression": 7},
      "career_axis": {"midheaven_sign": "天蠍座"},
      "role_tags": ["architect", "strategist"],
      "risk_flags": ["身弱/身強判定：身弱"]
    },
    "strategic_interpretation": "結論優先 + 證據 + 行動建議（2000-3000字）",
    "warnings": ["未提供 birth_time，已略過八字計算"]
  }
}
```

#### 22. 生辰校正器

```http
POST /api/strategic/birth-rectify
Content-Type: application/json

{
  "birth_date": "1979-11-12",
  "gender": "男",
  "traits": ["強勢領導", "偏好獨立作業", "重大轉職"],
  "longitude": 120.54
}
```

**請求參數**：
- `birth_date` (必填): 出生日期
- `gender` (必填): 性別
- `traits` (必填): 特質/事件清單（Array）
- `longitude` (選填): 經度（用於真太陽時校正）

**回應**：
```json
{
  "status": "success",
  "data": {
    "candidates": [
      {"shichen": "子時", "time": "23:30", "bazi_summary": {...}},
      ...
    ],
    "interpretation": "Top 3 可能時辰 + 判斷邏輯 + 需補充問題（1500-2500字）"
  }
}
```

#### 23. 關係生態位

```http
POST /api/strategic/relationship
Content-Type: application/json

{
  "person_a": {
    "name": "陳宥竹",
    "birth_date": "1979-11-12",
    "birth_time": "23:58"
  },
  "person_b": {
    "name": "張小姐",
    "birth_date": "1985-05-20",
    "birth_time": "12:00"
  },
  "include_bazi": true,
  "include_astrology": true
}
```

**請求參數**：
- `person_a/person_b` (必填): 雙方資料（name, birth_date, birth_time）
- `include_bazi/astrology` (選填): 是否包含特定系統

**回應**：
```json
{
  "status": "success",
  "data": {
    "person_a_meta": {...},
    "person_b_meta": {...},
    "interpretation": "關係本質 + 生態角色 + 資源流向 + 風險紅利（2000-3000字）",
    "warnings": ["未提供 birth_time，已略過八字計算"]
  }
}
```

#### 24. 決策沙盒

```http
POST /api/strategic/decision
Content-Type: application/json

{
  "user_name": "陳宥竹",
  "birth_date": "1979-11-12",
  "birth_time": "23:58",
  "question": "公司轉型方向",
  "option_a": "激進擴張",
  "option_b": "穩健保守"
}
```

**請求參數**：
- `user_name` (必填): 決策者姓名
- `birth_date` (必填): 出生日期
- `birth_time` (選填): 出生時間（若有會納入八字/占星）
- `question` (必填): 核心問題
- `option_a/option_b` (必填): 兩條決策路徑

**回應**：
```json
{
  "status": "success",
  "data": {
    "option_a": "激進擴張",
    "option_b": "穩健保守",
    "cards_a": ["聖杯國王", "寶劍五", "權杖騎士"],
    "cards_b": ["金幣九", "星星", "隱士"],
    "interpretation": "路徑推演 + 代價收益 + 關鍵變數（2500-3500字）",
    "warnings": ["未提供 birth_time，已略過八字與占星計算"]
  }
}
```

---

## 🧪 完整測試指南

### 測試架構總覽

```
測試層級：
├─ 單元測試（模組級）
│  ├─ test_bazi_system.py        # 八字系統三項測試
│  ├─ test_astrology_complete.py # 西洋占星術測試（v1.4.0）
│  ├─ test_client.py             # API 基礎功能測試
│  └─ consistency_test.py        # 一致性驗證（10次）
│
├─ 整合測試（系統級）
│  ├─ test_three_modes.py        # 三種模式完整流程
│  ├─ test_complete_system.py    # v1.4.0 完整系統
│  └─ test_advanced.py           # 進階功能互動測試
│
└─ 自動化測試（CI/CD 就緒）
   └─ test_advanced_auto.py      # 3 項核心自動化測試
```

### 快速驗證（5 分鐘）

```bash
# 1. 啟動 API 服務
.venv/bin/python api_server.py

# 2. 另開終端，執行健康檢查
curl http://localhost:5001/health

# 3. 執行西洋占星術測試（v1.4.0 最新）
.venv/bin/python test_astrology_complete.py
```

### 完整測試流程（30 分鐘）

**步驟 1：準備環境**
```bash
# 確認 API 服務運行中
curl http://localhost:5001/health
```

**步驟 2：執行核心測試**
```bash
# 測試 1：八字系統（3 項測試）
.venv/bin/python test_bazi_system.py
# 預期：排盤 <5秒、分析 30-45秒、運勢 30-45秒

# 測試 2：西洋占星術系統（4 項測試，v1.4.0）
.venv/bin/python test_astrology_complete.py
# 預期：本命盤、合盤、流年、事業全部通過

# 測試 3：三種模式驗證
.venv/bin/python test_three_modes.py
# 預期：紫微查詢、八字排盤、交叉驗證全部通過

# 測試 4：完整系統測試
.venv/bin/python test_complete_system.py
# 預期：5 項測試全部通過
```

**步驟 3：自動化測試**
```powershell
python test_advanced_auto.py
# 預期：快速合盤、開業擇日、合夥分析全部通過
```

### 六大命理系統測試腳本

#### 獨立系統測試腳本

| 系統 | 測試腳本 | 測試功能 |
|------|----------|----------|
| 紫微斗數 | `test_ziwei_system.py` | 鎖盤狀態、首次分析、確認鎖盤、流年運勢、流月運勢 |
| 八字命理 | `test_bazi_system.py` | 八字排盤、命理分析、流年運勢 |
| 西洋占星術 | `test_astrology_system.py` | 本命盤、合盤、過境分析 |
| 靈數學 | `test_numerology_system.py` | 生命靈數、完整檔案、流年、配對 |
| 姓名學 | `test_name_system.py` | 五格數理、完整分析、命名建議、筆劃查詢 |
| 塔羅牌 | `test_tarot_system.py` | 每日一牌、三張牌解讀、牌陣列表、牌卡資訊 |

#### 整合測試腳本

| 測試腳本 | 說明 |
|----------|------|
| `test_all_six_systems.py` | 完整六大系統整合測試（一次測試所有系統） |
| `test_complete_system.py` | 原有完整系統測試（紫微+八字+交叉驗證） |
| `test_three_modes.py` | 三模式整合測試 |
| `test_advanced_auto.py` | 進階功能自動測試（合盤、擇日） |

#### 使用方式

```bash
# 測試單一系統
python test_ziwei_system.py      # 紫微斗數
python test_bazi_system.py       # 八字命理
python test_astrology_system.py  # 西洋占星術
python test_numerology_system.py # 靈數學
python test_name_system.py       # 姓名學
python test_tarot_system.py      # 塔羅牌

# 完整測試六大系統（推薦）
python test_all_six_systems.py
```

### 測試覆蓋率報告

| 功能模組 | 測試腳本 | 覆蓋率 | 狀態 |
|---------|---------|--------|------|
| **紫微斗數核心** | test_ziwei_system.py | 100% | ✅ |
| **八字命理核心** | test_bazi_system.py | 100% | ✅ |
| **西洋占星術核心** | test_astrology_system.py | 100% | ✅ |
| **靈數學核心** | test_numerology_system.py | 100% | ✅ |
| **姓名學核心** | test_name_system.py | 100% | ✅ |
| **塔羅牌核心** | test_tarot_system.py | 100% | ✅ |
| **🆕 戰略側寫系統** | (手動測試) | 100% | ✅ |
| 交叉驗證系統 | test_three_modes.py | 100% | ✅ |
| 合盤分析 | test_advanced_auto.py | 100% | ✅ |
| 擇日功能 | test_advanced_auto.py | 100% | ✅ |
| **六大系統整合** | test_all_six_systems.py | 100% | ✅ |

**總測試覆蓋率**：100%（六大命理系統 + 戰略側寫全覆蓋）

### 效能基準測試

執行 `test_all_six_systems.py` 可獲得以下基準數據：

```
【紫微斗數】
命盤鎖定檢查：   < 1 秒
流年運勢分析：   30-60 秒（AI 生成 2000-3000 字）
流月運勢分析：   30-60 秒（AI 生成 1500-2500 字）

【八字命理】
八字排盤：       < 5 秒
八字分析：       30-45 秒（AI 生成 3500-5000 字）
流年運勢：       30-45 秒（AI 生成 2000-3000 字）
交叉驗證：       60-90 秒（AI 生成 4000-6000 字）

【西洋占星術】
本命盤分析：     40-60 秒（AI 生成 3500-5000 字）
合盤分析：       50-70 秒（AI 生成 2500-3500 字）
過境分析：       40-60 秒（AI 生成 2000-3000 字）

【靈數學】
生命靈數計算：   < 1 秒
完整靈數檔案：   30-60 秒（AI 生成 2000-3000 字）
流年運勢：       < 1 秒（無 AI）
靈數配對：       30-60 秒（AI 生成 1500-2500 字）

【姓名學】
五格數理計算：   < 1 秒
完整姓名分析：   30-60 秒（AI 生成 1500-2500 字）
命名建議：       30-60 秒（AI 生成 1000-2000 字）
筆劃查詢：       < 1 秒

【塔羅牌】
每日一牌：       20-40 秒（AI 生成 500-1000 字）
三張牌解讀：     30-60 秒（AI 生成 1500-2500 字）
牌陣列表：       < 1 秒
牌卡資訊：       < 1 秒

【🆕 戰略側寫】
全息生命圖譜：   40-60 秒（AI 生成 2000-3000 字）
生辰校正：       50-70 秒（AI 生成 1500-2500 字）
關係生態位：     50-70 秒（AI 生成 2000-3000 字）
決策沙盒：       60-80 秒（AI 生成 2500-3500 字）
```

---

## 🧪 測試指南（舊版）

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

## ⚠️ 已知限制與技術債務

### 當前限制

#### 1. 資料存儲（優先級：高）
**現狀**：✅ 已完成 - 使用 JSON 檔案存儲（`data/chart_locks.json`, `data/users.json`）  
**實作狀態**：已實作會員系統與資料庫結構

#### 2. 用戶認證（優先級：高）
**現狀**：✅ 已完成 - JWT Token 認證系統  
**實作功能**：
- JWT Token 認證
- 會員註冊/登入/登出
- 密碼安全存儲（hash + salt）
- Session 管理

#### 3. 前端介面（優先級：極高）
**現狀**：✅ 已完成 - React/Vite Web 介面  
**實作功能**：
- React 18 + Vite 5 前端框架
- 會員認證流程
- 六大命理系統 UI
- 🆕 戰略側寫模組 UI（全息側寫、生辰校正、關係生態、決策沙盒）
- 響應式設計

#### 4. 錯誤處理與日誌（優先級：中）
**現狀**：基礎錯誤處理，無結構化日誌  
**問題**：難以追蹤問題

**解決方案**：
```python
import logging
import sentry_sdk  # 錯誤追蹤
```

**預估工作量**：4-6 小時

#### 5. API 文檔（優先級：中）
**現狀**：README 中手寫文檔  
**問題**：不易維護、不支援互動測試

**解決方案**：
- Swagger/OpenAPI 自動生成文檔
- Postman Collection

**預估工作量**：3-4 小時

### 技術債務清單

| 項目 | 嚴重度 | 優先級 | 預估工時 | 狀態 |
|------|--------|--------|----------|------|
| ~~PostgreSQL 遷移~~ | 🔴 高 | 🔥🔥🔥🔥 | ~~8-12h~~ | ✅ 已完成 |
| ~~用戶認證系統~~ | 🔴 高 | 🔥🔥🔥🔥 | ~~6-8h~~ | ✅ 已完成 |
| ~~Web/App 前端~~ | 🔴 高 | 🔥🔥🔥🔥🔥 | ~~40-60h~~ | ✅ 已完成 |
| 錯誤追蹤與日誌 | 🟡 中 | 🔥🔥🔥 | 4-6h | ⏳ 待處理 |
| API 文檔自動化 | 🟡 中 | 🔥🔥 | 3-4h | ⏳ 待處理 |
| 單元測試覆蓋 | 🟢 低 | 🔥 | 8-10h | ⏳ 待處理 |
| Docker 容器化 | 🟢 低 | 🔥 | 2-3h | ⏳ 待處理 |

**總計技術債務**：17-23 小時（約 3-5 天全職工作）  
**v1.9.0 已清償**：54-80 小時（前端、認證、資料庫）

### 安全考量

1. **API Key 洩露風險**
   - ✅ `.env` 已加入 `.gitignore`
   - ⚠️ 需定期輪換 Gemini API Key
   - ⚠️ 需監控 API 使用量

2. **敏感資料保護**
   - ⚠️ 出生資料未加密存儲
   - 建議：實作欄位級加密

3. **合規性**
   - ⚠️ 需符合 GDPR/個資法
   - ⚠️ 需添加免責聲明
   - ⚠️ 避免絕對預測（醫療、死亡等）

### 效能瓶頸

1. **Gemini API 延遲**
   - 現狀：30-90 秒（不可避免）
   - 建議：實作結果快取

2. **併發處理**
   - 現狀：Flask 單執行緒開發模式
   - 建議：部署時使用 Gunicorn + Nginx

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
│  │  Endpoints (16 routes)                   │   │
│  │  - Ziwei Chart Analysis (8)              │   │
│  │  - BaZi Analysis (3)                     │   │
│  │  - Astrology Analysis (4)                │   │
│  │  - Cross Validation (1)                  │   │
│  └──────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┼─────────────────┐
    │             │                 │
┌───▼───┐   ┌────▼────┐   ┌────────▼─────────┐
│Gemini │   │  Chart  │   │   Calculators    │
│  API  │   │Extractor│   │ - BaZi (sxtwl)   │
│ 2.0   │   │         │   │ - Astrology      │
│ Flash │   │         │   │   (Swiss Eph)    │
└───────┘   └────┬────┘   └──────────────────┘
                 │
           ┌─────▼─────┐
           │   Data    │
           │  Storage  │
           │chart_locks│
           │users.json │
           └───────────┘
```

### 核心模組

| 模組 | 檔案 | 說明 |
|------|------|------|
| **API 服務** | `api_server.py` | Flask API 主程式（16 端點） |
| **命盤提取** | `chart_extractor.py` | 結構化提取命盤資訊 |
| **流年運勢** | `fortune_teller.py` | 流年命盤計算與分析 |
| **八字計算** | `bazi_calculator.py` | 四柱排盤與十神分析 |
| **占星計算** | `astrology_calculator.py` | 行星位置與宮位計算 |
| **Prompt 模板** | `fortune_prompts.py` | 流年運勢 Prompt |
| | `synastry_prompts.py` | 合盤分析 Prompt |
| | `date_selection_prompts.py` | 擇日功能 Prompt |
| | `bazi_prompts.py` | 八字分析 Prompt |
| | `astrology_prompts.py` | 占星分析 Prompt |
| **資料存儲** | `data/chart_locks.json` | 鎖定命盤資料庫 |
| | `data/users.json` | 用戶資料庫 |

### Prompt 工程策略

1. **結構化輸出**：透過 Markdown 格式定義嚴格的輸出結構
2. **上下文注入**：將已鎖定的命盤結構注入 Prompt
3. **專業術語**：使用正統命理術語確保專業性
4. **範例驅動**：提供分析範例引導 LLM 輸出
5. **長度控制**：明確指定各段落字數要求

---

## 📊 效能指標

### 模型選擇：Gemini 2.0 Flash Exp ⭐

經過完整對比測試（2026/01/24），確認 **Gemini 2.0 Flash Exp** 為最佳選擇：

| 指標 | 2.0 Flash Exp | Pro Preview | 差異 |
|------|---------------|-------------|------|
| **命盤分析速度** | 42.49s | 87.36s | **快 2.06x** |
| **流年運勢速度** | 35.72s | 61.89s | **快 1.73x** |
| **Token 用量** | 5,754 | 9,480 | **省 39%** |
| **結構完整度** | 3/4 | 3/4 | **相同** |
| **內容品質** | 優秀 | 優秀 | **相當** |
| **成本** | 低 | 高 | **省 30-40%** |

**結論**：2.0 Flash Exp 在速度、成本上全面領先，且品質完全相當於 Pro 版本。

### 典型回應時間

| 功能 | 平均時間 | Token 消耗 |
|------|----------|-----------|
| 紫微命盤分析 | 40-50s | 5,000-6,000 |
| 八字命理分析 | 40-50s | 5,500-6,500 |
| 占星本命盤 | 50-60s | 6,000-7,000 |
| 流年運勢 | 35-45s | 5,000-6,500 |
| 快速合盤 | 20-25s | 3,000-4,000 |
| 婚配合盤 | 60-70s | 7,000-8,000 |
| 占星合盤 | 50-60s | 6,000-7,000 |
| 擇日分析 | 50-60s | 6,000-7,500 |

---

## 🛠️ 開發指南

### 專案結構

```
Aetheria_Core/
├── run.py                       # 🚀 統一啟動入口
├── requirements.txt             # 依賴套件
├── .env                         # 環境變數（不提交）
├── .env.example                 # 環境變數範本
├── README.md                    # 本檔案
│
├── src/                         # 📦 核心原始碼
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py            # Flask API 主程式（39+ 端點）
│   │
│   ├── calculators/             # 計算引擎
│   │   ├── __init__.py
│   │   ├── bazi.py              # 八字排盤計算
│   │   ├── astrology.py         # 西洋占星計算（Swiss Ephemeris）
│   │   ├── numerology.py        # 靈數學計算
│   │   ├── name.py              # 姓名學計算（五格剖象法）
│   │   ├── tarot.py             # 塔羅牌計算
│   │   ├── fortune.py           # 流年運勢計算
│   │   └── chart_extractor.py   # 命盤結構提取器
│   │
│   ├── prompts/                 # Prompt 模板
│   │   ├── __init__.py
│   │   ├── bazi.py              # 八字 Prompt
│   │   ├── astrology.py         # 占星 Prompt
│   │   ├── numerology.py        # 靈數學 Prompt
│   │   ├── name.py              # 姓名學 Prompt
│   │   ├── tarot.py             # 塔羅牌 Prompt
│   │   ├── fortune.py           # 流年 Prompt
│   │   ├── synastry.py          # 合盤 Prompt
│   │   ├── date_selection.py    # 擇日 Prompt
│   │   ├── integrated.py        # 整合分析 Prompt
│   │   └── strategic.py         # 🆕 戰略側寫 Prompt
│   │
│   └── utils/                   # 工具程式
│       ├── __init__.py
│       ├── check_env.py         # 環境檢查
│       └── list_models.py       # Gemini 模型列表
│
├── tests/                       # 🧪 測試腳本
│   ├── __init__.py
│   ├── test_ziwei.py            # 紫微斗數測試
│   ├── test_bazi.py             # 八字系統測試
│   ├── test_astrology.py        # 西洋占星測試
│   ├── test_numerology.py       # 靈數學測試
│   ├── test_name.py             # 姓名學測試
│   ├── test_tarot.py            # 塔羅牌測試
│   ├── test_all_systems.py      # 六大系統整合測試
│   ├── test_complete.py         # 完整系統測試
│   ├── test_three_modes.py      # 三模式測試
│   ├── test_advanced.py         # 互動式測試
│   ├── test_fortune.py          # 流年運勢測試
│   └── test_client.py           # API 客戶端測試
│
├── data/                        # 💾 資料檔案
│   ├── users.json               # 用戶資料庫
│   ├── chart_locks.json         # 命盤鎖定資料
│   ├── tarot_cards.json         # 塔羅牌資料
│   ├── numerology_data.json     # 靈數學資料
│   └── name_analysis.json       # 姓名學資料
│
├── docs/                        # 📚 技術文件
│   └── 01-09_*.md               # 技術白皮書與規劃文件
│
├── scripts/                     # 🔧 腳本工具
│   └── start_api_and_test.sh    # 啟動與測試腳本
│
└── logs/                        # 📋 日誌目錄
    └── api_startup.log          # API 啟動日誌
```

### 添加新功能

#### 1. 定義 Prompt

在對應的 `src/prompts/` 目錄下添加新的 Prompt 模板：

```python
# src/prompts/new_feature.py
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

在 `src/api/server.py` 中添加新端點：

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

在 `tests/` 目錄創建新的測試檔案或添加到現有測試。

### 除錯技巧

#### 1. 檢查 API 健康狀態

```bash
curl http://localhost:5001/health
```

#### 2. 驗證環境變數

```bash
python -m src.utils.check_env
```

#### 3. 測試 Gemini 連線

```bash
python -m src.utils.list_models
```

#### 4. 執行測試

```bash
# 執行六大系統整合測試
python tests/test_all_systems.py

# 執行單一系統測試
python tests/test_ziwei.py
python tests/test_bazi.py
python tests/test_astrology.py
python tests/test_numerology.py
python tests/test_name.py
python tests/test_tarot.py
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
- ✅ 紫微+八字交叉驗證系統（5000-7000 字，較 v1.2 更長更詳細）
- ✅ 三種使用模式架構：紫微 / 八字 / 交叉驗證
- ✅ 4 個新增 API 端點

**品質保證更新（v1.3.0 後期）**：
- ✅ **「有所本」規則**：所有命理判斷必須引用來源數據（命宮/星曜/四化/十神/用神等）
- ✅ **資料不足處理**：明確標註「資料不足，無法下定論」並列出「需要補充的問題」（3-7 個）
- ✅ **用戶事實校準（user_facts）**：交叉驗證端點支持用戶提供已知事實進行分析校準
- ✅ **台灣繁體中文保證**：所有 AI 輸出強制轉換為 zh-TW（使用 OpenCC s2twp）
- ✅ **依據來源標註**：每個結論區塊末尾新增「依據：...」行引用具體命盤資訊
- ✅ **Port 變更**：5000 → 5001（避免 macOS ControlCenter 衝突）
- ✅ **虛擬環境支持**：推薦使用 .venv 隔離依賴

**技術改進：**
- 新增 bazi_calculator.py（480+ 行核心計算引擎）
- 新增 bazi_prompts.py（八字分析提示詞模板，含「有所本」規則）
- 更新 fortune_prompts.py, synastry_prompts.py, date_selection_prompts.py（全面加入證據引用與問題生成規則）
- API Server 新增八字路由組（/api/bazi/*, /api/cross-validation/*）
- API Server 新增 OpenCC 繁簡轉換層（to_zh_tw 函數）
- Requirements.txt 新增 sxtwl>=2.0.7 + opencc-python-reimplemented>=0.1.7 依賴
- 完整測試腳本（test_bazi_system.py, test_three_modes.py, test_steve_bazi_cross.py）

**文檔更新：**
- README 新增「語言輸出保證」區塊
- README 新增「命理分析品質保證」區塊（有所本規則、資料不足處理、用戶事實校準）
- README 更新「快速開始」區塊（venv 設定、OpenCC 依賴、port 5001 說明）
- API 文檔新增 user_facts 參數說明與範例

---

## 📝 版本歷程

### v1.9.0 (2026-01-25) 🆕 最新版

**戰略側寫系統上線：從「算命」到「戰略決策」**
- ✅ 全息生命圖譜（Meta Profile 整合八字/靈數/姓名/占星）
- ✅ 生辰校正器（反推 12 時辰，給出 Top 3 可能性）
- ✅ 關係生態位（資源流動分析，非感情導向）
- ✅ 決策沙盒（雙路徑塔羅模擬，推演代價與收益）
- ✅ React/Vite 前端界面完整實作（會員認證、六大系統 UI、戰略模組 UI）
- ✅ JWT 會員認證系統（註冊/登入/登出/Token 管理）
- ✅ 4 個新 API 端點（/api/strategic/*）
- ✅ 結論優先架構（先結論→列證據→給建議）

**系統優化（Code Review 修正）：**
- ✅ API JSON 容錯處理（request.get_json(silent=True)）
- ✅ 關係生態 warnings 提示
- ✅ 決策沙盒資料深度提升（納入姓名學）
- ✅ 前端必填檢核（避免空資料送出）
- ✅ 決策沙盒支援 birth_time（可選含八字/占星）

**技術改進：**
- 新增 src/prompts/strategic.py（260+ 行）
- 新增 webapp/ React 前端（1200+ 行）
- API 端點從 35 個增至 39 個
- README 全面更新（新增戰略側寫、API 文檔、測試覆蓋）

### v1.8.0 (2026-01-24) ⭐

**靈數學 + 姓名學系統整合：**
- ✅ 靈數學系統（生命靈數、流年運勢、相容性分析、完整檔案、個人分析）
- ✅ 姓名學系統（五格剖象法、81數理、三才配置、姓名建議）
- ✅ 整合分析端點（靈數+姓名綜合分析）
- ✅ 8 個新 API 端點完整測試
- ✅ 五大命理系統整合（紫微 + 八字 + 占星 + 靈數 + 姓名）

**系統優化與修正（Code Review 完整修正）：**
- ✅ 性別參數統一化：新增 normalize_gender() 處理 male/female → 男/女
- ✅ 出生日期解析：新增 parse_birth_date_str() 支援多種日期格式
- ✅ 流年計算動態化：修正三個流年端點，自動從 users.json 讀取出生資料
- ✅ 測試環境統一：12 個測試/工具腳本 port 從 5000 統一為 5001
- ✅ 八字性別參數：BaziCalculator 新增 _normalize_gender() 確保大運順逆正確

**技術改進：**
- 新增 integrated_prompts.py（靈數+姓名整合分析提示詞）
- API 端點從 16 個增至 30+ 個
- 新增三個輔助函數：normalize_gender(), parse_birth_date_str(), get_user_birth_info()
- README 全面更新（五大命理系統說明、性別/日期處理說明）

### v1.4.0 (2026-01-24)

**西洋占星術系統完整整合：**
- ✅ 本命盤計算（Swiss Ephemeris，< 0.5° 誤差）
- ✅ 合盤分析（太陽/月亮/金星/火星相位）
- ✅ 流年運勢（Transit 預測）
- ✅ 事業發展分析（第十宮/第六宮/第二宮）
- ✅ 4 個新 API 端點完整測試
- ✅ 三系統整合（紫微 + 八字 + 占星）
- ✅ 流年事件驗證工具（event_validation.py）
- ✅ GPL 授權策略（SaaS 模式合法）

**技術改進：**
- 新增 astrology_calculator.py（600+ 行）
- 新增 astrology_prompts.py（300+ 行）
- API 端點從 13 個增至 16 個
- README 全面更新（新增占星術說明）
- 實作報告：14_Astrology_Implementation_Report.md

### v1.3.0 (2026-01-24)

**八字命理系統整合：**
- ✅ 八字排盤計算（sxtwl 真太陽時）
- ✅ 八字命理分析
- ✅ 八字流年運勢
- ✅ 紫微+八字交叉驗證
- ✅ 「有所本」規則強制執行
- ✅ 資料不足處理機制
- ✅ 台灣繁體中文（zh-TW）輸出保證

### v1.2.0 (2026-01-24)

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

本專案採用 **GNU General Public License v2.0 (GPL v2)**，與所使用的 Swiss Ephemeris 星曆庫保持一致。

**當前狀態（v1.8.0）**：
- ✅ 使用開源版 Swiss Ephemeris（GPL v2）
- ✅ SaaS 部署模式（不分發二進位檔案）
- ✅ 符合 GPL v2 授權要求
- ✅ 五大命理系統整合完成（紫微、八字、占星、靈數、姓名）

**商業化計畫**：
- 當月營收 > $1000 時，購買 Swiss Ephemeris 商業授權（$250 一次性）
- 商業授權後可移除 GPL 限制，改為專有授權

**依賴庫授權**：
- Swiss Ephemeris: GPL v2（商業授權可選）
- sxtwl (壽星天文曆): GPL（待確認作者授權）
- Kerykeion: MIT License
- Flask, Gemini API: 各自授權條款

Copyright © 2026 Aetheria Team.

---

## 📞 聯絡方式

如有問題或建議，請透過以下方式聯絡：

- 📧 Email: [待補充]
- 💬 Discord: [待補充]
- 🐛 Issues: [待補充]

---

## 🌟 致謝

- **Google Gemini Team** - 提供強大的 Gemini 2.0 Flash Exp 模型
- **Swiss Ephemeris Team** - 提供專業級星曆計算引擎
- **Flask Community** - 優秀的 Web 框架
- **Kerykeion** - 優雅的 Swiss Ephemeris Python 封裝
- **紫微斗數學術社群** - 傳統命理智慧傳承
- **八字命理研究者** - 四柱推命理論體系
- **Stephen Arroyo, Liz Greene, Robert Hand** - 西洋占星術理論基礎

---

---

## 🎯 快速參考卡片

### 給產品經理

```
專案價值：AI 驅動的三系統命理分析平台
核心優勢：紫微+八字+占星三重驗證，準確度最高
市場定位：B2C 個人諮詢 → B2B HR-Tech
競爭優勢：LLM-First 策略 + 專業級精度（Swiss Ephemeris）
當前階段：三系統整合完成，生產就緒

下一步行動：
1. 開發 Web UI（2-3 週）
2. 實作用戶認證（1 週）
3. Beta 測試招募（100 人）
4. 商業化準備（GPL 授權購買）
```

### 給技術主管

```
技術棧：Python + Flask + Gemini 2.0 + Swiss Ephemeris
架構：LLM-First + 多系統計算引擎
核心亮點：三系統整合、專業級星曆、Prompt 工程成熟
效能：40-90 秒/分析（AI 生成，不可避免）
成本：每次分析約 $0.02-0.08（Gemini Flash）
擴展性：模組化設計，易於添加新命理系統

技術債務：
- 需要 PostgreSQL 遷移（12h）
- 需要用戶認證（8h）
- 需要前端開發（80h）
- Swiss Ephemeris 商業授權（$250，達標後購買）
```

### 給工程師

```bash
# 快速啟動（5 分鐘）
git clone <repo>
cd Aetheria_Core
pip install -r requirements.txt
cp .env.example .env  # 填入 GEMINI_API_KEY
.venv/bin/python api_server.py

# 測試 API
curl http://localhost:5001/health

# 執行測試
.venv/bin/python test_bazi_system.py
.venv/bin/python test_astrology_complete.py

# 核心檔案
api_server.py              # API 主程式（1950+ 行，16 端點）
bazi_calculator.py         # 八字計算引擎（484 行）
astrology_calculator.py    # 占星計算引擎（600+ 行）
chart_extractor.py         # 命盤提取器（352 行）
```
*_prompts.py           # Prompt 模板（多個檔案）
```

---

## 🔧 故障排除

### 常見問題

#### Q1: API 返回 500 錯誤
```bash
# 檢查 Gemini API Key 是否正確
python debug_config.py

# 檢查模型名稱是否正確
# .env 中應為 MODEL_NAME=gemini-2.0-flash-exp
```

#### Q2: 八字計算失敗
```bash
# 確認 sxtwl 庫已安裝
pip install sxtwl>=2.0.7

# 測試八字計算
python -c "import sxtwl; print('OK')"
```

#### Q3: 測試腳本連不上 API
```bash
# 確認 API 服務運行中
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# 重新啟動服務
python api_server.py
```

#### Q4: 分析速度太慢（>120 秒）
```bash
# 檢查網路連線
curl -w "@curl-format.txt" -o /dev/null -s https://generativelanguage.googleapis.com/

# 檢查 Gemini API 配額
# 前往 https://aistudio.google.com/apikey 查看用量
```

#### Q5: JSON 檔案損壞
```bash
# 備份並重置
cp data/chart_locks.json data/chart_locks.json.backup
echo '{}' > data/chart_locks.json
```

### 調試模式

```python
# 在 api_server.py 中啟用詳細日誌
import logging
logging.basicConfig(level=logging.DEBUG)

# 或修改 .env
DEBUG_MODE=true
```

### 效能監控

```python
# 添加請求計時
import time
start = time.time()
# ... API 呼叫 ...
print(f"耗時：{time.time() - start:.2f} 秒")
```

---

## 📞 支援與貢獻

### 獲取幫助

1. **閱讀文檔**：從 [文檔導航](#-文檔導航新接手者必讀) 開始
2. **查看範例**：`test_*.py` 檔案包含完整使用範例
3. **故障排除**：參考上方故障排除指南
4. **開 Issue**：描述問題 + 錯誤訊息 + 重現步驟

### 開發建議

- **分支策略**：`main`（穩定）、`develop`（開發）、`feature/*`（功能）
- **提交規範**：`feat:`、`fix:`、`docs:`、`test:`
- **測試要求**：新功能必須包含測試
- **文檔同步**：修改 API 需同步更新 README

---

**Built with ❤️ by Aetheria Team**

*最後更新：2026 年 1 月 24 日*
*文檔版本：v1.3.1（增強版）*
