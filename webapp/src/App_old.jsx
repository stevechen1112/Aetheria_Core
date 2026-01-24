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
  { label: '感情關係', value: '感情關係卡住了，能幫我看看嗎？' },
  { label: '近期決策', value: '近期有重大決策，要注意什麼？' },
]

function App() {
  const [apiBase, setApiBase] = useState(
    localStorage.getItem('aetheria_api_base') || 'http://localhost:5001'
  )
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [authStatus, setAuthStatus] = useState('尚未登入')
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
  const [prefStatus, setPrefStatus] = useState('偏好尚未更新')

  const [chartPayload, setChartPayload] = useState(defaultPayload)
  const [chartStatus, setChartStatus] = useState('尚未建立命盤')
  const [chartSummary, setChartSummary] = useState(null)

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
      setAuthStatus('尚未登入')
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
      setAuthStatus(`已登入：${data.profile.display_name || data.profile.email}`)
      setGuideStep(2)
    } catch {
      storeToken('')
      setAuthStatus('登入狀態失效，請重新登入')
      setGuideStep(1)
    }
  }

  useEffect(() => {
    refreshProfile()
  }, [token])

  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000)
  }

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
      await apiFetch(
        '/api/profile',
        { preferences },
        'PATCH'
      )
      setTone(preferences.tone)
      showToast('偏好已更新', 'success')
    } catch (error) {
      showToast(`更新失敗：${error.message}`, 'error')
    } finally {
      setLoading(false)
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
        { role: 'ai', text: '我已完成命盤分析，若內容符合，請按下「確認鎖盤」。', time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) },
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
        { role: 'ai', text: '命盤已鎖定完成。我會以此為基礎回答你接下來的問題。', time: new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }) },
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
            <div>
              <div className="title">Aetheria</div>
              <div className="subtitle">命理老師互動 App</div>
            </div>
          </div>
          <div className="env">
            <label htmlFor="apiBase">API</label>
            <input
              id="apiBase"
              value={apiBase}
              onChange={(event) => setApiBase(event.target.value)}
            />
            <button onClick={saveApiBase}>儲存</button>
          </div>
        </header>

        <main className="app-content">
          {activeTab === 'home' && (
            <>
              <section className="panel hero">
                <div>
                  <h1>像真人命理老師一樣的對話體驗</h1>
                  <p>
                    我會先理解你的心情，再釐清重點，最後給出可行的建議與下一步。你可以在這裡完成命盤建立、
                    鎖盤確認，並與 Aetheria 進行後續對話。
                  </p>
                  <div className="chips">
                    <span>共感 → 釐清 → 解讀 → 建議</span>
                    <span>鎖盤一致性</span>
                    <span>溫度語氣控制</span>
                  </div>
                </div>
                <div className="hero-card">
                  <h3>快速開始</h3>
                  <ol>
                    <li>註冊或登入帳號</li>
                    <li>填寫基本資料並建立命盤</li>
                    <li>確認鎖盤並開始對話</li>
                  </ol>
                  <div className="hero-actions">
                    <button className="primary" onClick={() => setActiveTab('chart')}>
                      建立命盤
                    </button>
                    <button className="ghost" onClick={() => setActiveTab('chat')}>
                      開始對話
                    </button>
                  </div>
                </div>
              </section>

              <section className="panel guide">
                {[1, 2, 3].map((step) => (
                  <div
                    key={step}
                    className={`guide-step ${guideStep === step ? 'active' : ''}`}
                  >
                    {step === 1 && (
                      <>
                        <div className="guide-title">第 1 步：建立你的帳號</div>
                        <p>這能保存命盤與對話摘要，讓我逐步更理解你。</p>
                      </>
                    )}
                    {step === 2 && (
                      <>
                        <div className="guide-title">第 2 步：建立命盤並鎖定</div>
                        <p>鎖盤後，我會以同一份命盤作為所有回應的基礎。</p>
                      </>
                    )}
                    {step === 3 && (
                      <>
                        <div className="guide-title">第 3 步：開始對話</div>
                        <p>你可以從事業、感情、近期決策開始，我會逐步陪你拆解。</p>
                      </>
                    )}
                  </div>
                ))}
              </section>
            </>
          )}

          {activeTab === 'chart' && (
            <section className="grid">
              <div className="panel">
                <h2>建立命盤</h2>
                <div className="form-grid">
                  <label>
                    使用者 ID
                    <input
                      value={chartPayload.user_id}
                      onChange={(event) =>
                        setChartPayload((prev) => ({ ...prev, user_id: event.target.value }))
                      }
                      placeholder="user_001"
                    />
                  </label>
                  <label>
                    出生日期
                    <input
                      value={chartPayload.birth_date}
                      onChange={(event) =>
                        setChartPayload((prev) => ({ ...prev, birth_date: event.target.value }))
                      }
                      placeholder="農曆68年9月23日"
                    />
                  </label>
                  <label>
                    出生時間
                    <input
                      value={chartPayload.birth_time}
                      onChange={(event) =>
                        setChartPayload((prev) => ({ ...prev, birth_time: event.target.value }))
                      }
                      placeholder="23:58"
                    />
                  </label>
                  <label>
                    出生地點
                    <input
                      value={chartPayload.birth_location}
                      onChange={(event) =>
                        setChartPayload((prev) => ({ ...prev, birth_location: event.target.value }))
                      }
                      placeholder="台灣彰化市"
                    />
                  </label>
                  <label>
                    性別
                    <select
                      value={chartPayload.gender}
                      onChange={(event) =>
                        setChartPayload((prev) => ({ ...prev, gender: event.target.value }))
                      }
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
                      <div><strong>關鍵宮位：</strong>{summaryText.keyPalaces}</div>
                    </>
                  ) : (
                    '這裡會顯示命盤重點與鎖盤狀態'
                  )}
                </div>
              </div>
            </section>
          )}

          {activeTab === 'chat' && (
            <section className="panel chat">
              <div className="chat-header">
                <div>
                  <h2>與命理老師對話</h2>
                  <p>保持「真人感」：簡短共感 → 分析 → 建議 → 下一步提問</p>
                </div>
                <div className="tone">
                  <label>語氣</label>
                  <select value={tone} onChange={(event) => setTone(event.target.value)}>
                    <option value="溫暖專業">溫暖專業</option>
                    <option value="理性直接">理性直接</option>
                    <option value="安撫支持">安撫支持</option>
                  </select>
                </div>
              </div>

              <div className="summary">{conversationSummary}</div>

              <div className="chat-suggestions">
                <div className="suggestions-title">推薦問題</div>
                <div className="suggestions">
                  {suggestedQuestions.map((question) => (
                    <button
                      key={question.label}
                      className="suggestion"
                      onClick={() => setMessageInput(question.value)}
                    >
                      {question.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="chat-log">
                {chatLog.map((entry, index) => (
                  <div key={`${entry.role}-${index}`} className={`msg ${entry.role}`}>
                    {entry.text}
                  </div>
                ))}
              </div>

              <div className="chat-input">
                <input
                  value={messageInput}
                  onChange={(event) => setMessageInput(event.target.value)}
                  onKeyDown={(event) => event.key === 'Enter' && handleSendMessage()}
                  placeholder="想了解感情或事業，可以直接說"
                />
                <button className="primary" onClick={handleSendMessage}>
                  送出
                </button>
              </div>
              <div className="hint">建議提問：事業方向、感情走向、近期決策、家庭關係</div>
            </section>
          )}

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
            className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <span className="nav-icon">👤</span>
            <span className="nav-label">我的</span>
          </button>
        </nav>
      </div>
    </div>
  )
}

export default App
