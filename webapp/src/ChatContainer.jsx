import { useState, useEffect, useRef, useCallback } from 'react'
import MessageRenderer from './MessageRenderer'
import { useAetheriaContext } from './contexts/AetheriaContext'
import './ChatContainer.css'

/**
 * ChatContainer — Chat-First 主介面 (Agent 2.0)
 * 
 * 設計原則：
 * 1. 對話即一切 — 沒有頁面切換、沒有選單、沒有表單
 * 2. AI 主動引導 — 首次進入即有歡迎語，引導使用者開始對話
 * 3. 零摩擦體驗 — 無須先「鎖定命盤」即可聊天
 * 4. 優雅錯誤處理 — 所有錯誤在對話流中呈現，不使用 alert/confirm
 */
function ChatContainer({ apiBase, token, userId, embedded = false }) {
  const {
    messages,
    setMessages,
    currentSession,
    setCurrentSession
  } = useAetheriaContext()

  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [toolExecuting, setToolExecuting] = useState(null)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [showClearConfirm, setShowClearConfirm] = useState(false)

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const storagePrefix = userId || token || 'guest'
  const storageSessionKey = `aetheria_session_${storagePrefix}`
  const storageMessagesKey = `aetheria_messages_${storagePrefix}`

  const sessionId = currentSession

  // ========== 自動滾動 ==========
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // ========== 清空狀態（使用者切換） ==========
  useEffect(() => {
    setMessages([])
    setCurrentSession(null)
    setHistoryLoaded(false)
  }, [storagePrefix, setMessages, setCurrentSession])

  // ========== 載入歷史 ==========
  useEffect(() => {
    if (!token) { setHistoryLoaded(true); return }

    const loadMessages = async (sessId) => {
      try {
        const resp = await fetch(`${apiBase}/api/chat/messages?session_id=${sessId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (resp.status === 401) { localStorage.removeItem('aetheria_token'); return }
        if (!resp.ok) return
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
        }
      } catch (err) {
        console.warn('Load messages failed:', err)
        // 嘗試從 localStorage 恢復
        const cached = localStorage.getItem(storageMessagesKey)
        if (cached) { try { setMessages(JSON.parse(cached)) } catch {} }
      }
    }

    const init = async () => {
      // 嘗試恢復上一次 session
      const savedSession = localStorage.getItem(storageSessionKey)
      if (savedSession) {
        setCurrentSession(savedSession)
        await loadMessages(savedSession)
        setHistoryLoaded(true)
        return
      }

      // 查詢伺服器是否有歷史 session
      try {
        const resp = await fetch(`${apiBase}/api/chat/sessions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (resp.ok) {
          const data = await resp.json()
          const latest = data?.sessions?.[0]
          if (latest?.session_id) {
            setCurrentSession(latest.session_id)
            localStorage.setItem(storageSessionKey, latest.session_id)
            await loadMessages(latest.session_id)
          }
        }
      } catch (err) {
        console.warn('Init session failed:', err)
      }
      setHistoryLoaded(true)
    }

    init()
  }, [apiBase, token, storagePrefix, storageSessionKey, storageMessagesKey, setCurrentSession, setMessages])

  // ========== 持久化 ==========
  useEffect(() => {
    if (currentSession) localStorage.setItem(storageSessionKey, currentSession)
  }, [currentSession, storageSessionKey])

  useEffect(() => {
    if (messages?.length) {
      localStorage.setItem(storageMessagesKey, JSON.stringify(messages.slice(-200)))
    }
  }, [messages, storageMessagesKey])

  // ========== 在對話中插入系統訊息（取代 alert） ==========
  const pushSystemMessage = useCallback((content) => {
    setMessages(prev => [...prev, {
      id: `sys-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'system_event',
      role: 'system',
      content,
      timestamp: new Date().toISOString()
    }])
  }, [setMessages])

  // ========== 發送訊息 ==========
  const sendMessage = async (overrideText) => {
    const text = (overrideText || inputText).trim()
    if (!text) return

    if (!token) {
      pushSystemMessage('⚠️ 連線中斷，請重新整理頁面')
      return
    }

    const userMessage = {
      id: `user-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'text',
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    if (!overrideText) setInputText('')
    setLoading(true)
    inputRef.current?.focus()

    const assistantId = `assistant-${Date.now()}-${Math.random().toString(36).slice(2)}`
    setMessages(prev => [...prev, {
      id: assistantId,
      type: 'text',
      role: 'assistant',
      content: '',
      streaming: true,
      timestamp: new Date().toISOString()
    }])

    try {
      const response = await fetch(`${apiBase}/api/chat/consult-stream`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: text, session_id: sessionId })
      })

      if (response.status === 401) {
        localStorage.removeItem('aetheria_token')
        setMessages(prev => prev.filter(m => m.id !== assistantId))
        pushSystemMessage('⚠️ 登入已過期，請重新整理頁面')
        return
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        const errorMsg = errorData?.message || errorData?.error || `伺服器錯誤 (${response.status})`
        setMessages(prev => prev.filter(m => m.id !== assistantId))
        pushSystemMessage(`⚠️ ${errorMsg}`)
        return
      }

      // ===== SSE 串流處理 =====
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let accumulatedText = ''
      let currentEvent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim() || line.startsWith(':')) continue

          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim()
            continue
          }

          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim()
            try {
              const data = JSON.parse(dataStr)

              if (currentEvent === 'text' && data.chunk) {
                accumulatedText += data.chunk
                setMessages(prev => {
                  const updated = [...prev]
                  const idx = updated.findIndex(m => m?.id === assistantId)
                  if (idx >= 0) updated[idx] = { ...updated[idx], content: accumulatedText }
                  return updated
                })
              } else if (currentEvent === 'widget') {
                setMessages(prev => [...prev, {
                  id: `widget-${Date.now()}-${Math.random().toString(36).slice(2)}`,
                  type: 'widget',
                  role: 'assistant',
                  widget_type: data.type,
                  widget_data: data.data,
                  compact: data.compact || false,
                  timestamp: new Date().toISOString()
                }])
              } else if (currentEvent === 'tool') {
                if (data.status === 'executing') {
                  setToolExecuting({ name: data.name, args: data.args })
                } else {
                  setToolExecuting(null)
                }
              } else if (currentEvent === 'progress') {
                const progressMsg = {
                  id: `progress-${Date.now()}-${Math.random().toString(36).slice(2)}`,
                  type: 'widget',
                  role: 'assistant',
                  widget_type: 'progress',
                  widget_data: {
                    task_name: data.task_name || '運算中...',
                    progress: data.progress || 0,
                    status: data.status || 'running',
                    message: data.message || ''
                  },
                  timestamp: new Date().toISOString()
                }
                setMessages(prev => {
                  const existIdx = prev.findIndex(
                    m => m.type === 'widget' && m.widget_type === 'progress'
                      && m.widget_data?.task_name === data.task_name
                  )
                  if (existIdx >= 0) {
                    const updated = [...prev]
                    updated[existIdx] = progressMsg
                    return updated
                  }
                  return [...prev, progressMsg]
                })
              } else if (currentEvent === 'done' || currentEvent === 'session') {
                if (data.session_id && !sessionId) {
                  setCurrentSession(data.session_id)
                }
              }
            } catch (e) {
              console.warn('SSE parse error:', e, dataStr)
            }
          }
        }
      }

      // 串流完成
      setMessages(prev => {
        const updated = [...prev]
        const idx = updated.findIndex(m => m?.id === assistantId)
        if (idx >= 0) updated[idx] = { ...updated[idx], streaming: false }
        return updated
      })
    } catch (error) {
      console.error('Send failed:', error)
      setMessages(prev => prev.filter(m => m.id !== assistantId))
      pushSystemMessage('⚠️ 網路連線失敗，請檢查網路後重試')
    } finally {
      setLoading(false)
      setToolExecuting(null)
    }
  }

  // ========== 鍵盤處理 ==========
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // ========== 開始新對話 ==========
  const startNewSession = () => {
    setMessages([])
    setCurrentSession(null)
    localStorage.removeItem(storageSessionKey)
    localStorage.removeItem(storageMessagesKey)
    setShowClearConfirm(false)
  }

  // ========== 快速提問 ==========
  const handleQuickPrompt = (text) => {
    setInputText(text)
    // 延遲一幀讓 state 更新後再發送
    setTimeout(() => sendMessage(text), 0)
  }

  // ========== 歡迎畫面（無歷史訊息時顯示） ==========
  const renderWelcome = () => (
    <div className="welcome-screen">
      <div className="welcome-avatar-ring">
        <div className="welcome-avatar">🔮</div>
      </div>
      <h2 className="welcome-title">你好，我是 Aetheria</h2>
      <p className="welcome-subtitle">
        你的 AI 命理分析顧問
      </p>
      <p className="welcome-desc">
        整合紫微斗數、八字、西洋占星、數字命理等多元系統，<br />
        透過對話為你提供深度的命理洞察與人生建議。
      </p>
      <div className="welcome-prompts">
        <button onClick={() => handleQuickPrompt('你好！我想了解一下我的命理，該從哪裡開始？')}>
          <span className="prompt-icon">👋</span>
          <span className="prompt-text">初次見面，想了解命理</span>
        </button>
        <button onClick={() => handleQuickPrompt('我的出生日期是…（請幫我分析）')}>
          <span className="prompt-icon">📅</span>
          <span className="prompt-text">提供生辰，開始分析</span>
        </button>
        <button onClick={() => handleQuickPrompt('最近生活上遇到一些困惑，想聽聽建議')}>
          <span className="prompt-icon">💭</span>
          <span className="prompt-text">聊聊最近的困惑</span>
        </button>
        <button onClick={() => handleQuickPrompt('幫我看看今年的整體運勢走向')}>
          <span className="prompt-icon">✨</span>
          <span className="prompt-text">詢問今年運勢</span>
        </button>
      </div>
    </div>
  )

  return (
    <div className={`chat-container ${embedded ? 'embedded' : 'standalone'}`}>
      {/* 頂部操作列 */}
      <div className="chat-toolbar">
        <button
          className="toolbar-btn"
          onClick={() => messages.length > 0 ? setShowClearConfirm(true) : null}
          disabled={messages.length === 0}
          title="開始新對話"
        >
          <span>＋</span> 新對話
        </button>
      </div>

      {/* 對話區域 */}
      <div className="messages-container">
        {messages.length === 0 && historyLoaded && renderWelcome()}

        {messages.map((msg) => (
          <MessageRenderer
            key={msg.id}
            message={msg}
            apiBase={apiBase}
            token={token}
            sessionId={sessionId}
          />
        ))}

        {toolExecuting && (
          <div className="tool-executing">
            <div className="spinner" />
            <span>正在分析 {toolExecuting.name}...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 輸入區 */}
      <div className="input-container">
        {loading && (
          <div className="input-status">
            <div className="typing-indicator">
              <span /><span /><span />
            </div>
            <span className="typing-text">Aetheria 正在思考...</span>
          </div>
        )}
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="輸入你的問題... (Shift+Enter 換行)"
            disabled={loading}
            rows={1}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !inputText.trim()}
            className="btn-send"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </div>

      {/* 清除確認（取代 browser confirm） */}
      {showClearConfirm && (
        <div className="confirm-overlay" onClick={() => setShowClearConfirm(false)}>
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <p>確定要開始新對話嗎？<br /><small>目前的對話歷史仍會保存在伺服器。</small></p>
            <div className="confirm-actions">
              <button className="confirm-cancel" onClick={() => setShowClearConfirm(false)}>
                取消
              </button>
              <button className="confirm-ok" onClick={startNewSession}>
                開始新對話
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatContainer
