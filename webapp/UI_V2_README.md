# Aetheria UI v2.0 - 完全重新設計

## 🎨 設計系統升級

已為 Aetheria Core 創建全新的現代化 UI/UX 設計！

### 主要改進

#### 1. **設計系統完整化**
- ✨ 完整的設計 token 系統（顏色、間距、圓角、陰影）
- 🎨 獨特的戰略側寫視覺語言（藍色調）
- 📏 8px 間距系統，一致的視覺節奏
- 🌈 語意化色彩系統（成功、警告、錯誤、資訊）

#### 2. **架構優化**
- **未登入狀態**：Landing Page（Hero + Features）
- **已登入狀態**：Dashboard Layout（Sidebar + Main Content）
- **漸進式揭露**：6步驟 Wizard 引導命盤建立
- **卡片流設計**：所有內容以卡片形式組織

#### 3. **用戶體驗提升**
- 🚀 側邊欄導航（固定位置，一目了然）
- 📊 進度指示器（Wizard 步驟可視化）
- 💬 Toast 通知系統（優雅的反饋）
- 🎭 Modal 對話框（登入/註冊）
- ⚡ 快速操作（Dashboard 快捷卡片）

#### 4. **視覺層次清晰**
- 主 CTA 按鈕使用漸層背景
- 戰略功能使用獨特配色（藍色系）
- 卡片懸停效果（提升互動感）
- 統一的圓角和陰影系統

### 文件說明

- `App.v2.jsx` - 全新的 React 組件（完全重寫）
- `App.v2.css` - 全新的設計系統 CSS（1000+ 行）
- `App.jsx` - 原始組件（已備份）
- `App.css` - 原始樣式（已備份）

### 啟用新設計

#### 方案 A：完全替換（推薦）

```bash
# 備份舊版本
cd webapp/src
mv App.jsx App.old.jsx
mv App.css App.old.css

# 啟用新版本
mv App.v2.jsx App.jsx
mv App.v2.css App.css

# 重啟開發伺服器
cd ../..
npm run dev
```

#### 方案 B：共存測試

修改 `main.jsx`：

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './App.jsx'  // 舊版本
import App from './App.v2.jsx'  // 新版本
import './App.v2.css'            // 新樣式

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

### 功能清單

#### 已實作
- ✅ Landing Page（未登入首頁）
- ✅ 登入/註冊 Modal
- ✅ Dashboard Layout（側邊欄 + 主內容）
- ✅ 6步驟命盤建立 Wizard
- ✅ 首頁（Dashboard Home）
- ✅ 六大系統入口頁面
- ✅ 戰略側寫入口頁面（獨特設計）
- ✅ 設定頁面
- ✅ Toast 通知系統
- ✅ Loading 狀態處理
- ✅ 響應式設計基礎

#### 待整合（API 端點已存在）
- ⏳ 紫微斗數詳細頁面
- ⏳ 八字命理詳細頁面
- ⏳ 西洋占星詳細頁面
- ⏳ 靈數學詳細頁面
- ⏳ 姓名學詳細頁面
- ⏳ 塔羅牌詳細頁面
- ⏳ 全息圖譜功能頁面
- ⏳ 生辰校正功能頁面
- ⏳ 關係生態位功能頁面
- ⏳ 決策沙盒功能頁面

### 設計亮點

#### 1. 色彩系統
```css
主題色：#8b9a87（沉穩的綠色）
強調色：#c5b5a0（溫暖的米色）
戰略色：#7a8fa6（專業的藍色）- 獨特視覺語言
```

#### 2. 漸進式揭露
- 首次進入：只看到 Landing Page
- 登入後：看到 Dashboard 和命盤建立引導
- 命盤鎖定後：解鎖所有功能

#### 3. 視覺差異化
- 六大系統：使用主題綠色
- 戰略側寫：使用獨特藍色，強調「從算命到戰略」的升級

#### 4. 卡片設計
```
- 統一的 border-radius: 16-24px
- 柔和的陰影：多層次陰影系統
- 懸停效果：translateY(-4px) + 陰影增強
- 玻璃擬態：backdrop-filter: blur(20px)
```

### 技術特點

- **純 CSS**：無需額外 UI 框架
- **語意化 HTML**：清晰的結構
- **CSS 變量**：易於主題定制
- **動畫流暢**：cubic-bezier 緩動
- **可擴展性**：模組化設計，易於添加新功能

### 響應式設計

- **Desktop（> 1024px）**：側邊欄 + 主內容雙欄布局
- **Tablet（768-1024px）**：單欄布局，漢堡菜單（待實作）
- **Mobile（< 768px）**：簡化版 UI，垂直堆疊

### 下一步建議

1. **整合詳細功能頁面**
   - 為每個命理系統創建詳細分析頁面
   - 為戰略側寫創建互動式工具頁面

2. **增強互動**
   - 添加更多微動畫
   - 添加頁面切換過渡效果
   - 添加骨架屏（Skeleton Loading）

3. **完善響應式**
   - 實作移動端導航菜單
   - 優化移動端表單體驗
   - 測試各種螢幕尺寸

4. **數據可視化**
   - 命盤結構圖表化
   - 流年運勢曲線圖
   - 五行能量雷達圖

5. **性能優化**
   - 代碼分割（Code Splitting）
   - 懶加載（Lazy Loading）
   - 圖片優化

### 對比分析

| 項目 | 舊版本 | 新版本 v2.0 |
|------|--------|-------------|
| 架構 | 單頁面 Tab 切換 | 側邊欄導航 + 多視圖 |
| 設計系統 | 部分定義 | 完整 Design Token |
| 用戶引導 | 簡單步驟提示 | 6步驟 Wizard |
| 視覺層次 | 較扁平 | 明確的卡片層次 |
| 戰略側寫 | 與普通功能相同 | 獨特視覺語言 |
| 響應式 | 基礎支援 | 完整規劃 |
| 代碼組織 | 1266行單文件 | 模組化，易擴展 |

### 預覽截圖描述

#### Landing Page（未登入）
```
[Header with Logo]
Hero Section:
  ✨ v1.9.0 戰略側寫系統上線
  從算命到戰略
  AI 命理決策顧問
  [免費開始分析] [了解更多]

Feature Cards (3x2 Grid):
  🔮 紫微斗數
  ☯️ 八字命理
  ⭐ 西洋占星術
  🔢 靈數學
  📝 姓名學
  🎴 塔羅牌
  🎯 戰略側寫（跨兩欄，藍色強調）
```

#### Dashboard（已登入）
```
[Sidebar Navigation]
  A Aetheria
  ─────────
  🏠 首頁
  🔮 我的命盤 [!]
  
  命理系統
  📚 六大系統
  
  進階功能
  🎯 戰略側寫 [NEW]
  
  ⚙️ 設定
  ─────────
  [User Avatar] 用戶名

[Main Content]
  歡迎回來，用戶
  您的命盤已鎖定...
  
  [統計卡片]
  🔮 已鎖定    📊 6+1 系統    🎯 戰略版
  
  快速開始
  [📚 六大命理系統]
  [🎯 戰略側寫系統]
```

---

**Built with ❤️ for Aetheria Core v1.9.0**

**設計版本**：v2.0  
**創建日期**：2026-01-25  
**設計師**：GitHub Copilot (Claude Sonnet 4.5)
