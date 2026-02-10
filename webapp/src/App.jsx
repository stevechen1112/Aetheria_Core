import { useState, useEffect, useCallback } from 'react'
import { AetheriaProvider } from './contexts/AetheriaContext'
import ChatContainer from './ChatContainer'
import SessionSidebar from './SessionSidebar'
import './App.css'

/* ==========================================
   Aetheria Core v2.0 — Chat-First Agent UI
   
   純聊天介面，無舊版選單/Landing Page。
   訪客可直接開始對話，無須先註冊。
   ========================================== */

function App() {
  // ========== API Base ==========
  const [apiBase] = useState(() => {
    const host = window.location.hostname
    const protocol = window.location.protocol
    const isLocal = host === 'localhost' || host === '127.0.0.1'
    const saved = localStorage.getItem('aetheria_api_base')
    if (saved) return saved
    return isLocal ? `${protocol}//${host}:5001` : `${protocol}//${host}`
  })

  // ========== Auth State ==========
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [userId, setUserId] = useState(localStorage.getItem('aetheria_user_id') || '')
  const [authReady, setAuthReady] = useState(false)
  const [authError, setAuthError] = useState('')

  // ========== Auth Modal ==========
  const [showAuth, setShowAuth] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState({ email: '', password: '', display_name: '' })
  const [authLoading, setAuthLoading] = useState(false)

  // ========== Sidebar State ==========
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('aetheria_sidebar_collapsed')
    return saved === 'true'
  })

  useEffect(() => {
    localStorage.setItem('aetheria_sidebar_collapsed', sidebarCollapsed)
  }, [sidebarCollapsed])

  // ========== Auto-provision guest on first visit ==========
  const provisionGuest = useCallback(async () => {
    try {
      const guestId = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
      const resp = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: `${guestId}@guest.aetheria.local`,
          password: guestId,
          display_name: '訪客',
          consents: { terms_accepted: true, data_usage_accepted: true }
        })
      })
      if (!resp.ok) throw new Error('Guest provision failed')
      const data = await resp.json()
      localStorage.setItem('aetheria_token', data.token)
      localStorage.setItem('aetheria_user_id', data.user_id)
      setToken(data.token)
      setUserId(data.user_id)
      return data.token
    } catch (err) {
      console.error('Guest provision error:', err)
      setAuthError('無法連接到伺服器，請確認後端已啟動')
      return null
    }
  }, [apiBase])

  // ========== Validate existing session or create guest ==========
  useEffect(() => {
    const init = async () => {
      if (token) {
        // Validate existing token
        try {
          const resp = await fetch(`${apiBase}/api/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (resp.ok) {
            const data = await resp.json()
            setUserId(data.profile?.user_id || userId)
            setAuthReady(true)
            return
          }
          // Token expired — clear and re-provision
          localStorage.removeItem('aetheria_token')
          localStorage.removeItem('aetheria_user_id')
          setToken('')
          setUserId('')
        } catch {
          // Server might be down
        }
      }
      // No valid token — auto-provision guest
      const newToken = await provisionGuest()
      setAuthReady(!!newToken)
    }
    init()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ========== Login / Register ==========
  const handleAuth = async () => {
    setAuthLoading(true)
    setAuthError('')
    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register'
      const payload = authMode === 'login'
        ? { email: authForm.email.trim(), password: authForm.password.trim() }
        : {
            email: authForm.email.trim(),
            password: authForm.password.trim(),
            display_name: authForm.display_name.trim() || '使用者',
            consents: { terms_accepted: true, data_usage_accepted: true }
          }

      const resp = await fetch(`${apiBase}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await resp.json()
      if (!resp.ok) {
        setAuthError(data.message || '登入失敗')
        return
      }
      localStorage.setItem('aetheria_token', data.token)
      localStorage.setItem('aetheria_user_id', data.user_id)
      setToken(data.token)
      setUserId(data.user_id)
      setShowAuth(false)
      setAuthForm({ email: '', password: '', display_name: '' })
    } catch {
      setAuthError('無法連接到伺服器')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('aetheria_token')
    localStorage.removeItem('aetheria_user_id')
    setToken('')
    setUserId('')
    setAuthReady(false)
    // Re-provision guest
    provisionGuest().then(t => setAuthReady(!!t))
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAuth()
    }
  }

  // ========== Loading State ==========
  if (!authReady) {
    return (
      <div className="app-loading">
        <div className="loading-content">
          <div className="loading-icon">🔮</div>
          <h2>Aetheria</h2>
          <p>{authError || '正在連接...'}</p>
          {authError && (
            <button className="retry-btn" onClick={() => {
              setAuthError('')
              provisionGuest().then(t => setAuthReady(!!t))
            }}>
              重試
            </button>
          )}
        </div>
      </div>
    )
  }

  // ========== Main Chat-First UI ==========
  return (
    <AetheriaProvider apiBase={apiBase} token={token}>
      <div className="app-root">
        {/* Top Bar — minimal */}
        <header className="app-topbar">
          <div className="topbar-brand">
            <span className="brand-icon">🔮</span>
            <span className="brand-name">Aetheria</span>
            <span className="brand-version">Agent 2.0</span>
          </div>
          <div className="topbar-actions">
            {userId && !userId.startsWith('guest_') ? (
              <div className="user-info">
                <span className="user-badge">👤</span>
                <button className="btn-topbar" onClick={handleLogout}>登出</button>
              </div>
            ) : (
              <button className="btn-topbar btn-login" onClick={() => setShowAuth(true)}>
                登入 / 註冊
              </button>
            )}
          </div>
        </header>

        {/* Main area: Sidebar + Chat */}
        <main className="app-main">
          {/* Mobile backdrop when sidebar is open */}
          {!sidebarCollapsed && (
            <div
              className="sidebar-backdrop visible"
              onClick={() => setSidebarCollapsed(true)}
            />
          )}
          <SessionSidebar
            apiBase={apiBase}
            token={token}
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed(prev => !prev)}
            onSessionSelected={() => {
              // Auto-close sidebar on mobile after session select
              if (window.innerWidth <= 768) setSidebarCollapsed(true)
            }}
          />
          <div className="app-chat-area">
            <ChatContainer
              apiBase={apiBase}
              token={token}
              userId={userId}
              embedded={false}
              sidebarCollapsed={sidebarCollapsed}
              onToggleSidebar={() => setSidebarCollapsed(prev => !prev)}
            />
          </div>
        </main>

        {/* Auth Modal */}
        {showAuth && (
          <div className="modal-overlay" onClick={() => setShowAuth(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>{authMode === 'login' ? '登入' : '註冊'}</h3>
                <button className="modal-close" onClick={() => setShowAuth(false)}>✕</button>
              </div>
              <div className="modal-body">
                {authMode === 'register' && (
                  <input
                    type="text"
                    placeholder="顯示名稱"
                    value={authForm.display_name}
                    onChange={e => setAuthForm(f => ({ ...f, display_name: e.target.value }))}
                    onKeyDown={handleKeyDown}
                  />
                )}
                <input
                  type="email"
                  placeholder="Email"
                  value={authForm.email}
                  onChange={e => setAuthForm(f => ({ ...f, email: e.target.value }))}
                  onKeyDown={handleKeyDown}
                />
                <input
                  type="password"
                  placeholder="密碼"
                  value={authForm.password}
                  onChange={e => setAuthForm(f => ({ ...f, password: e.target.value }))}
                  onKeyDown={handleKeyDown}
                />
                {authError && <div className="auth-error">{authError}</div>}
                <button
                  className="btn-auth-submit"
                  onClick={handleAuth}
                  disabled={authLoading}
                >
                  {authLoading ? '處理中...' : authMode === 'login' ? '登入' : '註冊'}
                </button>
                <div className="auth-switch">
                  {authMode === 'login' ? (
                    <span>沒有帳號？<button onClick={() => { setAuthMode('register'); setAuthError('') }}>註冊</button></span>
                  ) : (
                    <span>已有帳號？<button onClick={() => { setAuthMode('login'); setAuthError('') }}>登入</button></span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AetheriaProvider>
  )
}

export default App
