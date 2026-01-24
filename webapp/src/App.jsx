import { useEffect, useMemo, useState } from 'react'
import './App.css'

const defaultPayload = {
  user_id: '',
  birth_date: '',
  birth_time: '',
  birth_location: '',
  gender: '男',
}

const suggestedQuestions = [
  { label: '事業方向', value: '我最近工作有點迷惘，事業方向怎麼看？' },
  { label: '感情關係', value: '感情關係卡住了,能幫我看看嗎？' },
  { label: '近期決策', value: '近期有重大決策，要注意什麼？' },
]

function App() {
  const [apiBase, setApiBase] = useState(
    localStorage.getItem('aetheria_api_base') || 'http://localhost:5001'
  )
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [guideStep, setGuideStep] = useState(1)
  const [activeTab, setActiveTab] = useState('home')
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' })

  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    display_name: '',
  })
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })

  const [profile, setProfile] = useState(null)
  const [preferences, setPreferences] = useState({
    tone: '溫暖專業',
    response_length: '適中',
  })

  const [chartPayload, setChartPayload] = useState(defaultPayload)
  const [chartStatus, setChartStatus] = useState('尚未建立命盤')
  const [chartSummary, setChartSummary] = useState(null)

  const [strategicPayload, setStrategicPayload] = useState({
    birth_date: '',
    birth_time: '',
    chinese_name: '',
    english_name: '',
    gender: '男',
    analysis_focus: 'career',
    include_bazi: true,
    include_astrology: true,
    include_tarot: true,
    longitude: 120.54,
    latitude: 24.08,
    timezone: 'Asia/Taipei',
    city: 'Changhua',
    nation: 'TW',
  })
  const [strategicResult, setStrategicResult] = useState(null)
  const [strategicWarnings, setStrategicWarnings] = useState([])
  const [rectifyPayload, setRectifyPayload] = useState({
    birth_date: '',
    gender: '男',
    traits: '',
    longitude: 120.54,
  })
  const [rectifyResult, setRectifyResult] = useState(null)
  
  // 關係生態與決策沙盒
  const [ecoPayload, setEcoPayload] = useState({
    person_a: { name: '', birth_date: '', birth_time: '' },
    person_b: { name: '', birth_date: '', birth_time: '' },
  })
  const [ecoResult, setEcoResult] = useState(null)
  
  const [decisionPayload, setDecisionPayload] = useState({
    user_name: '',
    birth_date: '',
    birth_time: '',
    question: '',
    option_a: '',
    option_b: '',
  })
  const [decisionResult, setDecisionResult] = useState(null)
  
  const [strategicLoading, setStrategicLoading] = useState(false)

  const [tone, setTone] = useState('溫暖專業')
  const [messageInput, setMessageInput] = useState('')
  const [chatLog, setChatLog] = useState([
    {
      role: 'ai',
      text: '你好，我是 Aetheria。請先建立並確認命盤，我會用溫暖專業的方式回應你。',
      time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
    },
  ])
  const [conversationSummary, setConversationSummary] = useState('對話摘要會顯示在這裡')

  const authHeaders = useMemo(() => {
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    return headers
  }, [token])

  const saveApiBase = () => {
    localStorage.setItem('aetheria_api_base', apiBase)
  }

  const storeToken = (nextToken) => {
    if (nextToken) {
      localStorage.setItem('aetheria_token', nextToken)
      setToken(nextToken)
    } else {
      localStorage.removeItem('aetheria_token')
      setToken('')
    }
  }

  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000)
  }

  const apiFetch = async (path, payload, method = 'POST') => {
    const response = await fetch(`${apiBase}${path}`, {
      method,
      headers: authHeaders,
      body: payload ? JSON.stringify(payload) : undefined,
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.message || data.error || 'API 失敗')
    }
    return data
  }

  const apiGet = async (path) => {
    const response = await fetch(`${apiBase}${path}`, { headers: authHeaders })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.message || data.error || 'API 失敗')
    }
    return data
  }

  const refreshProfile = async () => {
    if (!token) {
      setProfile(null)
      setGuideStep(1)
      return
    }
    try {
      const data = await apiGet('/api/profile')
      setProfile(data.profile)
      setPreferences((prev) => ({
        tone: data.preferences?.tone || prev.tone,
        response_length: data.preferences?.response_length || prev.response_length,
      }))
      setTone(data.preferences?.tone || tone)
      setChartPayload((prev) => ({ ...prev, user_id: data.profile.user_id }))
      setGuideStep(2)
    } catch {
      storeToken('')
      setGuideStep(1)
    }
  }

  useEffect(() => {
    refreshProfile()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  useEffect(() => {
    if (!profile && activeTab !== 'home') {
      setActiveTab('home')
    }
  }, [profile, activeTab])

  const handleRegister = async () => {
    setLoading(true)
    try {
      const data = await apiFetch('/api/auth/register', {
        email: registerForm.email.trim(),
        password: registerForm.password.trim(),
        display_name: registerForm.display_name.trim(),
        consents: { terms_accepted: true, data_usage_accepted: true },
      })
      storeToken(data.token)
      setShowAuthModal(false)
      showToast('註冊成功！', 'success')
    } catch (error) {
      showToast(`註冊失敗：${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    setLoading(true)
    try {
      const data = await apiFetch('/api/auth/login', {
        email: loginForm.email.trim(),
        password: loginForm.password.trim(),
      })
      storeToken(data.token)
      setShowAuthModal(false)
      showToast('登入成功！', 'success')
    } catch (error) {
      showToast(`登入失敗：${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    setLoading(true)
    try {
      await apiFetch('/api/auth/logout', {})
    } catch {
      // ignore
    }
    storeToken('')
    setProfile(null)
    setGuideStep(1)
    setActiveTab('home')
    showToast('已登出', 'info')
    setLoading(false)
  }

  const handleSavePrefs = async () => {
    setLoading(true)
    try {
      await apiFetch('/api/profile', { preferences }, 'PATCH')
      setTone(preferences.tone)
      showToast('偏好已更新', 'success')
    } catch (error) {
      showToast(`更新失敗：${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleStrategicProfile = async () => {
    setStrategicLoading(true)
    try {
      const payload = {
        ...strategicPayload,
        longitude: strategicPayload.longitude ? Number(strategicPayload.longitude) : undefined,
        latitude: strategicPayload.latitude ? Number(strategicPayload.latitude) : undefined,
      }
      const data = await apiFetch('/api/strategic/profile', payload)
      setStrategicResult(data.data)
      setStrategicWarnings(data.data?.warnings || [])
      showToast('戰略側寫完成', 'success')
    } catch (error) {
      showToast(`戰略側寫失敗：${error.message}`, 'error')
    } finally {
      setStrategicLoading(false)
    }
  }

  const handleBirthRectify = async () => {
    setStrategicLoading(true)
    try {
      const traits = rectifyPayload.traits
        .split(/\n|,|，/)
        .map((item) => item.trim())
        .filter(Boolean)

      if (traits.length === 0) {
        showToast('請輸入至少一條特質或事件', 'error')
        setStrategicLoading(false)
        return
      }

      const payload = {
        birth_date: rectifyPayload.birth_date,
        gender: rectifyPayload.gender,
        traits,
        longitude: rectifyPayload.longitude ? Number(rectifyPayload.longitude) : undefined,
      }
      const data = await apiFetch('/api/strategic/birth-rectify', payload)
      setRectifyResult(data.data)
      showToast('生辰校正完成', 'success')
    } catch (error) {
      showToast(`生辰校正失敗：${error.message}`, 'error')
    } finally {
      setStrategicLoading(false)
    }
  }

  const handleEcoAnalysis = async () => {
    if (!ecoPayload.person_a.birth_date || !ecoPayload.person_b.birth_date) {
      showToast('請輸入雙方出生日期', 'error')
      return
    }
    setStrategicLoading(true)
    try {
      const data = await apiFetch('/api/strategic/relationship', ecoPayload)
      setEcoResult(data.data)
      showToast('關係分析完成', 'success')
    } catch (error) {
      showToast(`分析失敗：${error.message}`, 'error')
    } finally {
      setStrategicLoading(false)
    }
  }

  const handleDecisionSim = async () => {
    if (!decisionPayload.birth_date || !decisionPayload.question || !decisionPayload.option_a || !decisionPayload.option_b) {
      showToast('請完整填寫出生日期、核心問題與兩條路徑', 'error')
      return
    }
    setStrategicLoading(true)
    try {
      const data = await apiFetch('/api/strategic/decision', decisionPayload)
      setDecisionResult(data.data)
      showToast('模擬完成', 'success')
    } catch (error) {
      showToast(`模擬失敗：${error.message}`, 'error')
    } finally {
      setStrategicLoading(false)
    }
  }

  const handleCreateChart = async () => {
    if (
      !chartPayload.user_id ||
      !chartPayload.birth_date ||
      !chartPayload.birth_time ||
      !chartPayload.birth_location
    ) {
      showToast('請完整填寫所有資料', 'error')
      return
    }
    setLoading(true)
    setChartStatus('命盤分析中...')
    try {
      const data = await apiFetch('/api/chart/initial-analysis', chartPayload)
      setChartStatus('命盤已生成，等待確認鎖盤')
      setChartSummary(data.structure)
      setChatLog((prev) => [
        ...prev,
        {
          role: 'ai',
          text: '我已完成命盤分析，若內容符合，請按下「確認鎖盤」。',
          time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
        },
      ])
      setGuideStep(2)
      showToast('命盤分析完成', 'success')
    } catch (error) {
      showToast(`命盤生成失敗：${error.message}`, 'error')
      setChartStatus('生成失敗')
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmLock = async () => {
    if (!chartPayload.user_id) {
      showToast('請先填寫使用者 ID', 'error')
      return
    }
    setLoading(true)
    setChartStatus('鎖盤確認中...')
    try {
      const data = await apiFetch('/api/chart/confirm-lock', {
        user_id: chartPayload.user_id,
      })
      setChartStatus(`命盤已鎖定（${data.locked_at || '完成'}）`)
      setChatLog((prev) => [
        ...prev,
        {
          role: 'ai',
          text: '命盤已鎖定完成。我會以此為基礎回答你接下來的問題。',
          time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
        },
      ])
      setGuideStep(3)
      showToast('命盤已鎖定', 'success')
    } catch (error) {
      showToast(`鎖盤失敗：${error.message}`, 'error')
      setChartStatus('鎖盤失敗')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async () => {
    if (!chartPayload.user_id) {
      showToast('請先完成命盤建立', 'error')
      return
    }
    if (!messageInput.trim()) return
    const message = messageInput.trim()
    const currentTime = new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    setChatLog((prev) => [...prev, { role: 'user', text: message, time: currentTime }])
    setMessageInput('')
    setLoading(true)
    try {
      const data = await apiFetch('/api/chat/message', {
        user_id: chartPayload.user_id,
        message,
        tone,
      })
      setChatLog((prev) => [...prev, { role: 'ai', text: data.reply || '已收到', time: currentTime }])
      if (data.conversation_summary) {
        setConversationSummary(data.conversation_summary)
      }
    } catch (error) {
      showToast(`連線失敗：${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const summaryText = useMemo(() => {
    if (!chartSummary) return '這裡會顯示命盤重點與鎖盤狀態'
    const main = chartSummary['命宮'] || {}
    const mainStars = (main['主星'] || []).join('、')
    const keyPalaces = ['官祿宮', '財帛宮', '夫妻宮']
      .map((name) => {
        const palace = (chartSummary['十二宮'] || {})[name]
        if (!palace) return null
        const stars = (palace['主星'] || []).join('、')
        return `${name}:${stars || '-'}`
      })
      .filter(Boolean)
      .join(' / ')
    return {
      mainPalace: main['宮位'] || '-',
      mainStars: mainStars || '-',
      keyPalaces: keyPalaces || '-',
    }
  }, [chartSummary])

  return (
    <div className="app">
      <div className="bg" />
      
      {/* Toast 通知 */}
      {toast.show && (
        <div className={`toast toast-${toast.type}`}>
          {toast.message}
        </div>
      )}

      {/* 登入/註冊 Modal */}
      {showAuthModal && (
        <div className="modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{authMode === 'login' ? '會員登入' : '會員註冊'}</h2>
              <button className="close-btn" onClick={() => setShowAuthModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              {authMode === 'login' ? (
                <div className="form-grid">
                  <label>
                    Email
                    <input
                      type="email"
                      value={loginForm.email}
                      onChange={(e) => setLoginForm((prev) => ({ ...prev, email: e.target.value }))}
                      placeholder="you@example.com"
                    />
                  </label>
                  <label>
                    密碼
                    <input
                      type="password"
                      value={loginForm.password}
                      onChange={(e) => setLoginForm((prev) => ({ ...prev, password: e.target.value }))}
                      placeholder="輸入密碼"
                    />
                  </label>
                </div>
              ) : (
                <div className="form-grid">
                  <label>
                    Email
                    <input
                      type="email"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, email: e.target.value }))}
                      placeholder="you@example.com"
                    />
                  </label>
                  <label>
                    密碼
                    <input
                      type="password"
                      value={registerForm.password}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, password: e.target.value }))}
                      placeholder="至少 8 個字元"
                    />
                  </label>
                  <label>
                    顯示名稱
                    <input
                      type="text"
                      value={registerForm.display_name}
                      onChange={(e) => setRegisterForm((prev) => ({ ...prev, display_name: e.target.value }))}
                      placeholder="你的名字"
                    />
                  </label>
                </div>
              )}
              <div className="actions">
                <button 
                  className="primary" 
                  onClick={authMode === 'login' ? handleLogin : handleRegister}
                  disabled={loading}
                >
                  {loading ? '處理中...' : (authMode === 'login' ? '登入' : '註冊')}
                </button>
              </div>
              <div className="modal-footer">
                {authMode === 'login' ? (
                  <span>還沒有帳號？<a onClick={() => setAuthMode('register')}>立即註冊</a></span>
                ) : (
                  <span>已有帳號？<a onClick={() => setAuthMode('login')}>返回登入</a></span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="app-shell">
        <header className="app-bar">
          <div className="brand">
            <div className="logo">A</div>
            <div className="title">Aetheria</div>
          </div>
          {profile && (
            <button className="profile-btn" onClick={() => setActiveTab('profile')}>
              <span>👤</span>
            </button>
          )}
        </header>

        <main className="app-content">
          {/* 首頁 */}
          {activeTab === 'home' && (
            <>
              {!profile ? (
                <div className="welcome-screen">
                  <div className="welcome-content">
                    <div className="welcome-logo">✨</div>
                    <h1 className="welcome-title">Aetheria</h1>
                    <p className="welcome-subtitle">AI 紫微斗數命理諮詢</p>
                    <div className="welcome-actions">
                      <button 
                        className="btn-welcome-primary" 
                        onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
                      >
                        開始使用
                      </button>
                      <button 
                        className="btn-welcome-ghost" 
                        onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                      >
                        已有帳號登入
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <div className="panel welcome-back">
                    <h2>歡迎回來，{profile.display_name || '用戶'}</h2>
                    <p className="helper">選擇下方功能開始使用</p>
                  </div>

                  <div className="feature-grid">
                    <button className="feature-card" onClick={() => setActiveTab('chart')}>
                      <div className="feature-icon">⭐</div>
                      <div className="feature-title">我的命盤</div>
                      <div className="feature-desc">{chartSummary ? '已建立命盤' : '建立你的紫微命盤'}</div>
                    </button>
                    <button className="feature-card" onClick={() => setActiveTab('chat')}>
                      <div className="feature-icon">💬</div>
                      <div className="feature-title">AI 對話</div>
                      <div className="feature-desc">開始命理諮詢</div>
                    </button>
                    <button className="feature-card" onClick={() => setActiveTab('strategic')}>
                      <div className="feature-icon">🧭</div>
                      <div className="feature-title">戰略側寫</div>
                      <div className="feature-desc">全息側寫與生辰校正</div>
                    </button>
                  </div>

                  {suggestedQuestions.length > 0 && (
                    <div className="panel">
                      <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>💡 常見問題</h3>
                      <div className="quick-questions">
                        {suggestedQuestions.map((q) => (
                          <button
                            key={q.label}
                            className="question-chip"
                            onClick={() => {
                              setMessageInput(q.value)
                              setActiveTab('chat')
                            }}
                          >
                            {q.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {/* 命盤頁 */}
          {activeTab === 'chart' && (
            <>
              <div className="panel">
                <h2>建立命盤</h2>
                <p className="helper">請填寫完整的出生資料，我會根據紫微斗數排盤。</p>
                <div className="form-grid">
                  <label>
                    User ID
                    <input
                      type="text"
                      value={chartPayload.user_id}
                      onChange={(e) => setChartPayload((prev) => ({ ...prev, user_id: e.target.value }))}
                      placeholder="輸入 user_id"
                    />
                  </label>
                  <label>
                    出生日期
                    <input
                      type="date"
                      value={chartPayload.birth_date}
                      onChange={(e) => setChartPayload((prev) => ({ ...prev, birth_date: e.target.value }))}
                    />
                  </label>
                  <label>
                    出生時間
                    <input
                      type="time"
                      value={chartPayload.birth_time}
                      onChange={(e) => setChartPayload((prev) => ({ ...prev, birth_time: e.target.value }))}
                    />
                  </label>
                  <label>
                    出生地點
                    <input
                      type="text"
                      value={chartPayload.birth_location}
                      onChange={(e) => setChartPayload((prev) => ({ ...prev, birth_location: e.target.value }))}
                      placeholder="例：台北"
                    />
                  </label>
                  <label>
                    性別
                    <select
                      value={chartPayload.gender}
                      onChange={(e) => setChartPayload((prev) => ({ ...prev, gender: e.target.value }))}
                    >
                      <option value="男">男</option>
                      <option value="女">女</option>
                      <option value="未指定">未指定</option>
                    </select>
                  </label>
                </div>
                <div className="actions">
                  <button className="primary" onClick={handleCreateChart} disabled={loading}>
                    {loading ? '分析中...' : '建立命盤'}
                  </button>
                  <button className="ghost" onClick={handleConfirmLock} disabled={loading}>
                    {loading ? '鎖定中...' : '確認鎖盤'}
                  </button>
                </div>
                <div className="status">{chartStatus}</div>
              </div>

              <div className="panel">
                <h2>命盤摘要</h2>
                <div className={`summary ${chartSummary ? '' : 'empty'}`}>
                  {chartSummary ? (
                    <>
                      <div><strong>命宮：</strong>{summaryText.mainPalace}</div>
                      <div><strong>主星：</strong>{summaryText.mainStars}</div>
                      <div><strong>三方四正：</strong>{summaryText.keyPalaces}</div>
                    </>
                  ) : (
                    '這裡會顯示命盤重點與鎖盤狀態'
                  )}
                </div>
              </div>
            </>
          )}

          {/* 對話頁 */}
          {activeTab === 'chat' && (
            <div className="chat-container">
              <div className="chat-header panel">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h2>AI 對話</h2>
                  <select 
                    value={tone} 
                    onChange={(e) => setTone(e.target.value)}
                    style={{ width: 'auto', fontSize: '12px' }}
                  >
                    <option value="溫暖專業">溫暖專業</option>
                    <option value="理性直接">理性直接</option>
                    <option value="安撫支持">安撫支持</option>
                  </select>
                </div>
                <div className="suggested-questions">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q.label}
                      className="suggested-chip"
                      onClick={() => setMessageInput(q.value)}
                    >
                      {q.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="chat-messages">
                {chatLog.map((msg, idx) => (
                  <div key={idx} className={`bubble-wrapper bubble-${msg.role}`}>
                    <div className="bubble">
                      <div className="bubble-text">{msg.text}</div>
                      {msg.time && <div className="bubble-time">{msg.time}</div>}
                    </div>
                  </div>
                ))}
              </div>

              <div className="chat-input-container">
                <input
                  type="text"
                  className="chat-input"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="輸入你的問題..."
                  onKeyDown={(e) => e.key === 'Enter' && !loading && handleSendMessage()}
                  disabled={loading}
                />
                <button 
                  className="send-btn" 
                  onClick={handleSendMessage}
                  disabled={loading || !messageInput.trim()}
                >
                  {loading ? '⋯' : '➤'}
                </button>
              </div>
            </div>
          )}

          {/* 戰略側寫 */}
          {activeTab === 'strategic' && (
            <>
              <div className="panel">
                <h2>戰略側寫</h2>
                <p className="helper">輸入基本資料，獲得結論優先的全息側寫。</p>
                <div className="form-grid">
                  <label>
                    中文姓名
                    <input
                      type="text"
                      value={strategicPayload.chinese_name}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, chinese_name: e.target.value }))
                      }
                      placeholder="例：陳宥竹"
                    />
                  </label>
                  <label>
                    英文姓名
                    <input
                      type="text"
                      value={strategicPayload.english_name}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, english_name: e.target.value }))
                      }
                      placeholder="例：CHEN YOU ZHU"
                    />
                  </label>
                  <label>
                    出生日期
                    <input
                      type="date"
                      value={strategicPayload.birth_date}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, birth_date: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    出生時間
                    <input
                      type="time"
                      value={strategicPayload.birth_time}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, birth_time: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    性別
                    <select
                      value={strategicPayload.gender}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, gender: e.target.value }))
                      }
                    >
                      <option value="男">男</option>
                      <option value="女">女</option>
                      <option value="未指定">未指定</option>
                    </select>
                  </label>
                  <label>
                    分析焦點
                    <select
                      value={strategicPayload.analysis_focus}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, analysis_focus: e.target.value }))
                      }
                    >
                      <option value="general">整體定位</option>
                      <option value="career">事業定位</option>
                      <option value="relationship">關係定位</option>
                      <option value="wealth">財務策略</option>
                      <option value="health">身心管理</option>
                    </select>
                  </label>
                  <label>
                    經度
                    <input
                      type="number"
                      step="0.0001"
                      value={strategicPayload.longitude}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, longitude: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    緯度
                    <input
                      type="number"
                      step="0.0001"
                      value={strategicPayload.latitude}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, latitude: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    城市
                    <input
                      type="text"
                      value={strategicPayload.city}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, city: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    國家
                    <input
                      type="text"
                      value={strategicPayload.nation}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, nation: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    時區
                    <input
                      type="text"
                      value={strategicPayload.timezone}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, timezone: e.target.value }))
                      }
                    />
                  </label>
                </div>
                <div className="checkbox-row">
                  <label>
                    <input
                      type="checkbox"
                      checked={strategicPayload.include_bazi}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, include_bazi: e.target.checked }))
                      }
                    />
                    八字
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={strategicPayload.include_astrology}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, include_astrology: e.target.checked }))
                      }
                    />
                    占星
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={strategicPayload.include_tarot}
                      onChange={(e) =>
                        setStrategicPayload((prev) => ({ ...prev, include_tarot: e.target.checked }))
                      }
                    />
                    塔羅
                  </label>
                </div>
                <div className="actions">
                  <button className="primary" onClick={handleStrategicProfile} disabled={strategicLoading}>
                    {strategicLoading ? '分析中...' : '產生側寫'}
                  </button>
                </div>
                {strategicWarnings.length > 0 && (
                  <div className="status">⚠️ {strategicWarnings.join('；')}</div>
                )}
              </div>

              <div className="panel">
                <h2>戰略結論</h2>
                {strategicResult ? (
                  <>
                    <div className="result-box">{strategicResult.strategic_interpretation}</div>
                    <div className="result-meta">
                      <details>
                        <summary>Meta Profile</summary>
                        <pre>{JSON.stringify(strategicResult.meta_profile, null, 2)}</pre>
                      </details>
                      <details>
                        <summary>原始輸入摘要</summary>
                        <pre>
                          {JSON.stringify(
                            {
                              numerology: strategicResult.numerology,
                              name_analysis: strategicResult.name_analysis,
                              bazi: strategicResult.bazi,
                              astrology_core: strategicResult.astrology_core,
                              tarot: strategicResult.tarot,
                            },
                            null,
                            2
                          )}
                        </pre>
                      </details>
                    </div>
                  </>
                ) : (
                  <div className="summary empty">尚未產生側寫結果</div>
                )}
              </div>

              <div className="panel">
                <h2>生辰校正</h2>
                <p className="helper">輸入特質或重大事件，系統將列出最可能的時辰。</p>
                <div className="form-grid">
                  <label>
                    出生日期
                    <input
                      type="date"
                      value={rectifyPayload.birth_date}
                      onChange={(e) =>
                        setRectifyPayload((prev) => ({ ...prev, birth_date: e.target.value }))
                      }
                    />
                  </label>
                  <label>
                    性別
                    <select
                      value={rectifyPayload.gender}
                      onChange={(e) =>
                        setRectifyPayload((prev) => ({ ...prev, gender: e.target.value }))
                      }
                    >
                      <option value="男">男</option>
                      <option value="女">女</option>
                      <option value="未指定">未指定</option>
                    </select>
                  </label>
                  <label>
                    經度
                    <input
                      type="number"
                      step="0.0001"
                      value={rectifyPayload.longitude}
                      onChange={(e) =>
                        setRectifyPayload((prev) => ({ ...prev, longitude: e.target.value }))
                      }
                    />
                  </label>
                  <label className="full-width">
                    特質 / 事件（可換行或逗號分隔）
                    <textarea
                      rows={4}
                      value={rectifyPayload.traits}
                      onChange={(e) =>
                        setRectifyPayload((prev) => ({ ...prev, traits: e.target.value }))
                      }
                      placeholder="例：強勢領導\n偏好獨立作業\n重大轉職"
                    />
                  </label>
                </div>
                <div className="actions">
                  <button className="primary" onClick={handleBirthRectify} disabled={strategicLoading}>
                    {strategicLoading ? '分析中...' : '開始校正'}
                  </button>
                </div>
                {rectifyResult ? (
                  <div className="result-box" style={{ marginTop: '16px' }}>
                    {rectifyResult.interpretation}
                  </div>
                ) : (
                  <div className="summary empty">尚未產生校正結果</div>
                )}
              </div>

              <div className="panel">
                <h2>關係生態位</h2>
                <p className="helper">分析雙方的資源流動與功能定位（不只看感情）。</p>
                <div className="form-grid">
                  <div style={{gridColumn: '1/-1', fontWeight: 'bold', marginTop: '8px'}}>甲方（決策者）</div>
                  <label>姓名
                    <input type="text" value={ecoPayload.person_a.name} onChange={e=>setEcoPayload(p=>({...p, person_a: {...p.person_a, name: e.target.value}}))} />
                  </label>
                  <label>生日
                    <input type="date" value={ecoPayload.person_a.birth_date} onChange={e=>setEcoPayload(p=>({...p, person_a: {...p.person_a, birth_date: e.target.value}}))} />
                  </label>
                  <label>時間
                    <input type="time" value={ecoPayload.person_a.birth_time} onChange={e=>setEcoPayload(p=>({...p, person_a: {...p.person_a, birth_time: e.target.value}}))} />
                  </label>

                  <div style={{gridColumn: '1/-1', fontWeight: 'bold', marginTop: '8px'}}>乙方（合作者/伴侶）</div>
                  <label>姓名
                    <input type="text" value={ecoPayload.person_b.name} onChange={e=>setEcoPayload(p=>({...p, person_b: {...p.person_b, name: e.target.value}}))} />
                  </label>
                  <label>生日
                    <input type="date" value={ecoPayload.person_b.birth_date} onChange={e=>setEcoPayload(p=>({...p, person_b: {...p.person_b, birth_date: e.target.value}}))} />
                  </label>
                  <label>時間
                    <input type="time" value={ecoPayload.person_b.birth_time} onChange={e=>setEcoPayload(p=>({...p, person_b: {...p.person_b, birth_time: e.target.value}}))} />
                  </label>
                </div>
                <div className="actions">
                  <button className="primary" onClick={handleEcoAnalysis} disabled={strategicLoading}>
                    {strategicLoading ? '分析中...' : '開始生態分析'}
                  </button>
                </div>
                {ecoResult && (
                  <div className="result-box" style={{marginTop: '16px'}}>
                    {ecoResult.interpretation}
                  </div>
                )}
                {ecoResult?.warnings?.length > 0 && (
                  <div className="status">⚠️ {ecoResult.warnings.join('；')}</div>
                )}
              </div>

              <div className="panel">
                <h2>決策沙盒</h2>
                <p className="helper">輸入當前困境與兩條可能路徑，系統將進行沙盒模擬。</p>
                <div className="form-grid">
                  <label>決策者姓名
                    <input type="text" value={decisionPayload.user_name} onChange={e=>setDecisionPayload(p=>({...p, user_name: e.target.value}))} />
                  </label>
                  <label>出生日期
                    <input type="date" value={decisionPayload.birth_date} onChange={e=>setDecisionPayload(p=>({...p, birth_date: e.target.value}))} />
                  </label>
                  <label>出生時間
                    <input type="time" value={decisionPayload.birth_time} onChange={e=>setDecisionPayload(p=>({...p, birth_time: e.target.value}))} />
                  </label>
                  <label className="full-width">核心問題
                    <input type="text" placeholder="例：公司該擴張還是保守？" value={decisionPayload.question} onChange={e=>setDecisionPayload(p=>({...p, question: e.target.value}))} />
                  </label>
                  <label className="full-width">路徑 A（選項一）
                    <input type="text" placeholder="例：激進擴張，借貸融資" value={decisionPayload.option_a} onChange={e=>setDecisionPayload(p=>({...p, option_a: e.target.value}))} />
                  </label>
                  <label className="full-width">路徑 B（選項二）
                    <input type="text" placeholder="例：穩健保守，現金為王" value={decisionPayload.option_b} onChange={e=>setDecisionPayload(p=>({...p, option_b: e.target.value}))} />
                  </label>
                </div>
                <div className="actions">
                  <button className="primary" onClick={handleDecisionSim} disabled={strategicLoading}>
                    {strategicLoading ? '模擬中...' : '開始模擬'}
                  </button>
                </div>
                {decisionResult && (
                  <div className="result-box" style={{marginTop: '16px'}}>
                    {decisionResult.interpretation}
                  </div>
                )}
                {decisionResult?.warnings?.length > 0 && (
                  <div className="status">⚠️ {decisionResult.warnings.join('；')}</div>
                )}
              </div>
            </>
          )}

          {/* 個人資料頁 */}
          {activeTab === 'profile' && (
            <>
              {profile ? (
                <>
                  <div className="panel">
                    <h2>會員資訊</h2>
                    <div className="profile-info">
                      <div className="profile-avatar">{profile.display_name?.[0] || profile.email[0].toUpperCase()}</div>
                      <div>
                        <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>
                          {profile.display_name || '未設定名稱'}
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--muted)' }}>{profile.email}</div>
                        <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '8px' }}>ID: {profile.user_id}</div>
                      </div>
                    </div>
                  </div>

                  <div className="panel">
                    <h2>個人化偏好</h2>
                    <p className="helper">調整你喜歡的對話風格。</p>
                    <div className="form-grid">
                      <label>
                        偏好語氣
                        <select
                          value={preferences.tone}
                          onChange={(e) => setPreferences((prev) => ({ ...prev, tone: e.target.value }))}
                        >
                          <option value="溫暖專業">溫暖專業</option>
                          <option value="理性直接">理性直接</option>
                          <option value="安撫支持">安撫支持</option>
                        </select>
                      </label>
                      <label>
                        回覆長度
                        <select
                          value={preferences.response_length}
                          onChange={(e) => setPreferences((prev) => ({ ...prev, response_length: e.target.value }))}
                        >
                          <option value="精簡">精簡</option>
                          <option value="適中">適中</option>
                          <option value="深入">深入</option>
                        </select>
                      </label>
                    </div>
                    <div className="actions">
                      <button className="ghost" onClick={handleSavePrefs} disabled={loading}>
                        {loading ? '儲存中...' : '儲存偏好'}
                      </button>
                    </div>
                  </div>

                  <div className="panel">
                    <h2>系統設定</h2>
                    <div className="form-grid">
                      <label>
                        API 位址
                        <input
                          type="text"
                          value={apiBase}
                          onChange={(e) => setApiBase(e.target.value)}
                          placeholder="http://localhost:5001"
                        />
                      </label>
                    </div>
                    <div className="actions">
                      <button className="ghost" onClick={saveApiBase}>
                        儲存設定
                      </button>
                    </div>
                  </div>

                  <div className="panel">
                    <h2>帳號管理</h2>
                    <div className="actions">
                      <button className="ghost" onClick={handleLogout} disabled={loading}>
                        {loading ? '登出中...' : '登出帳號'}
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="panel">
                  <h2>尚未登入</h2>
                  <p className="helper">登入後可以使用完整功能。</p>
                  <div className="actions">
                    <button 
                      className="primary" 
                      onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
                    >
                      立即登入
                    </button>
                    <button 
                      className="ghost" 
                      onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
                    >
                      註冊帳號
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </main>

        {profile && (
          <nav className="bottom-nav">
            <button
              className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
              onClick={() => setActiveTab('home')}
            >
              <span className="nav-icon">🏠</span>
              <span className="nav-label">首頁</span>
            </button>
            <button
              className={`nav-item ${activeTab === 'chart' ? 'active' : ''}`}
              onClick={() => setActiveTab('chart')}
            >
              <span className="nav-icon">⭐</span>
              <span className="nav-label">命盤</span>
            </button>
            <button
              className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <span className="nav-icon">💬</span>
              <span className="nav-label">對話</span>
            </button>
            <button
              className={`nav-item ${activeTab === 'strategic' ? 'active' : ''}`}
              onClick={() => setActiveTab('strategic')}
            >
              <span className="nav-icon">🧭</span>
              <span className="nav-label">戰略</span>
            </button>
            <button
              className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <span className="nav-icon">👤</span>
              <span className="nav-label">我的</span>
            </button>
          </nav>
        )}
      </div>
    </div>
  )
}

export default App
