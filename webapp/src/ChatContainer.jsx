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
function ChatContainer({ apiBase, token, userId, embedded = false, sidebarCollapsed = true, onToggleSidebar, onOpenVoiceChat }) {
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
  const [loadingTip, setLoadingTip] = useState('')

  // ========== 思考中小知識 ==========
  const fortuneTips = [
    '💡 紫微斗數以北極星為首，構建十二宮命盤',
    '💡 八字中的「日主」代表你自己的本質',
    '💡 上升星座代表你給人的第一印象',
    '💡 命理分析最準確的前提是精確的出生時間',
    '💡 紫微斗數中「空宮」不代表沒有主星影響',
    '💡 生命靈數源自古希臘畢達哥拉斯學派',
    '💡 塔羅牌大阿爾克那有 22 張，象徵人生旅程',
    '💡 八字中的「食神」代表才華與口福',
    '💡 每個人的星盤都是獨一無二的宇宙指紋',
    '💡 姓名學中筆畫數影響性格與運勢走向',
    '💡 紫微斗數的「化忌」未必是壞事，要看整體格局',
    '💡 太陽星座影響你的外在表現，月亮星座影響內心世界',
  ]

  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const tipIntervalRef = useRef(null)
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
        if (resp.status === 401) { localStorage.removeItem('aetheria_token'); return false }
        if (!resp.ok) return false
        const data = await resp.json()
        if (data?.expired) return false
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
          return true
        }
        return data?.messages?.length === 0
      } catch (err) {
        console.warn('Load messages failed:', err)
        // 嘗試從 localStorage 恢復
        const cached = localStorage.getItem(storageMessagesKey)
        if (cached) { try { setMessages(JSON.parse(cached)); return true } catch {} }
        return false
      }
    }

    const init = async () => {
      // 嘗試恢復上一次 session
      const savedSession = localStorage.getItem(storageSessionKey)
      if (savedSession) {
        setCurrentSession(savedSession)
        const loaded = await loadMessages(savedSession)
        if (!loaded) {
          // session 已過期或被刪除，清除 stale 資料
          localStorage.removeItem(storageSessionKey)
          localStorage.removeItem(storageMessagesKey)
          setCurrentSession(null)
          setMessages([])
        }
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

  // ========== Loading tip 輪換 ==========
  useEffect(() => {
    if (loading) {
      setLoadingTip(fortuneTips[Math.floor(Math.random() * fortuneTips.length)])
      tipIntervalRef.current = setInterval(() => {
        setLoadingTip(fortuneTips[Math.floor(Math.random() * fortuneTips.length)])
      }, 4000)
    } else {
      setLoadingTip('')
      if (tipIntervalRef.current) clearInterval(tipIntervalRef.current)
    }
    return () => {
      if (tipIntervalRef.current) clearInterval(tipIntervalRef.current)
    }
  }, [loading]) // eslint-disable-line react-hooks/exhaustive-deps

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

  // ========== 工具名稱人性化映射 ==========
  const toolDisplayNames = {
    'calculate_bazi': '🔮 正在為您排八字命盤...',
    'calculate_ziwei': '🌟 正在為您排紫微斗數命盤...',
    'calculate_astrology': '♈ 正在繪製您的星盤...',
    'calculate_numerology': '🔢 正在計算您的生命靈數...',
    'analyze_name': '✍️ 正在分析您的姓名...',
    'draw_tarot': '🃏 正在為您抽取塔羅牌...',
    'get_fortune': '✨ 正在查看您的運勢...',
    'calculate_compatibility': '💕 正在分析合盤...',
    'search_knowledge': '📚 正在查閱命理典籍...',
    'get_user_profile': '👤 正在讀取您的資料...',
    'lock_chart': '📋 正在鎖定命盤...',
  }

  const getToolDisplayName = (name) => {
    if (!name) return '⏳ 正在處理中...'
    if (toolDisplayNames[name]) return toolDisplayNames[name]
    // Fallback: convert snake_case to readable
    return `⏳ 正在執行 ${name.replace(/_/g, ' ')}...`
  }

  // ========== Textarea 自動擴展 ==========
  const handleInputChange = (e) => {
    setInputText(e.target.value)
    // Auto-expand textarea
    const textarea = e.target
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }

  // 同步高度（支援快速提問或外部 setInputText）
  useEffect(() => {
    if (!inputRef.current) return
    const textarea = inputRef.current
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
  }, [inputText])

  // ========== 鍵盤處理 ==========
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // ========== 快速提問 ==========
  const handleQuickPrompt = (text) => {
    setInputText(text)
    // 延遲一幀讓 state 更新後再發送
    setTimeout(() => sendMessage(text), 0)
  }

  // ========== 新對話（從 context 操作） ==========
  const startNewSession = useCallback(() => {
    setMessages([])
    setCurrentSession(null)
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }
  }, [setMessages, setCurrentSession])

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

      {/* 能力標籤 */}
      <div className="welcome-capabilities">
        <span className="capability-tag">🌟 紫微斗數</span>
        <span className="capability-tag">☯️ 八字命理</span>
        <span className="capability-tag">♈ 西洋占星</span>
        <span className="capability-tag">🔢 生命靈數</span>
        <span className="capability-tag">✍️ 姓名學</span>
        <span className="capability-tag">🃏 塔羅占卜</span>
      </div>

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

      {/* 信任指標 */}
      <div className="welcome-trust">
        <span className="trust-item">🔒 對話內容加密保護</span>
        <span className="trust-divider">·</span>
        <span className="trust-item">🧠 六大命理系統交叉驗證</span>
        <span className="trust-divider">·</span>
        <span className="trust-item">📊 AI 驅動精準分析</span>
      </div>
    </div>
  )

  return (
    <div className={`chat-container ${embedded ? 'embedded' : 'standalone'}`}>
      {/* 頂部操作列 */}
      <div className="chat-toolbar">
        {sidebarCollapsed && (
          <button
            className="toolbar-btn toolbar-sidebar-toggle"
            onClick={onToggleSidebar}
            title="開啟對話列表"
          >
            <span>☰</span>
          </button>
        )}
        <div className="toolbar-session-title">
          {currentSession ? '對話中' : '新對話'}
        </div>
        {messages.length > 0 && (
          <button
            className="toolbar-btn toolbar-new-chat"
            onClick={startNewSession}
            title="開始新對話"
          >
            <span>＋</span>
            <span className="new-chat-label">新對話</span>
          </button>
        )}
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
            <span>{getToolDisplayName(toolExecuting.name)}</span>
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
            {loadingTip && (
              <span className="loading-tip">{loadingTip}</span>
            )}
          </div>
        )}
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="輸入你的問題... (Shift+Enter 換行)"
            disabled={loading}
            rows={1}
          />
          {onOpenVoiceChat && (
            <button
              onClick={onOpenVoiceChat}
              className="btn-voice-input"
              title="語音對話"
              type="button"
            >
              🎤
            </button>
          )}
          <button
            onClick={() => sendMessage()}
            disabled={loading || !inputText.trim()}
            className="btn-send"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </div>

    </div>
  )
}

export default ChatContainer
