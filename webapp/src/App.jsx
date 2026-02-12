import { useState, useEffect, useCallback, useRef } from 'react'
import { AetheriaProvider } from './contexts/AetheriaContext'
import ChatContainer from './ChatContainer'
import SessionSidebar from './SessionSidebar'
import VoiceChat from './VoiceChat'
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
  const [userProfile, setUserProfile] = useState(null) // 新增：用戶資料
  const [birthInfo, setBirthInfo] = useState(null)
  const [memberPreferences, setMemberPreferences] = useState({})
  const [memberConsents, setMemberConsents] = useState({})
  const [authReady, setAuthReady] = useState(false)
  const [authError, setAuthError] = useState('')

  // ========== Auth Modal ==========
  const [showAuth, setShowAuth] = useState(false)
  const [authMode, setAuthMode] = useState('login')
  const [authForm, setAuthForm] = useState({ username: '', password: '', display_name: '' })
  const [authLoading, setAuthLoading] = useState(false)
  const authModalRef = useRef(null)
  const authFirstFieldRef = useRef(null)

  // ========== Sidebar State ==========
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('aetheria_sidebar_collapsed')
    return saved === 'true'
  })

  // ========== Mobile UI ==========
  const [isMobile, setIsMobile] = useState(() => window.innerWidth <= 768)
  const [mobileTab, setMobileTab] = useState('chat') // chat | me

  // ========== Mobile "Me" settings sheet ==========
  const [showMeSheet, setShowMeSheet] = useState(false)
  const [meSection, setMeSection] = useState('birth') // birth | voice | privacy
  const [meSaving, setMeSaving] = useState(false)
  const [meError, setMeError] = useState('')

  const [birthForm, setBirthForm] = useState({
    name: '',
    gender: '',
    birth_date: '',
    birth_time: '',
    birth_location: ''
  })

  const [voicePrefForm, setVoicePrefForm] = useState({
    preferred_voice: '',
    voice_mode: 'auto' // auto | voice | text
  })

  const [consentForm, setConsentForm] = useState({
    terms_accepted: true,
    data_usage_accepted: true
  })

  const [availableVoices, setAvailableVoices] = useState([])

  // ========== Voice Chat State ==========
  const [showVoiceChat, setShowVoiceChat] = useState(false)

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 768)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  useEffect(() => {
    if (!isMobile) setMobileTab('chat')
  }, [isMobile])

  // Prevent background scroll when any modal is open
  useEffect(() => {
    const modalOpen = showAuth || showVoiceChat || showMeSheet
    const rootEl = document.documentElement
    const bodyEl = document.body

    if (modalOpen) {
      rootEl.classList.add('aetheria-modal-open')
      bodyEl.classList.add('aetheria-modal-open')
    } else {
      rootEl.classList.remove('aetheria-modal-open')
      bodyEl.classList.remove('aetheria-modal-open')
    }

    return () => {
      rootEl.classList.remove('aetheria-modal-open')
      bodyEl.classList.remove('aetheria-modal-open')
    }
  }, [showAuth, showVoiceChat, showMeSheet])

  useEffect(() => {
    localStorage.setItem('aetheria_sidebar_collapsed', sidebarCollapsed)
  }, [sidebarCollapsed])

  const loadProfile = useCallback(async (overrideToken) => {
    const authToken = overrideToken || token
    if (!authToken) return null

    const resp = await fetch(`${apiBase}/api/profile`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    if (!resp.ok) throw new Error('profile fetch failed')
    const data = await resp.json()

    setUserProfile(data.profile || null)
    setBirthInfo(data.birth_info || null)
    setMemberPreferences(data.preferences || {})
    setMemberConsents(data.consents || {})

    const bi = data.birth_info || {}
    setBirthForm(prev => ({
      ...prev,
      name: bi.name || prev.name || data.profile?.display_name || data.profile?.username || '',
      gender: bi.gender || prev.gender || '',
      birth_date: bi.birth_date || prev.birth_date || '',
      birth_time: bi.birth_time || prev.birth_time || '',
      birth_location: bi.birth_location || prev.birth_location || ''
    }))

    const prefs = data.preferences || {}
    setVoicePrefForm(prev => ({
      ...prev,
      preferred_voice: prefs.preferred_voice || prev.preferred_voice || '',
      voice_mode: prefs.voice_mode || prev.voice_mode || 'auto'
    }))

    const cons = data.consents || {}
    setConsentForm(prev => ({
      ...prev,
      terms_accepted: typeof cons.terms_accepted === 'boolean' ? cons.terms_accepted : prev.terms_accepted,
      data_usage_accepted: typeof cons.data_usage_accepted === 'boolean' ? cons.data_usage_accepted : prev.data_usage_accepted
    }))

    return data
  }, [apiBase, token])

  // ========== Guest trial (明確告知使用者) ==========
  const startGuestTrial = useCallback(async () => {
    if (!window.confirm(
      '⚠️ 訪客試用模式\n\n' +
      '• 對話記錄僅保存 7 天\n' +
      '• 無法儲存命盤資料\n' +
      '• 建議註冊以獲得完整功能\n\n' +
      '確定要以訪客身份試用嗎？'
    )) {
      return null
    }

    try {
      const guestId = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
      const resp = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: guestId,
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
      
      // 載入訪客資料
      loadProfile(data.token).catch(() => {})
      
      setAuthReady(true)
      return data.token
    } catch (err) {
      console.error('Guest trial error:', err)
      alert('無法連接到伺服器，請稍後再試')
      return null
    }
  }, [apiBase])

  // ========== Validate existing session ==========
  useEffect(() => {
    const init = async () => {
      // 檢查版本，自動清除舊資料（從 email 改為 username）
      const appVersion = localStorage.getItem('aetheria_app_version')
      if (appVersion !== '2.0.0') {
        // 自動清除所有舊資料
        localStorage.clear()
        localStorage.setItem('aetheria_app_version', '2.0.0')
        setToken('')
        setUserId('')
        setUserProfile(null)
        setBirthInfo(null)
        setMemberPreferences({})
        setMemberConsents({})
        setAuthReady(false)
        console.log('✓ 已自動清除舊版本資料，現在使用 username 登入')
        return
      }

      if (token) {
        // Validate existing token
        try {
          const resp = await fetch(`${apiBase}/api/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (resp.ok) {
            const data = await resp.json()
            // 自動清除舊的訪客 token（username 以 guest_ 開頭的）
            if (data.profile?.username?.startsWith('guest_')) {
              localStorage.removeItem('aetheria_token')
              localStorage.removeItem('aetheria_user_id')
              setToken('')
              setUserId('')
              setUserProfile(null)
              setBirthInfo(null)
              setMemberPreferences({})
              setMemberConsents({})
              setAuthReady(false)
              return
            }
            setUserId(data.profile?.user_id || userId)
            setUserProfile(data.profile)
            setBirthInfo(data.birth_info || null)
            setMemberPreferences(data.preferences || {})
            setMemberConsents(data.consents || {})
            setAuthReady(true)
            return
          }
          // Token expired or invalid — clear
          localStorage.removeItem('aetheria_token')
          localStorage.removeItem('aetheria_user_id')
          setToken('')
          setUserId('')
          setUserProfile(null)
          setBirthInfo(null)
          setMemberPreferences({})
          setMemberConsents({})
        } catch {
          // Server error or network issue — clear invalid token
          localStorage.removeItem('aetheria_token')
          localStorage.removeItem('aetheria_user_id')
          setToken('')
          setUserId('')
          setUserProfile(null)
          setBirthInfo(null)
          setMemberPreferences({})
          setMemberConsents({})
        }
      }
      // No valid token — 顯示登入頁面
      setAuthReady(false)
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
        ? { username: authForm.username.trim(), password: authForm.password.trim() }
        : {
            username: authForm.username.trim(),
            password: authForm.password.trim(),
            display_name: authForm.display_name.trim() || authForm.username.trim(),
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
      setAuthForm({ username: '', password: '', display_name: '' })
      
      // 重新載入用戶資料
      loadProfile(data.token).then(() => {
        setAuthReady(true) // 設定為已認證
      }).catch(() => {
        setAuthReady(true) // 即使取得 profile 失敗也進入主介面
      })
    } catch {
      setAuthError('無法連接到伺服器')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('aetheria_token')
    localStorage.removeItem('aetheria_user_id')
    setUserProfile(null)
    setBirthInfo(null)
    setMemberPreferences({})
    setMemberConsents({})
    setToken('')
    setUserId('')
    setAuthReady(false)
    setShowMeSheet(false)
    // 登出後顯示登入頁面
  }

  const openMeSection = useCallback(async (section) => {
    setMeError('')
    setMeSection(section)
    setShowMeSheet(true)

    if (section === 'voice' && Array.isArray(availableVoices) && availableVoices.length === 0) {
      try {
        const resp = await fetch(`${apiBase}/api/voice/voices`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (resp.ok) {
          const data = await resp.json()
          const voices = data?.voices || data?.data || []
          if (Array.isArray(voices)) setAvailableVoices(voices)
        }
      } catch {
        // ignore
      }
    }
  }, [apiBase, token, availableVoices])

  const saveBirthInfo = useCallback(async () => {
    setMeSaving(true)
    setMeError('')
    try {
      if (!birthForm.birth_date || !birthForm.birth_time || !birthForm.birth_location) {
        setMeError('生辰資料不完整（需要出生日期、時間、地點）')
        return
      }

      const resp = await fetch(`${apiBase}/api/profile/birth-info`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: birthForm.name || undefined,
          gender: birthForm.gender || undefined,
          birth_date: birthForm.birth_date,
          birth_time: birthForm.birth_time,
          birth_location: birthForm.birth_location
        })
      })

      const data = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        setMeError(data?.error || data?.message || '儲存失敗')
        return
      }

      await loadProfile()
      setShowMeSheet(false)
    } catch {
      setMeError('儲存失敗（網路或伺服器錯誤）')
    } finally {
      setMeSaving(false)
    }
  }, [apiBase, token, birthForm, loadProfile])

  const saveVoicePrefs = useCallback(async () => {
    setMeSaving(true)
    setMeError('')
    try {
      const resp = await fetch(`${apiBase}/api/profile`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          preferences: {
            ...(memberPreferences || {}),
            preferred_voice: voicePrefForm.preferred_voice || '',
            voice_mode: voicePrefForm.voice_mode || 'auto'
          }
        })
      })
      const data = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        setMeError(data?.error || data?.message || '儲存失敗')
        return
      }

      await loadProfile()
      setShowMeSheet(false)
    } catch {
      setMeError('儲存失敗（網路或伺服器錯誤）')
    } finally {
      setMeSaving(false)
    }
  }, [apiBase, token, memberPreferences, voicePrefForm, loadProfile])

  const saveConsents = useCallback(async () => {
    setMeSaving(true)
    setMeError('')
    try {
      const resp = await fetch(`${apiBase}/api/consent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...(memberConsents || {}),
          terms_accepted: !!consentForm.terms_accepted,
          data_usage_accepted: !!consentForm.data_usage_accepted
        })
      })
      const data = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        setMeError(data?.error || data?.message || '儲存失敗')
        return
      }

      await loadProfile()
      setShowMeSheet(false)
    } catch {
      setMeError('儲存失敗（網路或伺服器錯誤）')
    } finally {
      setMeSaving(false)
    }
  }, [apiBase, token, memberConsents, consentForm, loadProfile])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAuth()
    }
  }

  const handleAuthModalKeyDown = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      setShowAuth(false)
      return
    }

    if (e.key !== 'Tab') return
    const container = authModalRef.current
    if (!container) return

    const focusable = container.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    if (!focusable.length) return

    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement

    if (e.shiftKey) {
      if (active === first || active === container) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (active === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  useEffect(() => {
    if (!showAuth) return

    const focusTimer = window.setTimeout(() => {
      authFirstFieldRef.current?.focus()
    }, 0)

    const onKeyDown = (e) => {
      if (e.key === 'Escape') setShowAuth(false)
    }
    window.addEventListener('keydown', onKeyDown)

    return () => {
      window.clearTimeout(focusTimer)
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [showAuth, authMode])

  // ========== 未登入：顯示登入頁面 ==========
  if (!authReady) {
    return (
      <div className="auth-page" role="main" aria-label="登入 / 註冊">
        <div className="auth-frame">
          <header className="auth-topbar" role="banner">
            <div className="auth-topbar-inner">
              <div className="auth-brand" aria-label="Aetheria">
                <div className="auth-brand-mark" aria-hidden="true">🔮</div>
                <div className="auth-brand-text">
                  <strong>Aetheria</strong>
                  <span>登入 · 海軍藍主題</span>
                </div>
              </div>
            </div>
          </header>

          <section className="auth-container" aria-label="登入卡片">
            <div className="auth-header">
              <h1>{authMode === 'login' ? '歡迎回來' : '建立帳號'}</h1>
              <p className="auth-tagline">
                保持簡潔：登入後直接進入「命理師對話」，語音是主要入口。
              </p>
            </div>

            <div className="auth-form">
              <div className="auth-tabs" role="tablist" aria-label="登入或註冊">
                <button
                  className={authMode === 'login' ? 'auth-tab active' : 'auth-tab'}
                  onClick={() => { setAuthMode('login'); setAuthError('') }}
                  type="button"
                  role="tab"
                  aria-selected={authMode === 'login'}
                >
                  登入
                </button>
                <button
                  className={authMode === 'register' ? 'auth-tab active' : 'auth-tab'}
                  onClick={() => { setAuthMode('register'); setAuthError('') }}
                  type="button"
                  role="tab"
                  aria-selected={authMode === 'register'}
                >
                  註冊
                </button>
              </div>

              <div className="auth-form-fields">
                {authMode === 'register' && (
                  <input
                    type="text"
                    placeholder="顯示名稱（選填）"
                    value={authForm.display_name}
                    onChange={(e) => setAuthForm(prev => ({ ...prev, display_name: e.target.value }))}
                    onKeyDown={handleKeyDown}
                    autoComplete="nickname"
                  />
                )}

                <input
                  type="text"
                  placeholder="Email 或使用者名稱"
                  value={authForm.username}
                  onChange={(e) => setAuthForm(prev => ({ ...prev, username: e.target.value }))}
                  onKeyDown={handleKeyDown}
                  autoComplete="username"
                />

                <input
                  type="password"
                  placeholder={authMode === 'register' ? '設定密碼（至少 8 碼）' : '密碼'}
                  value={authForm.password}
                  onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
                  onKeyDown={handleKeyDown}
                  autoComplete={authMode === 'register' ? 'new-password' : 'current-password'}
                />

                {authError && <div className="auth-error">{authError}</div>}

                <button
                  className="btn-auth-submit"
                  onClick={handleAuth}
                  disabled={authLoading}
                  type="button"
                >
                  {authLoading ? '處理中...' : authMode === 'login' ? '登入' : '建立帳號'}
                </button>

                <button
                  className="btn-guest-trial"
                  onClick={startGuestTrial}
                  disabled={authLoading}
                  type="button"
                >
                  訪客試用（不保存）
                </button>
              </div>

              <div className="auth-footer">
                <p>繼續即表示同意服務條款與隱私政策</p>
              </div>
            </div>
          </section>

          <footer className="auth-bottom">
            <span>登入後你會直接進入對話（Voice-first）。</span>
          </footer>
        </div>
      </div>
    )
  }

  const isSignedIn = !!token && authReady
  const displayName = userProfile?.display_name || userProfile?.username || '用戶'
  const isGuestUser = userProfile?.username?.startsWith('guest_')

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
            {isMobile ? (
              <>
                <button
                  className="btn-topbar btn-icon"
                  type="button"
                  aria-label="對話列表"
                  onClick={() => setSidebarCollapsed(false)}
                >
                  🗂️
                </button>
                <button
                  className="btn-topbar btn-icon"
                  type="button"
                  aria-label="我的"
                  onClick={() => setMobileTab('me')}
                >
                  👤
                </button>
              </>
            ) : isSignedIn ? (
              <div className="user-info">
                <span className="user-badge">👤</span>
                <span className="user-name">{displayName}{isGuestUser ? '（訪客）' : ''}</span>
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
        <main className={isMobile ? 'app-main mobile' : 'app-main'}>
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
            {isMobile && mobileTab === 'me' ? (
              <div className="mobile-me" role="main" aria-label="我的">
                <div className="mobile-me-card">
                  <div className="mobile-me-title">👤 {displayName}{isGuestUser ? '（訪客）' : ''}</div>
                  <div className="mobile-me-sub">這裡只保留必要項：生辰資料、語音偏好、隱私同意。</div>
                  <div className="mobile-me-actions">
                    <button className="mobile-me-btn" type="button" onClick={() => openMeSection('birth')}>生辰資料</button>
                    <button className="mobile-me-btn" type="button" onClick={() => openMeSection('voice')}>語音偏好</button>
                    <button className="mobile-me-btn" type="button" onClick={() => openMeSection('privacy')}>隱私同意</button>
                    <button className="mobile-me-btn primary" type="button" onClick={handleLogout}>登出</button>
                  </div>

                  {birthInfo && (birthInfo.birth_date || birthInfo.birth_time || birthInfo.birth_location) && (
                    <div className="mobile-me-hint" aria-label="目前生辰資料摘要">
                      <div className="mobile-me-hint-row">📅 {birthInfo.birth_date || '—'} {birthInfo.birth_time || ''}</div>
                      <div className="mobile-me-hint-row">📍 {birthInfo.birth_location || '—'}</div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <ChatContainer
                apiBase={apiBase}
                token={token}
                userId={userId}
                embedded={false}
                sidebarCollapsed={sidebarCollapsed}
                onToggleSidebar={() => setSidebarCollapsed(prev => !prev)}
                onOpenVoiceChat={() => {
                  setShowVoiceChat(true)
                }}
              />
            )}
          </div>
        </main>

        {/* Mobile bottom nav (voice-first) */}
        {isMobile && (
          <nav className="mobile-bottom-nav" aria-label="底部導覽">
            <button
              type="button"
              className={mobileTab !== 'me' && !showVoiceChat ? 'mbn-item active' : 'mbn-item'}
              aria-current={mobileTab !== 'me' && !showVoiceChat ? 'page' : undefined}
              onClick={() => {
                setMobileTab('chat')
                setShowVoiceChat(false)
              }}
            >
              <span className="mbn-ico" aria-hidden="true">💬</span>
              <span className="mbn-txt">對話</span>
            </button>
            <button
              type="button"
              className={showVoiceChat ? 'mbn-item voice active' : 'mbn-item voice'}
              aria-current={showVoiceChat ? 'page' : undefined}
              onClick={() => {
                setMobileTab('chat')
                setShowVoiceChat(true)
              }}
            >
              <span className="mbn-ico" aria-hidden="true">🎙️</span>
              <span className="mbn-txt">語音</span>
            </button>
            <button
              type="button"
              className={mobileTab === 'me' ? 'mbn-item active' : 'mbn-item'}
              aria-current={mobileTab === 'me' ? 'page' : undefined}
              onClick={() => {
                setShowVoiceChat(false)
                setMobileTab('me')
              }}
            >
              <span className="mbn-ico" aria-hidden="true">👤</span>
              <span className="mbn-txt">我的</span>
            </button>
          </nav>
        )}

        {/* Auth Modal */}
        {showAuth && (
          <div className="modal-overlay" onClick={() => setShowAuth(false)}>
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
              onKeyDown={handleAuthModalKeyDown}
              role="dialog"
              aria-modal="true"
              aria-labelledby="auth-modal-title"
              ref={authModalRef}
            >
              <div className="modal-header">
                <h3 id="auth-modal-title">{authMode === 'login' ? '登入' : '註冊'}</h3>
                <button className="modal-close" onClick={() => setShowAuth(false)} aria-label="關閉登入視窗">✕</button>
              </div>
              <div className="modal-body">
                {authMode === 'register' && (
                  <input
                    type="text"
                    placeholder="顯示名稱（選填）"
                    value={authForm.display_name}
                    onChange={e => setAuthForm(f => ({ ...f, display_name: e.target.value }))}
                    onKeyDown={handleKeyDown}
                    ref={authFirstFieldRef}
                  />
                )}
                <input
                  type="text"
                  placeholder="使用者名稱"
                  value={authForm.username}
                  onChange={e => setAuthForm(f => ({ ...f, username: e.target.value }))}
                  onKeyDown={handleKeyDown}
                  ref={authMode === 'login' ? authFirstFieldRef : undefined}
                  autoComplete="username"
                />
                <input
                  type="password"
                  placeholder="密碼"
                  value={authForm.password}
                  onChange={e => setAuthForm(f => ({ ...f, password: e.target.value }))}
                  onKeyDown={handleKeyDown}
                  autoComplete="current-password"
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

        {/* Voice Chat Modal */}
        {showVoiceChat && (
          <VoiceChat
            apiBase={apiBase}
            token={token}
            userId={userId}
            onClose={() => setShowVoiceChat(false)}
            embedded={false}
            variant={isMobile ? 'sheet' : 'modal'}
          />
        )}

        {/* Mobile Me Sheet */}
        {isMobile && showMeSheet && (
          <div className="me-sheet-overlay" onClick={() => setShowMeSheet(false)} role="presentation">
            <div
              className="me-sheet"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-modal="true"
              aria-label={meSection === 'birth' ? '生辰資料' : meSection === 'voice' ? '語音偏好' : '隱私同意'}
            >
              <div className="me-sheet-header">
                <div className="me-sheet-title">
                  {meSection === 'birth' ? '生辰資料' : meSection === 'voice' ? '語音偏好' : '隱私同意'}
                </div>
                <button className="me-sheet-close" type="button" onClick={() => setShowMeSheet(false)} aria-label="關閉">✕</button>
              </div>

              <div className="me-sheet-body">
                {meError && <div className="me-sheet-error">{meError}</div>}

                {meSection === 'birth' && (
                  <>
                    <label className="me-field">
                      <span>姓名（選填）</span>
                      <input
                        type="text"
                        value={birthForm.name}
                        onChange={(e) => setBirthForm(f => ({ ...f, name: e.target.value }))}
                        placeholder="例：王小明"
                        autoComplete="name"
                      />
                    </label>

                    <label className="me-field">
                      <span>性別（選填）</span>
                      <select value={birthForm.gender} onChange={(e) => setBirthForm(f => ({ ...f, gender: e.target.value }))}>
                        <option value="">不指定</option>
                        <option value="男">男</option>
                        <option value="女">女</option>
                      </select>
                    </label>

                    <label className="me-field">
                      <span>出生日期（必填）</span>
                      <input type="date" value={birthForm.birth_date} onChange={(e) => setBirthForm(f => ({ ...f, birth_date: e.target.value }))} />
                    </label>

                    <label className="me-field">
                      <span>出生時間（必填）</span>
                      <input type="time" value={birthForm.birth_time} onChange={(e) => setBirthForm(f => ({ ...f, birth_time: e.target.value }))} />
                    </label>

                    <label className="me-field">
                      <span>出生地點（必填）</span>
                      <input
                        type="text"
                        value={birthForm.birth_location}
                        onChange={(e) => setBirthForm(f => ({ ...f, birth_location: e.target.value }))}
                        placeholder="例：台灣台北市"
                        autoComplete="address-level2"
                      />
                    </label>

                    <button className="me-sheet-primary" type="button" onClick={saveBirthInfo} disabled={meSaving}>
                      {meSaving ? '儲存中...' : '儲存生辰資料'}
                    </button>
                  </>
                )}

                {meSection === 'voice' && (
                  <>
                    <label className="me-field">
                      <span>語音模式</span>
                      <select value={voicePrefForm.voice_mode} onChange={(e) => setVoicePrefForm(f => ({ ...f, voice_mode: e.target.value }))}>
                        <option value="auto">自動（建議）</option>
                        <option value="voice">偏好語音</option>
                        <option value="text">偏好文字</option>
                      </select>
                    </label>

                    <label className="me-field">
                      <span>偏好聲線（選填）</span>
                      {Array.isArray(availableVoices) && availableVoices.length > 0 ? (
                        <select value={voicePrefForm.preferred_voice} onChange={(e) => setVoicePrefForm(f => ({ ...f, preferred_voice: e.target.value }))}>
                          <option value="">不指定</option>
                          {availableVoices.map((v) => {
                            const id = typeof v === 'string' ? v : (v.id || v.voice || v.name)
                            const label = typeof v === 'string' ? v : (v.name || v.voice || v.id)
                            if (!id) return null
                            return <option key={id} value={id}>{label}</option>
                          })}
                        </select>
                      ) : (
                        <input
                          type="text"
                          value={voicePrefForm.preferred_voice}
                          onChange={(e) => setVoicePrefForm(f => ({ ...f, preferred_voice: e.target.value }))}
                          placeholder="例：alloy"
                        />
                      )}
                    </label>

                    <button className="me-sheet-primary" type="button" onClick={saveVoicePrefs} disabled={meSaving}>
                      {meSaving ? '儲存中...' : '儲存語音偏好'}
                    </button>
                  </>
                )}

                {meSection === 'privacy' && (
                  <>
                    <label className="me-check">
                      <input
                        type="checkbox"
                        checked={!!consentForm.terms_accepted}
                        onChange={(e) => setConsentForm(f => ({ ...f, terms_accepted: e.target.checked }))}
                      />
                      <span>我同意服務條款</span>
                    </label>

                    <label className="me-check">
                      <input
                        type="checkbox"
                        checked={!!consentForm.data_usage_accepted}
                        onChange={(e) => setConsentForm(f => ({ ...f, data_usage_accepted: e.target.checked }))}
                      />
                      <span>我同意資料用於提供服務（例如儲存命盤資料）</span>
                    </label>

                    <button className="me-sheet-primary" type="button" onClick={saveConsents} disabled={meSaving}>
                      {meSaving ? '儲存中...' : '儲存隱私同意'}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </AetheriaProvider>
  )
}

export default App
