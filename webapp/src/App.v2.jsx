import { useEffect, useState, useMemo } from 'react'
import './App.v2.css'

/* ==========================================
   Aetheria Core - v2.0 完全重新設計
   現代化命理分析平台
========================================== */

function App() {
  // ========== State Management ==========
  const [apiBase, setApiBase] = useState(
    localStorage.getItem('aetheria_api_base') || 'http://localhost:5001'
  )
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [profile, setProfile] = useState(null)
  const [currentView, setCurrentView] = useState('home') // home, chart, systems, strategic, settings
  const [currentSystem, setCurrentSystem] = useState(null) // ziwei, bazi, astrology, etc.
  
  // Loading & Toast
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' })
  
  // Auth Modal
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login') // login or register
  const [authForm, setAuthForm] = useState({
    email: '',
    password: '',
    display_name: ''
  })
  
  // Chart Data
  const [chartLocked, setChartLocked] = useState(false)
  const [chartSummary, setChartSummary] = useState(null)
  const [chartAnalysis, setChartAnalysis] = useState(null) // 完整的綜合分析
  const [systemAnalysis, setSystemAnalysis] = useState({}) // 各系統詳細分析
  
  // Wizard for chart creation
  const [wizardStep, setWizardStep] = useState(1)
  const [chartForm, setChartForm] = useState({
    birth_date: '',
    birth_time: '',
    birth_location: '',
    gender: '男',
    chinese_name: '',
    english_name: ''
  })

  // ========== API Helpers ==========
  const authHeaders = useMemo(() => {
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    return headers
  }, [token])

  const apiCall = async (path, payload = null, method = 'POST') => {
    try {
      const options = {
        method: payload ? method : 'GET',
        headers: authHeaders
      }
      if (payload) {
        options.body = JSON.stringify(payload)
      }
      const response = await fetch(`${apiBase}${path}`, options)
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.message || data.error || 'API 失敗')
      }
      return data
    } catch (error) {
      showToast(error.message, 'error')
      throw error
    }
  }

  // ========== Toast System ==========
  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000)
  }

  // ========== Auth Functions ==========
  const handleLogin = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/auth/login', {
        email: authForm.email.trim(),
        password: authForm.password.trim()
      })
      localStorage.setItem('aetheria_token', data.token)
      setToken(data.token)
      setShowAuthModal(false)
      showToast('登入成功！', 'success')
      setAuthForm({ email: '', password: '', display_name: '' })
    } catch (error) {
      // Error already shown by apiCall
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/auth/register', {
        email: authForm.email.trim(),
        password: authForm.password.trim(),
        display_name: authForm.display_name.trim(),
        consents: { terms_accepted: true, data_usage_accepted: true }
      })
      localStorage.setItem('aetheria_token', data.token)
      setToken(data.token)
      setShowAuthModal(false)
      showToast('註冊成功！', 'success')
      setAuthForm({ email: '', password: '', display_name: '' })
    } catch (error) {
      // Error already shown by apiCall
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('aetheria_token')
    setToken('')
    setProfile(null)
    setChartLocked(false)
    setChartSummary(null)
    setCurrentView('home')
    showToast('已登出', 'info')
  }

  // ========== Profile & Chart ==========
  const fetchProfile = async () => {
    if (!token) return
    try {
      const data = await apiCall('/api/profile', null, 'GET')
      setProfile(data.profile)
    } catch (error) {
      localStorage.removeItem('aetheria_token')
      setToken('')
    }
  }

  const checkChartLock = async () => {
    if (!profile) return
    try {
      const data = await apiCall(`/api/chart/get-lock?user_id=${profile.user_id}`, null, 'GET')
      if (data.locked) {
        setChartLocked(true)
        setChartSummary(data.chart_structure)
      }
    } catch (error) {
      // No chart locked yet
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [token])

  useEffect(() => {
    if (profile) {
      checkChartLock()
    }
  }, [profile])

  // ========== Chart Creation Wizard ==========
  const handleCreateChart = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/chart/initial-analysis', {
        user_id: profile.user_id,
        birth_date: chartForm.birth_date,
        birth_time: chartForm.birth_time,
        birth_location: chartForm.birth_location,
        gender: chartForm.gender
      })
      setChartSummary(data.chart_structure)
      setWizardStep(5)
      showToast('命盤建立成功！', 'success')
    } catch (error) {
      // Error already shown
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmLock = async () => {
    setLoading(true)
    try {
      await apiCall('/api/chart/confirm-lock', {
        user_id: profile.user_id
      })
      setChartLocked(true)
      setWizardStep(6)
      showToast('命盤已鎖定！', 'success')
    } catch (error) {
      // Error already shown
    } finally {
      setLoading(false)
    }
  }

  // ========== Render Functions ==========
  
  // Landing Page (未登入)
  const renderLanding = () => (
    <div className="landing">
      <div className="landing-header">
        <div className="landing-brand">
          <div className="landing-logo">A</div>
          <div>
            <div className="landing-title">Aetheria</div>
            <div className="landing-subtitle">超個人化命理分析系統</div>
          </div>
        </div>
        <div className="landing-actions">
          <button 
            className="btn btn-ghost" 
            onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
          >
            登入
          </button>
          <button 
            className="btn btn-primary" 
            onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
          >
            開始使用
          </button>
        </div>
      </div>

      <div className="landing-hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span>✨</span>
            <span>v1.9.0 戰略側寫系統上線</span>
          </div>
          <h1 className="hero-title">
            從算命到戰略<br />AI 命理決策顧問
          </h1>
          <p className="hero-description">
            整合六大命理系統，結合 Gemini AI 深度推理，
            提供結論優先、證據充足、可執行的戰略建議
          </p>
          <div className="hero-cta">
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
            >
              免費開始分析
            </button>
            <button className="btn btn-secondary btn-lg">
              了解更多
            </button>
          </div>
        </div>
      </div>

      <div className="landing-features">
        <h2 className="features-title">六大命理系統 + 戰略側寫</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔮</div>
            <div className="feature-title">紫微斗數</div>
            <div className="feature-desc">
              LLM-First 排盤，深度格局分析，流年運勢預測
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">☯️</div>
            <div className="feature-title">八字命理</div>
            <div className="feature-desc">
              四柱排盤，十神分析，大運流年推算
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⭐</div>
            <div className="feature-title">西洋占星術</div>
            <div className="feature-desc">
              Swiss Ephemeris 專業星曆，本命盤合盤分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔢</div>
            <div className="feature-title">靈數學</div>
            <div className="feature-desc">
              生命靈數，天賦潛能，流年週期分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <div className="feature-title">姓名學</div>
            <div className="feature-desc">
              五格剖象法，81數理，三才配置分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎴</div>
            <div className="feature-title">塔羅牌</div>
            <div className="feature-desc">
              多種牌陣，每日一牌，情境解讀指引
            </div>
          </div>
          <div className="feature-card" style={{gridColumn: 'span 2', background: 'var(--color-strategic-bg)', borderColor: 'var(--color-strategic)'}}>
            <div className="feature-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
            <div className="feature-title" style={{color: 'var(--color-strategic)'}}>
              ✨ 戰略側寫系統
            </div>
            <div className="feature-desc">
              全息圖譜、生辰校正、關係生態位、決策沙盒 - 四大戰略工具，
              從被動算命升級為主動決策支援
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  // Dashboard Home (已登入首頁)
  const renderDashboardHome = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">歡迎回來，{profile?.display_name || '用戶'}</h1>
        <p className="content-subtitle">
          {chartLocked 
            ? '您的命盤已鎖定，可以開始使用各項分析功能'
            : '請先建立並鎖定您的命盤'}
        </p>
      </div>
      <div className="content-body">
        {!chartLocked ? (
          <div className="card">
            <div className="card-header">
              <div className="card-title">🔮 建立您的專屬命盤</div>
              <div className="card-subtitle">
                命盤是所有分析的基礎，建立後將永久鎖定，確保一致性
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-primary"
                onClick={() => setCurrentView('chart')}
              >
                開始建立命盤
              </button>
            </div>
          </div>
        ) : (
          <div className="dashboard-grid">
            <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-primary)'}}>🔮</div>
              <div className="stat-content">
                <div className="stat-value">已鎖定</div>
                <div className="stat-label">命盤狀態</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-accent)'}}>📊</div>
              <div className="stat-content">
                <div className="stat-value">6 + 1</div>
                <div className="stat-label">可用系統</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
              <div className="stat-content">
                <div className="stat-value">戰略版</div>
                <div className="stat-label">進階功能</div>
              </div>
            </div>
          </div>
        )}

        <div style={{marginTop: 'var(--spacing-2xl)'}}>
          <h2 style={{fontSize: '24px', fontWeight: 700, marginBottom: 'var(--spacing-lg)'}}>
            快速開始
          </h2>
          <div className="dashboard-grid">
            <div 
              className="card" 
              style={{cursor: 'pointer'}}
              onClick={() => setCurrentView('systems')}
            >
              <div className="card-header">
                <div className="card-title">📚 六大命理系統</div>
              </div>
              <div className="card-body">
                紫微斗數、八字命理、西洋占星術、靈數學、姓名學、塔羅牌
              </div>
            </div>
            <div 
              className="card card-strategic" 
              style={{cursor: 'pointer'}}
              onClick={() => setCurrentView('strategic')}
            >
              <div className="card-header">
                <div className="card-title" style={{color: 'var(--color-strategic)'}}>
                  🎯 戰略側寫系統
                </div>
              </div>
              <div className="card-body">
                全息圖譜、生辰校正、關係生態位、決策沙盒
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )

  // Chart Creation View
  const renderChartView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">建立專屬命盤</h1>
        <p className="content-subtitle">請按照步驟填寫完整的出生資料</p>
      </div>
      <div className="content-body">
        {/* Wizard Progress */}
        <div className="progress-wizard">
          {[
            { step: 1, label: '基本資料' },
            { step: 2, label: '出生資訊' },
            { step: 3, label: '確認資料' },
            { step: 4, label: '分析中' },
            { step: 5, label: '預覽結果' },
            { step: 6, label: '完成' }
          ].map(item => (
            <div 
              key={item.step}
              className={`wizard-step ${wizardStep === item.step ? 'active' : ''} ${wizardStep > item.step ? 'completed' : ''}`}
            >
              <div className="wizard-circle">
                {wizardStep > item.step ? '✓' : item.step}
              </div>
              <div className="wizard-label">{item.label}</div>
            </div>
          ))}
        </div>

        {/* Step 1: Basic Info */}
        {wizardStep === 1 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 1：基本資料</div>
              <div className="card-subtitle">請提供您的姓名與性別</div>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">中文姓名</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.chinese_name}
                  onChange={(e) => setChartForm({...chartForm, chinese_name: e.target.value})}
                  placeholder="例：張小明"
                />
              </div>
              <div className="form-group">
                <label className="form-label">英文姓名（選填，用於靈數學分析）</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.english_name}
                  onChange={(e) => setChartForm({...chartForm, english_name: e.target.value})}
                  placeholder="例：ZHANG XIAO MING"
                />
              </div>
              <div className="form-group">
                <label className="form-label">性別</label>
                <select 
                  className="form-select"
                  value={chartForm.gender}
                  onChange={(e) => setChartForm({...chartForm, gender: e.target.value})}
                >
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="未指定">未指定</option>
                </select>
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-primary"
                onClick={() => setWizardStep(2)}
                disabled={!chartForm.chinese_name}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Birth Info */}
        {wizardStep === 2 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 2：出生資訊</div>
              <div className="card-subtitle">請提供準確的出生日期、時間與地點</div>
            </div>
            <div className="card-body">
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">出生日期</label>
                  <input 
                    type="date"
                    className="form-input"
                    value={chartForm.birth_date}
                    onChange={(e) => setChartForm({...chartForm, birth_date: e.target.value})}
                  />
                  <div className="form-hint">請使用國曆日期</div>
                </div>
                <div className="form-group">
                  <label className="form-label">出生時間</label>
                  <input 
                    type="time"
                    className="form-input"
                    value={chartForm.birth_time}
                    onChange={(e) => setChartForm({...chartForm, birth_time: e.target.value})}
                  />
                  <div className="form-hint">請盡可能提供準確時間</div>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">出生地點</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.birth_location}
                  onChange={(e) => setChartForm({...chartForm, birth_location: e.target.value})}
                  placeholder="例：台灣台北市"
                />
                <div className="form-hint">用於計算經緯度與時區</div>
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => setWizardStep(1)}
              >
                上一步
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setWizardStep(3)}
                disabled={!chartForm.birth_date || !chartForm.birth_time || !chartForm.birth_location}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirmation */}
        {wizardStep === 3 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 3：確認資料</div>
              <div className="card-subtitle">請仔細核對資料無誤後送出</div>
            </div>
            <div className="card-body">
              <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                <div><strong>姓名：</strong>{chartForm.chinese_name}</div>
                {chartForm.english_name && <div><strong>英文名：</strong>{chartForm.english_name}</div>}
                <div><strong>性別：</strong>{chartForm.gender}</div>
                <div><strong>出生日期：</strong>{chartForm.birth_date}</div>
                <div><strong>出生時間：</strong>{chartForm.birth_time}</div>
                <div><strong>出生地點：</strong>{chartForm.birth_location}</div>
              </div>
              <div style={{marginTop: 'var(--spacing-lg)', padding: 'var(--spacing-md)', background: 'var(--color-warning)', opacity: 0.1, borderRadius: 'var(--radius-md)', color: 'var(--color-text)'}}>
                ⚠️ 命盤一旦鎖定後無法修改，請確保資料正確
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => setWizardStep(2)}
              >
                上一步
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setWizardStep(4)
                  handleCreateChart()
                }}
                disabled={loading}
              >
                {loading ? '分析中...' : '開始分析'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Loading */}
        {wizardStep === 4 && (
          <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
            <div style={{textAlign: 'center'}}>
              <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
              <div style={{fontSize: '18px', fontWeight: 600, marginBottom: 'var(--spacing-sm)'}}>
                AI 正在分析您的命盤...
              </div>
              <div style={{color: 'var(--color-text-muted)'}}>
                這可能需要 30-60 秒
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Preview */}
        {wizardStep === 5 && chartSummary && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 5：命盤總攬</div>
              <div className="card-subtitle">您的專屬命盤已生成，請確認資訊無誤</div>
            </div>
            <div className="card-body">
              <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
                {/* 紫微斗數 */}
                <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                  <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>🔮 紫微斗數</div>
                  <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                    <div><strong>命宮：</strong>{chartSummary.命宮?.宮位} - {chartSummary.命宮?.主星?.join('、')}</div>
                    {chartSummary.核心格局 && <div><strong>格局：</strong>{chartSummary.核心格局.join('、')}</div>}
                    {chartSummary.五行局 && <div><strong>五行局：</strong>{chartSummary.五行局}</div>}
                  </div>
                </div>
                
                {/* 八字命理 */}
                {chartSummary.八字 && (
                  <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                    <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>☯️ 八字命理</div>
                    <div><strong>四柱：</strong>{chartSummary.八字.年柱} {chartSummary.八字.月柱} {chartSummary.八字.日柱} {chartSummary.八字.時柱}</div>
                  </div>
                )}
                
                {/* 其他系統提示 */}
                <div style={{padding: 'var(--spacing-md)', background: 'var(--color-info)', opacity: 0.1, borderRadius: 'var(--radius-md)', color: 'var(--color-text)'}}>
                  <div>✨ 鎖定後可使用：西洋占星、靈數學、姓名學、塔羅牌等完整分析</div>
                </div>
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => {
                  setWizardStep(1)
                  setChartSummary(null)
                }}
              >
                重新建立
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleConfirmLock}
                disabled={loading}
              >
                {loading ? '鎖定中...' : '確認鎖定'}
              </button>
            </div>
          </div>
        )}

        {/* Step 6: Complete */}
        {wizardStep === 6 && (
          <div className="card" style={{textAlign: 'center', padding: 'var(--spacing-3xl)'}}>
            <div style={{fontSize: '64px', marginBottom: 'var(--spacing-lg)'}}>✨</div>
            <div style={{fontSize: '28px', fontWeight: 700, marginBottom: 'var(--spacing-md)'}}>
              命盤建立完成！
            </div>
            <div style={{color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-2xl)'}}>
              您現在可以使用所有分析功能了
            </div>
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => setCurrentView('home')}
            >
              開始探索
            </button>
          </div>
        )}
      </div>
    </>
  )

  // Systems View
  const renderSystemsView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">六大命理系統</h1>
        <p className="content-subtitle">選擇您想使用的分析系統</p>
      </div>
      <div className="content-body">
        <div className="dashboard-grid">
          {[
            { id: 'ziwei', icon: '🔮', name: '紫微斗數', desc: 'LLM-First 排盤與格局分析' },
            { id: 'bazi', icon: '☯️', name: '八字命理', desc: '四柱排盤與十神分析' },
            { id: 'astrology', icon: '⭐', name: '西洋占星術', desc: '本命盤與合盤分析' },
            { id: 'numerology', icon: '🔢', name: '靈數學', desc: '生命靈數與天賦分析' },
            { id: 'name', icon: '📝', name: '姓名學', desc: '五格剖象法分析' },
            { id: 'tarot', icon: '🎴', name: '塔羅牌', desc: '牌陣占卜與指引' }
          ].map(system => (
            <div 
              key={system.id}
              className="card"
              style={{cursor: 'pointer'}}
              onClick={() => {
                if (!chartLocked) {
                  showToast('請先建立並鎖定命盤', 'warning')
                  return
                }
                setCurrentSystem(system.id)
                setCurrentView('system-detail')
              }}
            >
              <div style={{fontSize: '48px', marginBottom: 'var(--spacing-md)'}}>{system.icon}</div>
              <div className="card-title">{system.name}</div>
              <div className="card-body">{system.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )

  // Strategic View
  const renderStrategicView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title" style={{color: 'var(--color-strategic)'}}>
          🎯 戰略側寫系統
        </h1>
        <p className="content-subtitle">從算命到戰略 - 四大決策工具</p>
      </div>
      <div className="content-body">
        <div className="dashboard-grid">
          {[
            { 
              id: 'profile', 
              icon: '🌐', 
              name: '全息生命圖譜', 
              desc: 'Meta Profile 整合，結論優先架構，資源流向分析' 
            },
            { 
              id: 'rectify', 
              icon: '🕐', 
              name: '生辰校正器', 
              desc: '反推時辰邏輯，多系統驗證，Top 3 可能性' 
            },
            { 
              id: 'ecosystem', 
              icon: '🤝', 
              name: '關係生態位', 
              desc: '資源流動分析，功能互補評估，合作風險與紅利' 
            },
            { 
              id: 'decision', 
              icon: '⚖️', 
              name: '決策沙盒', 
              desc: '雙路徑模擬，因果推演，代價收益分析' 
            }
          ].map(tool => (
            <div 
              key={tool.id}
              className="card card-strategic"
              style={{cursor: 'pointer'}}
              onClick={() => showToast(`${tool.name} 功能開發中`, 'info')}
            >
              <div style={{fontSize: '48px', marginBottom: 'var(--spacing-md)'}}>{tool.icon}</div>
              <div className="card-title" style={{color: 'var(--color-strategic)'}}>{tool.name}</div>
              <div className="card-body">{tool.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )

  // Overview View (我的命盤總攬)
  const renderOverviewView = () => {
    const [overviewData, setOverviewData] = useState(null)
    const [loadingOverview, setLoadingOverview] = useState(false)

    const fetchOverview = async () => {
      setLoadingOverview(true)
      try {
        const data = await apiCall('/api/integrated/profile', {
          user_id: profile.user_id,
          birth_date: chartForm.birth_date || chartSummary?.birth_date,
          birth_time: chartForm.birth_time || chartSummary?.birth_time,
          birth_location: chartForm.birth_location || chartSummary?.birth_location
        })
        setOverviewData(data)
        setChartAnalysis(data)
      } catch (error) {
        showToast('載入失敗', 'error')
      } finally {
        setLoadingOverview(false)
      }
    }

    useEffect(() => {
      if (chartLocked && !overviewData) {
        fetchOverview()
      }
    }, [chartLocked])

    return (
      <>
        <div className="content-header">
          <h1 className="content-title">我的命盤總攬</h1>
          <p className="content-subtitle">綜合六大系統的完整分析</p>
        </div>
        <div className="content-body">
          {loadingOverview ? (
            <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                <div>正在載入您的命盤分析...</div>
              </div>
            </div>
          ) : overviewData ? (
            <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
              <div className="card">
                <div className="card-header">
                  <div className="card-title">📊 綜合分析</div>
                </div>
                <div className="card-body" style={{whiteSpace: 'pre-wrap'}}>
                  {overviewData.analysis || overviewData.summary || '分析資料載入中...'}
                </div>
              </div>
              
              <div className="dashboard-grid">
                {[
                  { id: 'ziwei', icon: '🔮', name: '紫微斗數' },
                  { id: 'bazi', icon: '☯️', name: '八字命理' },
                  { id: 'astrology', icon: '⭐', name: '西洋占星' },
                  { id: 'numerology', icon: '🔢', name: '靈數學' },
                  { id: 'name', icon: '📝', name: '姓名學' },
                  { id: 'tarot', icon: '🎴', name: '塔羅牌' }
                ].map(system => (
                  <div 
                    key={system.id}
                    className="card"
                    style={{cursor: 'pointer'}}
                    onClick={() => {
                      setCurrentSystem(system.id)
                      setCurrentView('system-detail')
                    }}
                  >
                    <div className="card-header">
                      <div className="card-title">{system.icon} {system.name}</div>
                    </div>
                    <div className="card-footer">
                      <button className="btn btn-ghost">查看詳細</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="card-body">尚無分析資料</div>
            </div>
          )}
        </div>
      </>
    )
  }

  // System Detail View (單一系統詳細分析)
  const renderSystemDetailView = () => {
    const [systemData, setSystemData] = useState(null)
    const [loadingSystem, setLoadingSystem] = useState(false)

    const fetchSystemAnalysis = async () => {
      if (!currentSystem || !chartLocked) return
      
      setLoadingSystem(true)
      try {
        let endpoint = ''
        let payload = {
          user_id: profile.user_id,
          birth_date: chartForm.birth_date || chartSummary?.birth_date,
          birth_time: chartForm.birth_time || chartSummary?.birth_time,
          birth_location: chartForm.birth_location || chartSummary?.birth_location
        }

        switch (currentSystem) {
          case 'ziwei':
            // 使用 initial-analysis 已有的資料
            setSystemData({ analysis: '紫微斗數詳細分析請使用「流年運勢」等專門功能' })
            setLoadingSystem(false)
            return
          case 'bazi':
            endpoint = '/api/bazi/analysis'
            break
          case 'astrology':
            endpoint = '/api/astrology/natal'
            break
          case 'numerology':
            endpoint = '/api/numerology/profile'
            payload.name = profile.display_name || chartForm.chinese_name
            break
          case 'name':
            endpoint = '/api/name/analyze'
            payload.chinese_name = chartForm.chinese_name || profile.display_name
            payload.gender = chartForm.gender
            break
          case 'tarot':
            showToast('塔羅牌需要選擇牌陣和問題', 'info')
            setLoadingSystem(false)
            return
          default:
            showToast('系統不存在', 'error')
            setLoadingSystem(false)
            return
        }

        const data = await apiCall(endpoint, payload)
        setSystemData(data)
        setSystemAnalysis(prev => ({ ...prev, [currentSystem]: data }))
      } catch (error) {
        showToast(`載入${currentSystem}失敗`, 'error')
      } finally {
        setLoadingSystem(false)
      }
    }

    useEffect(() => {
      if (currentSystem && chartLocked && !systemAnalysis[currentSystem]) {
        fetchSystemAnalysis()
      } else if (systemAnalysis[currentSystem]) {
        setSystemData(systemAnalysis[currentSystem])
      }
    }, [currentSystem, chartLocked])

    const getSystemInfo = (id) => {
      const systems = {
        ziwei: { icon: '🔮', name: '紫微斗數' },
        bazi: { icon: '☯️', name: '八字命理' },
        astrology: { icon: '⭐', name: '西洋占星術' },
        numerology: { icon: '🔢', name: '靈數學' },
        name: { icon: '📝', name: '姓名學' },
        tarot: { icon: '🎴', name: '塔羅牌' }
      }
      return systems[id] || { icon: '❓', name: '未知系統' }
    }

    const systemInfo = getSystemInfo(currentSystem)

    return (
      <>
        <div className="content-header">
          <button 
            className="btn btn-ghost" 
            onClick={() => setCurrentView('systems')}
            style={{marginBottom: 'var(--spacing-md)'}}
          >
            ← 返回
          </button>
          <h1 className="content-title">{systemInfo.icon} {systemInfo.name}</h1>
          <p className="content-subtitle">詳細分析報告</p>
        </div>
        <div className="content-body">
          {loadingSystem ? (
            <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                <div>正在分析...</div>
              </div>
            </div>
          ) : systemData ? (
            <div className="card">
              <div className="card-body" style={{whiteSpace: 'pre-wrap'}}>
                {systemData.analysis || systemData.interpretation || JSON.stringify(systemData, null, 2)}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="card-body">尚無分析資料</div>
            </div>
          )}
        </div>
      </>
    )
  }

  // Settings View
  const renderSettingsView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">設定</h1>
        <p className="content-subtitle">管理您的帳號與偏好設定</p>
      </div>
      <div className="content-body">
        <div className="card">
          <div className="card-header">
            <div className="card-title">個人資料</div>
          </div>
          <div className="card-body">
            <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
              <div><strong>User ID：</strong>{profile?.user_id}</div>
              <div><strong>Email：</strong>{profile?.email}</div>
              <div><strong>顯示名稱：</strong>{profile?.display_name || '未設定'}</div>
            </div>
          </div>
        </div>

        <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
          <div className="card-header">
            <div className="card-title">API 設定</div>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">API 位址</label>
              <input 
                type="text"
                className="form-input"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
              />
            </div>
          </div>
          <div className="card-footer">
            <button 
              className="btn btn-primary"
              onClick={() => {
                localStorage.setItem('aetheria_api_base', apiBase)
                showToast('API 位址已更新', 'success')
              }}
            >
              儲存
            </button>
          </div>
        </div>

        <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
          <div className="card-header">
            <div className="card-title">帳號管理</div>
          </div>
          <div className="card-footer">
            <button 
              className="btn btn-secondary"
              onClick={handleLogout}
            >
              登出
            </button>
          </div>
        </div>
      </div>
    </>
  )

  // Sidebar Navigation
  const renderSidebar = () => (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-logo">A</div>
          <div>
            <div className="sidebar-title">Aetheria</div>
          </div>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-section">
          <div 
            className={`nav-item ${currentView === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentView('home')}
          >
            <div className="nav-icon">🏠</div>
            <div>首頁</div>
          </div>
          <div 
            className={`nav-item ${currentView === 'chart' ? 'active' : ''}`}
            onClick={() => setCurrentView('chart')}
          >
            <div className="nav-icon">🔮</div>
            <div>建立命盤</div>
            {!chartLocked && <div className="nav-badge">!</div>}
          </div>
          {chartLocked && (
            <div 
              className={`nav-item ${currentView === 'overview' ? 'active' : ''}`}
              onClick={() => setCurrentView('overview')}
            >
              <div className="nav-icon">📊</div>
              <div>我的命盤</div>
            </div>
          )}
        </div>

        <div className="nav-section">
          <div className="nav-label">命理系統</div>
          <div 
            className={`nav-item ${currentView === 'systems' ? 'active' : ''}`}
            onClick={() => setCurrentView('systems')}
          >
            <div className="nav-icon">📚</div>
            <div>六大系統</div>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-label">進階功能</div>
          <div 
            className={`nav-item strategic ${currentView === 'strategic' ? 'active' : ''}`}
            onClick={() => setCurrentView('strategic')}
          >
            <div className="nav-icon">🎯</div>
            <div>戰略側寫</div>
            <div className="nav-badge">NEW</div>
          </div>
        </div>

        <div className="nav-section">
          <div 
            className={`nav-item ${currentView === 'settings' ? 'active' : ''}`}
            onClick={() => setCurrentView('settings')}
          >
            <div className="nav-icon">⚙️</div>
            <div>設定</div>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-card">
          <div className="user-avatar">
            {profile?.display_name?.charAt(0) || profile?.email?.charAt(0) || 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{profile?.display_name || '用戶'}</div>
            <div className="user-email">{profile?.email}</div>
          </div>
        </div>
      </div>
    </div>
  )

  // Auth Modal
  const renderAuthModal = () => {
    if (!showAuthModal) return null

    const handleSubmit = (e) => {
      e.preventDefault()
      if (authMode === 'login') {
        handleLogin()
      } else {
        handleRegister()
      }
    }

    return (
      <div className="modal-backdrop" onClick={() => setShowAuthModal(false)}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <div className="modal-title">
              {authMode === 'login' ? '登入 Aetheria' : '註冊 Aetheria'}
            </div>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {authMode === 'register' && (
                <div className="form-group">
                  <label className="form-label">顯示名稱</label>
                  <input 
                    type="text"
                    className="form-input"
                    value={authForm.display_name}
                    onChange={(e) => setAuthForm({...authForm, display_name: e.target.value})}
                    placeholder="您想被稱呼的名字"
                    autoComplete="name"
                  />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Email</label>
                <input 
                  type="email"
                  className="form-input"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  placeholder="your@email.com"
                  autoComplete="email"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">密碼</label>
                <input 
                  type="password"
                  className="form-input"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                  placeholder="至少 8 碼"
                  autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                  required
                  minLength={8}
                />
              </div>
              <div style={{fontSize: '13px', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-md)'}}>
                {authMode === 'login' ? (
                  <>
                    還沒有帳號？
                    <span 
                      style={{color: 'var(--color-primary)', cursor: 'pointer', marginLeft: 'var(--spacing-xs)'}}
                      onClick={() => setAuthMode('register')}
                    >
                      立即註冊
                    </span>
                  </>
                ) : (
                  <>
                    已有帳號？
                    <span 
                      style={{color: 'var(--color-primary)', cursor: 'pointer', marginLeft: 'var(--spacing-xs)'}}
                      onClick={() => setAuthMode('login')}
                    >
                      直接登入
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button 
                type="button"
                className="btn btn-ghost"
                onClick={() => setShowAuthModal(false)}
              >
                取消
              </button>
              <button 
                type="submit"
                className="btn btn-primary"
                disabled={loading || !authForm.email || !authForm.password || (authMode === 'register' && authForm.password.length < 8)}
              >
                {loading ? '處理中...' : (authMode === 'login' ? '登入' : '註冊')}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // Toast Notification
  const renderToast = () => {
    if (!toast.show) return null

    const icons = {
      success: '✓',
      error: '✕',
      info: 'ℹ'
    }

    return (
      <div className="toast-container">
        <div className={`toast toast-${toast.type}`}>
          <div className="toast-icon">{icons[toast.type]}</div>
          <div className="toast-content">
            <div className="toast-message">{toast.message}</div>
          </div>
        </div>
      </div>
    )
  }

  // ========== Main Render ==========
  return (
    <div className="app">
      <div className="app-bg"></div>
      
      {!token ? (
        // Landing Page
        renderLanding()
      ) : (
        // Dashboard
        <div className="dashboard">
          {renderSidebar()}
          <div className="main-content">
            {currentView === 'home' && renderDashboardHome()}
            {currentView === 'chart' && renderChartView()}
            {currentView === 'overview' && renderOverviewView()}
            {currentView === 'systems' && renderSystemsView()}
            {currentView === 'system-detail' && renderSystemDetailView()}
            {currentView === 'strategic' && renderStrategicView()}
            {currentView === 'settings' && renderSettingsView()}
          </div>
        </div>
      )}

      {renderAuthModal()}
      {renderToast()}
    </div>
  )
}

export default App
