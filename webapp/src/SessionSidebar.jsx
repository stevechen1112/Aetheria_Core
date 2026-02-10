import { useState, useEffect, useCallback, useRef } from 'react'
import { useAetheriaContext } from './contexts/AetheriaContext'
import './SessionSidebar.css'

/**
 * SessionSidebar — 對話歷史側邊欄
 *
 * 功能：
 * 1. 顯示所有過去對話（標題 + 時間）
 * 2. 點擊切換載入
 * 3. 滑入顯示刪除按鈕
 * 4. 頂部「＋ 新對話」按鈕
 * 5. 可收合
 */
function SessionSidebar({
  apiBase,
  token,
  collapsed,
  onToggleCollapse,
  onSessionSelected
}) {
  const {
    currentSession,
    setCurrentSession,
    setMessages
  } = useAetheriaContext()

  const [sessions, setSessions] = useState([])
  const [loadingSessions, setLoadingSessions] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const refreshTimerRef = useRef(null)

  // ========== 載入對話列表 ==========
  const fetchSessions = useCallback(async () => {
    if (!token) return
    setLoadingSessions(true)
    try {
      const resp = await fetch(`${apiBase}/api/chat/sessions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        const data = await resp.json()
        setSessions(data.sessions || [])
      }
    } catch (err) {
      console.warn('Fetch sessions failed:', err)
    } finally {
      setLoadingSessions(false)
    }
  }, [apiBase, token])

  // 初始載入 + 當 currentSession 變化時刷新
  useEffect(() => {
    fetchSessions()
  }, [fetchSessions, currentSession])

  // 定時刷新（每 30 秒）
  useEffect(() => {
    refreshTimerRef.current = setInterval(fetchSessions, 30000)
    return () => clearInterval(refreshTimerRef.current)
  }, [fetchSessions])

  // ========== 切換對話 ==========
  const selectSession = useCallback(async (sessionId) => {
    if (sessionId === currentSession) return
    setCurrentSession(sessionId)
    onSessionSelected?.()
    // 載入該 session 的訊息
    try {
      const resp = await fetch(`${apiBase}/api/chat/messages?session_id=${sessionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        const data = await resp.json()
        if (data?.messages?.length) {
          setMessages(data.messages.map(m => ({
            id: m.id || `msg-${Date.now()}-${Math.random().toString(36).slice(2)}`,
            type: m.type || 'text',
            role: m.role,
            content: m.content,
            widget_type: m.widget_type,
            widget_data: m.widget_data,
            citations: m.citations || [],
            used_systems: m.used_systems || [],
            confidence: m.confidence || 0,
            timestamp: m.created_at || new Date().toISOString()
          })))
        } else {
          setMessages([])
        }
      }
    } catch (err) {
      console.warn('Load session messages failed:', err)
    }
  }, [apiBase, token, currentSession, setCurrentSession, setMessages])

  // ========== 新對話 ==========
  const startNewSession = useCallback(() => {
    setMessages([])
    setCurrentSession(null)
  }, [setMessages, setCurrentSession])

  // ========== 刪除對話 ==========
  const deleteSession = async (sessionId) => {
    setDeletingId(sessionId)
    try {
      const resp = await fetch(`${apiBase}/api/chat/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        setSessions(prev => prev.filter(s => s.session_id !== sessionId))
        // 若刪除的是目前顯示的對話，自動新開
        if (currentSession === sessionId) {
          startNewSession()
        }
      }
    } catch (err) {
      console.warn('Delete session failed:', err)
    } finally {
      setDeletingId(null)
      setConfirmDeleteId(null)
    }
  }

  // ========== 格式化時間 ==========
  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    try {
      const date = new Date(dateStr)
      const now = new Date()
      const diffMs = now - date
      const diffMin = Math.floor(diffMs / 60000)
      const diffHr = Math.floor(diffMs / 3600000)
      const diffDay = Math.floor(diffMs / 86400000)

      if (diffMin < 1) return '剛剛'
      if (diffMin < 60) return `${diffMin} 分鐘前`
      if (diffHr < 24) return `${diffHr} 小時前`
      if (diffDay < 7) return `${diffDay} 天前`

      return date.toLocaleDateString('zh-TW', {
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return ''
    }
  }

  // ========== 擷取顯示標題 ==========
  const displayTitle = (session) => {
    const title = session.title || ''
    if (title && title !== '新對話') {
      return title.length > 28 ? title.slice(0, 28) + '…' : title
    }
    // 無標題時用時間代替
    return '新對話'
  }

  // ========== 過濾對話列表 ==========
  const filteredSessions = searchQuery.trim()
    ? sessions.filter(s => {
        const title = (s.title || '').toLowerCase()
        const query = searchQuery.trim().toLowerCase()
        return title.includes(query)
      })
    : sessions

  // ========== 收合模式 ==========
  if (collapsed) {
    return (
      <div className="session-sidebar collapsed">
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleCollapse}
          title="展開對話列表"
        >
          ☰
        </button>
        <button
          className="sidebar-new-btn-icon"
          onClick={startNewSession}
          title="新對話"
        >
          ＋
        </button>
      </div>
    )
  }

  // ========== 展開模式 ==========
  return (
    <div className="session-sidebar expanded">
      {/* 側邊欄頭部 */}
      <div className="sidebar-header">
        <button
          className="sidebar-new-btn"
          onClick={startNewSession}
        >
          <span className="new-icon">＋</span>
          <span>新對話</span>
        </button>
        <button
          className="sidebar-toggle-btn"
          onClick={onToggleCollapse}
          title="收合側邊欄"
        >
          ✕
        </button>
      </div>

      {/* 搜尋列 */}
      {sessions.length > 3 && (
        <div className="sidebar-search">
          <input
            type="text"
            placeholder="🔍 搜尋對話..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="sidebar-search-input"
          />
          {searchQuery && (
            <button
              className="sidebar-search-clear"
              onClick={() => setSearchQuery('')}
            >✕</button>
          )}
        </div>
      )}

      {/* 對話列表 */}
      <div className="sidebar-list">
        {loadingSessions && sessions.length === 0 && (
          <div className="sidebar-loading">
            <div className="sidebar-spinner" />
            <span>載入中...</span>
          </div>
        )}

        {!loadingSessions && sessions.length === 0 && (
          <div className="sidebar-empty">
            <span className="empty-icon">💬</span>
            <span>還沒有對話紀錄</span>
            <span className="empty-hint">開始你的第一次命理諮詢吧</span>
          </div>
        )}

        {searchQuery && filteredSessions.length === 0 && sessions.length > 0 && (
          <div className="sidebar-empty">
            <span className="empty-icon">🔍</span>
            <span>找不到符合的對話</span>
          </div>
        )}

        {filteredSessions.map((session) => (
          <div
            key={session.session_id}
            className={`sidebar-item ${currentSession === session.session_id ? 'active' : ''} ${confirmDeleteId === session.session_id ? 'confirming' : ''}`}
            onClick={() => selectSession(session.session_id)}
          >
            <div className="item-content">
              <div className="item-title">{displayTitle(session)}</div>
              <div className="item-time">{formatTime(session.updated_at || session.created_at)}</div>
            </div>

            {/* 刪除按鈕（hover 時顯示） */}
            <div className="item-actions" onClick={(e) => e.stopPropagation()}>
              {confirmDeleteId === session.session_id ? (
                <div className="delete-confirm-inline">
                  <button
                    className="delete-yes"
                    onClick={() => deleteSession(session.session_id)}
                    disabled={deletingId === session.session_id}
                    aria-label="確認刪除"
                  >
                    {deletingId === session.session_id ? '…' : '✓'}
                  </button>
                  <button
                    className="delete-no"
                    onClick={() => setConfirmDeleteId(null)}
                    aria-label="取消刪除"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <button
                  className="delete-btn"
                  onClick={() => setConfirmDeleteId(session.session_id)}
                  title="刪除對話"
                  aria-label="刪除對話"
                >
                  🗑
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 底部資訊 */}
      <div className="sidebar-footer">
        <span>{searchQuery ? `${filteredSessions.length}/${sessions.length}` : sessions.length} 個對話</span>
      </div>
    </div>
  )
}

export default SessionSidebar
