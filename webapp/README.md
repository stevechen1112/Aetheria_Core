# Aetheria Core - Web Application (UI v2.0)

> **現代化命理分析平台前端** | React 19 + Vite 7 | 全新 Dashboard 設計

[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7.3-purple.svg)](https://vite.dev/)
[![UI Version](https://img.shields.io/badge/UI-v2.0-brightgreen.svg)]()

## 📦 快速開始

### 安裝依賴

```bash
npm install
```

### 啟動開發伺服器

```bash
npm run dev
```

開啟 http://localhost:5173/ 即可看到全新界面！

### 構建生產版本

```bash
npm run build
```

---

## 🎨 UI v2.0 設計系統

**發布日期**：2026-01-25  
**設計哲學**：從「算命」到「戰略」的視覺升級

### 核心特性

#### 1. Dashboard + Sidebar 架構

```
┌──────────┬────────────────────┐
│          │  Content Header    │
│ Sidebar  ├────────────────────┤
│          │                    │
│ 🏠 首頁  │  Dynamic Content   │
│ 🔮 命盤  │  (視圖切換)         │
│ 📚 系統  │                    │
│ 🎯 戰略  │                    │
│ ⚙️ 設定  │                    │
│          │                    │
└──────────┴────────────────────┘
```

- **固定側邊欄導航**：清晰的功能分類
- **主內容區**：動態切換不同視圖
- **Landing Page**：未登入用戶的引導頁面

#### 2. 6 步驟 Wizard 命盤建立

```
[1] 基本資料 → [2] 出生資訊 → [3] 確認 → 
[4] 分析中 → [5] 預覽 → [6] 完成
```

- **漸進式揭露**：一次只問一件事，降低認知負擔
- **進度可視化**：圓圈進度條，清楚知道目前進度
- **即時驗證**：每步驟檢查輸入，避免錯誤累積

#### 3. 戰略側寫獨特視覺語言

- **主題色（六大系統）**：綠色系 `#8b9a87`（沉穩、自然、命理感）
- **戰略色**：藍色系 `#7a8fa6`（理性、專業、決策感）
- **視覺差異化**：戰略功能使用藍色漸層，一眼識別

#### 4. 完整設計 Token 系統

```css
/* 色彩系統 */
--color-primary: #8b9a87       /* 主綠色 */
--color-strategic: #7a8fa6     /* 戰略藍 */
--color-accent: #c5b5a0        /* 強調色 */

/* 間距系統（8px Grid）*/
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px
--spacing-2xl: 48px
--spacing-3xl: 64px

/* 圓角系統 */
--radius-sm: 8px
--radius-md: 12px
--radius-lg: 16px
--radius-xl: 24px

/* 陰影系統 */
--shadow-sm: 0 2px 8px rgba(58, 53, 48, 0.04)
--shadow-md: 0 4px 16px rgba(58, 53, 48, 0.08)
--shadow-lg: 0 12px 32px rgba(58, 53, 48, 0.12)
--shadow-xl: 0 20px 48px rgba(58, 53, 48, 0.16)
```

---

## 🏗️ 架構說明

### 文件結構

```
webapp/
├── src/
│   ├── App.jsx              # 主應用組件（當前使用）
│   ├── App.css              # 主應用樣式（當前使用）
│   ├── App.v2.jsx           # UI v2.0 原始檔案（備份）
│   ├── App.v2.css           # UI v2.0 樣式（備份）
│   ├── main.jsx             # 應用入口
│   ├── index.css            # 全局樣式
│   └── assets/              # 靜態資源
├── public/                  # 公開資源
├── index.html               # HTML 模板
├── vite.config.js           # Vite 配置
├── package.json             # 依賴管理
├── switch-to-v2.ps1         # 切換到 v2.0 腳本
├── switch-to-old.ps1        # 還原舊版腳本
└── UI_V2_README.md          # UI v2.0 詳細說明
```

### 視圖組件

| 組件 | 說明 | 觸發條件 |
|------|------|----------|
| **Landing Page** | 未登入首頁 | 無 token |
| **Dashboard Home** | 已登入首頁 | currentView === 'home' |
| **Chart View** | 命盤建立 Wizard | currentView === 'chart' |
| **Systems View** | 六大系統選擇 | currentView === 'systems' |
| **Strategic View** | 戰略側寫入口 | currentView === 'strategic' |
| **Settings View** | 設定頁面 | currentView === 'settings' |

### 共用組件

- **Sidebar Navigation**：側邊欄導航
- **Auth Modal**：登入/註冊彈窗
- **Toast System**：通知提示系統
- **Progress Wizard**：進度條組件

---

## 🔧 技術棧

- **框架**：React 19
- **構建工具**：Vite 7.3
- **狀態管理**：useState（未來可升級為 Context API 或 Zustand）
- **樣式**：純 CSS（完整設計系統，無額外依賴）
- **HTTP 請求**：Fetch API
- **路由**：視圖狀態切換（currentView）

---

## 📚 相關文檔

- **完整設計報告**：[../docs/18_UI_UX_Redesign_Report_v2.0.md](../docs/18_UI_UX_Redesign_Report_v2.0.md)
- **UI v2.0 詳細說明**：[UI_V2_README.md](UI_V2_README.md)
- **技術白皮書**：[../docs/01_Technical_Whitepaper.md](../docs/01_Technical_Whitepaper.md)
- **API 文檔**：[../docs/STRATEGIC_API.md](../docs/STRATEGIC_API.md)

---

## 🎓 開發指南

### 新增一個視圖

1. 在 `App.jsx` 中創建 render 函數：

```jsx
const renderNewView = () => (
  <>
    <div className="content-header">
      <h1 className="content-title">新視圖</h1>
      <p className="content-subtitle">描述</p>
    </div>
    <div className="content-body">
      {/* 內容 */}
    </div>
  </>
)
```

2. 在 Sidebar 新增導航項：

```jsx
<div 
  className={`nav-item ${currentView === 'newview' ? 'active' : ''}`}
  onClick={() => setCurrentView('newview')}
>
  <div className="nav-icon">🎨</div>
  <div>新視圖</div>
</div>
```

3. 在主內容區新增路由：

```jsx
{currentView === 'newview' && renderNewView()}
```

### 自定義主題色

修改 `App.css` 中的 CSS 變量：

```css
:root {
  --color-primary: #你的顏色;
  --color-strategic: #你的戰略色;
}
```

---

## 🚀 性能優化

### 待實作優化項目

- [ ] **代碼分割**：React.lazy + Suspense
- [ ] **圖片優化**：WebP 格式 + 懶加載
- [ ] **快取策略**：Service Worker + LocalStorage
- [ ] **Bundle 優化**：移除未使用的代碼

---

## 📞 問題排查

### Rollup 原生模組錯誤

如果遇到 `Cannot find module '@rollup/rollup-win32-x64-msvc'` 錯誤：

```bash
npm install --cpu=x64 --os=win32 @rollup/rollup-win32-x64-msvc
```

### 切換 UI 版本

**切換到 v2.0**：
```powershell
.\switch-to-v2.ps1
```

**還原舊版**：
```powershell
.\switch-to-old.ps1
```

---

**Aetheria Core UI v2.0 - 從算命到戰略的視覺升級**

設計師：GitHub Copilot (Claude Sonnet 4.5)  
創建日期：2026-01-25
