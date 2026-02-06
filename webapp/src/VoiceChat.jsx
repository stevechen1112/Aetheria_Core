import { useState, useEffect, useRef, useCallback } from 'react'
import './VoiceChat.css'

/**
 * VoiceChat Component - 語音/文字混合 AI 諮詢介面
 * 支援兩種模式：
 * 1. 文字模式：傳統文字對話
 * 2. 語音模式：使用 OpenAI Realtime WebRTC API 即時語音對話
 */
function VoiceChat({ apiBase, token, userId, onClose, embedded = false }) {
  // 基本狀態
  const [mode, setMode] = useState('text') // 'text' or 'voice'
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  const storagePrefix = userId || token || 'guest'
  const storageSessionKey = `aetheria_chat_session_id_${storagePrefix}`
  const storageMessagesKey = `aetheria_chat_messages_${storagePrefix}`
  
  // 語音模式狀態
  const [isConnected, setIsConnected] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [selectedVoice, setSelectedVoice] = useState('alloy')
  const [availableVoices, setAvailableVoices] = useState([])
  const [connectionError, setConnectionError] = useState('')
  
  // WebRTC 相關 refs
  const pcRef = useRef(null)
  const dcRef = useRef(null)
  const localStreamRef = useRef(null)
  const audioElRef = useRef(null)
  const messagesEndRef = useRef(null)

  // 舊版 Web Speech API refs（備援）
  const recognitionRef = useRef(null)

  // 載入可用語音選項
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const response = await fetch(`${apiBase}/api/voice/voices`)
        if (response.ok) {
          const data = await response.json()
          setAvailableVoices(data.voices || [])
          // 預設選擇推薦的語音
          const recommended = data.voices?.find(v => v.recommended)
          if (recommended) setSelectedVoice(recommended.id)
        }
      } catch (e) {
        console.warn('無法載入語音選項:', e)
        // 使用預設列表
        setAvailableVoices([
          { id: 'alloy', name: 'Alloy', description: '中性平衡' },
          { id: 'sage', name: 'Sage', description: '智慧沉穩' },
          { id: 'shimmer', name: 'Shimmer', description: '活潑輕快' }
        ])
      }
    }
    fetchVoices()
  }, [apiBase])

  // 初始化舊版 Web Speech API（作為備援）
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'zh-TW'

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInputText(transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = () => setIsListening(false)
      recognitionRef.current.onend = () => setIsListening(false)
    }

    return () => {
      disconnectRealtime()
      if (recognitionRef.current) recognitionRef.current.stop()
    }
  }, [disconnectRealtime])

  // 自動滾動到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 使用者切換時清空前端暫存狀態
  useEffect(() => {
    setMessages([])
    setSessionId(null)
  }, [storagePrefix])

  // 載入先前對話（優先從 API，失敗則用 localStorage）
  useEffect(() => {
    if (!token) return

    const loadMessages = async (sessId) => {
      try {
        const resp = await fetch(`${apiBase}/api/chat/messages?session_id=${sessId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (resp.status === 401) {
          localStorage.removeItem('aetheria_token')
          return
        }
        if (!resp.ok) throw new Error('load messages failed')
        const data = await resp.json()
        if (data?.messages?.length) {
          setMessages(data.messages.map(m => ({
            role: m.role,
            content: m.content,
            citations: m.citations || [],
            used_systems: m.used_systems || [],
            confidence: m.confidence || 0,
            timestamp: m.created_at || new Date().toISOString()
          })))
        }
      } catch (error) {
        console.warn('Load messages failed:', error)
        const cached = localStorage.getItem(storageMessagesKey)
        if (cached) {
          try {
            setMessages(JSON.parse(cached))
          } catch (error) {
            console.warn('Parse cached messages failed:', error)
          }
        }
      }
    }

    const init = async () => {
      const savedSession = localStorage.getItem(storageSessionKey)
      if (savedSession) {
        setSessionId(savedSession)
        await loadMessages(savedSession)
        return
      }

      try {
        const resp = await fetch(`${apiBase}/api/chat/sessions`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (resp.status === 401) {
          localStorage.removeItem('aetheria_token')
          return
        }
        if (!resp.ok) throw new Error('load sessions failed')
        const data = await resp.json()
        const latest = data?.sessions?.[0]
        if (latest?.session_id) {
          setSessionId(latest.session_id)
          localStorage.setItem(storageSessionKey, latest.session_id)
          await loadMessages(latest.session_id)
        }
      } catch (error) {
        console.warn('Init chat session failed:', error)
        const cached = localStorage.getItem(storageMessagesKey)
        if (cached) {
          try {
            setMessages(JSON.parse(cached))
          } catch (error) {
            console.warn('Parse cached messages failed:', error)
          }
        }
      }
    }

    init()
  }, [apiBase, token, storageMessagesKey, storageSessionKey])

  useEffect(() => {
    if (sessionId) localStorage.setItem(storageSessionKey, sessionId)
  }, [sessionId, storageSessionKey])

  useEffect(() => {
    if (messages?.length) {
      localStorage.setItem(storageMessagesKey, JSON.stringify(messages.slice(-200)))
    }
  }, [messages, storageMessagesKey])

  // 斷開 WebRTC 連線
  const disconnectRealtime = useCallback(() => {
    if (dcRef.current) {
      dcRef.current.close()
      dcRef.current = null
    }
    if (pcRef.current) {
      pcRef.current.close()
      pcRef.current = null
    }
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(t => t.stop())
      localStreamRef.current = null
    }
    if (audioElRef.current) {
      audioElRef.current.srcObject = null
      audioElRef.current = null
    }
    setIsConnected(false)
    setIsSpeaking(false)
  }, [])

  // 添加訊息
  const addMessage = useCallback((role, content) => {
    setMessages(prev => [...prev, {
      role,
      content,
      timestamp: new Date().toISOString()
    }])
  }, [])

  // 處理 Realtime API 事件
  const handleRealtimeEvent = useCallback((msg) => {
    switch (msg.type) {
      case 'conversation.item.created':
        if (msg.item?.role === 'user' && msg.item?.content?.[0]?.transcript) {
          const text = msg.item.content[0].transcript
          addMessage('user', text)
        }
        break
      
      case 'response.audio_transcript.delta':
        // AI 正在說話
        setIsSpeaking(true)
        break
      
      case 'response.audio_transcript.done':
        // AI 說完了
        if (msg.transcript) {
          addMessage('assistant', msg.transcript)
        }
        setIsSpeaking(false)
        break
      
      case 'response.done':
        setIsSpeaking(false)
        break
      
      case 'input_audio_buffer.speech_started':
        setIsListening(true)
        break
      
      case 'input_audio_buffer.speech_stopped':
        setIsListening(false)
        break
      
      case 'error':
        console.error('Realtime API 錯誤:', msg.error)
        setConnectionError(msg.error?.message || 'API 錯誤')
        break
      
      default:
        // 其他事件忽略
        break
    }
  }, [addMessage])

  // WebRTC 連接到 OpenAI Realtime
  const connectRealtime = useCallback(async () => {
    if (!token) {
      setConnectionError('請先登入')
      return
    }

    setConnectionError('')
    setLoading(true)

    try {
      // 取得麥克風權限
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      localStreamRef.current = stream
      const [audioTrack] = stream.getTracks()

      // 建立音訊播放元素
      const audioEl = new Audio()
      audioEl.autoplay = true
      audioElRef.current = audioEl

      // 建立 WebRTC PeerConnection
      const pc = new RTCPeerConnection()
      pcRef.current = pc

      // 加入本地音訊軌道
      pc.addTrack(audioTrack)

      // 處理遠端音訊
      pc.ontrack = (e) => {
        console.log('收到遠端音訊軌道')
        audioEl.srcObject = e.streams[0]
      }

      // 建立 DataChannel 接收事件
      const dc = pc.createDataChannel('oai-events')
      dcRef.current = dc

      dc.onopen = () => {
        console.log('DataChannel 已開啟')
        setIsConnected(true)
        setLoading(false)
        addMessage('system', '🎙️ 語音連線已建立，請開始說話...')
      }

      dc.onclose = () => {
        console.log('DataChannel 已關閉')
        setIsConnected(false)
      }

      dc.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          handleRealtimeEvent(msg)
        } catch (err) {
          console.warn('解析 Realtime 事件失敗:', err)
        }
      }

      // 建立 SDP offer
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      // 傳送到後端交換 SDP
      const response = await fetch(`${apiBase}/api/voice/session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sdp: offer.sdp,
          voice: selectedVoice
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `連線失敗 (${response.status})`)
      }

      const { sdp: answerSdp } = await response.json()
      
      // 設定遠端 SDP
      await pc.setRemoteDescription({
        type: 'answer',
        sdp: answerSdp
      })

    } catch (error) {
      console.error('Realtime 連線失敗:', error)
      setConnectionError(error.message || '連線失敗')
      setLoading(false)
      disconnectRealtime()
    }
  }, [apiBase, token, selectedVoice, addMessage, handleRealtimeEvent, disconnectRealtime])

  // 文字模式：發送訊息（Streaming 版本）
  const sendTextMessage = async () => {
    if (!inputText.trim()) return
    if (!token) {
      alert('請先登入後再使用 AI 諮詢')
      return
    }

    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    const userInput = inputText
    setInputText('')
    setLoading(true)

    // 添加一個空的 AI 訊息，準備接收 streaming 內容
    const assistantMessageId = `assistant-${Date.now()}-${Math.random().toString(36).slice(2)}`
    setMessages(prev => [...prev, {
      id: assistantMessageId,
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
        body: JSON.stringify({
          message: userInput,
          session_id: sessionId
        })
      })

      if (response.status === 401) {
        localStorage.removeItem('aetheria_token')
        throw new Error('請先登入')
      }

      if (!response.ok) {
        throw new Error(`請求失敗 (${response.status})`)
      }

      // 讀取 SSE 流
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
              
              // 處理不同類型的事件
              if (currentEvent === 'text' && data.chunk) {
                // 文字片段
                accumulatedText += data.chunk
                setMessages(prev => {
                  const newMessages = [...prev]
                  const targetIndex = newMessages.findIndex(m => m?.id === assistantMessageId)
                  if (targetIndex >= 0) {
                    newMessages[targetIndex] = {
                      ...newMessages[targetIndex],
                      content: accumulatedText
                    }
                  }
                  return newMessages
                })
              } else if (data.session_id && !sessionId) {
                // 新 session
                setSessionId(data.session_id)
              } else if (data.message) {
                // 狀態訊息（忽略或顯示在 UI）
                console.log('狀態:', data.message)
              } else if (data.name && data.status) {
                // 工具調用事件（可以顯示 UI 提示）
                if (data.status === 'executing') {
                  console.log('正在執行工具:', data.name)
                }
              }
            } catch (e) {
              console.warn('解析 SSE 資料失敗:', e, dataStr)
            }
          }
        }
      }

      // Streaming 完成，標記訊息為非 streaming
      setMessages(prev => {
        const newMessages = [...prev]
        const targetIndex = newMessages.findIndex(m => m?.id === assistantMessageId)
        if (targetIndex >= 0) {
          newMessages[targetIndex] = {
            ...newMessages[targetIndex],
            streaming: false
          }
        }
        return newMessages
      })

    } catch (error) {
      console.error('發送訊息失敗:', error)
      alert('發送失敗：' + error.message)
      
      // 移除失敗的 AI 訊息
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  // 語音模式：透過 DataChannel 發送文字（如果已連線）
  const sendVoiceText = () => {
    if (!inputText.trim()) return
    
    if (isConnected && dcRef.current?.readyState === 'open') {
      // 透過 WebRTC DataChannel 發送
      const event = {
        type: 'conversation.item.create',
        item: {
          type: 'message',
          role: 'user',
          content: [{ type: 'input_text', text: inputText }]
        }
      }
      dcRef.current.send(JSON.stringify(event))
      
      // 觸發回應
      dcRef.current.send(JSON.stringify({ type: 'response.create' }))
      
      addMessage('user', inputText)
      setInputText('')
    } else {
      // 未連線，使用文字模式
      sendTextMessage()
    }
  }

  // 切換模式
  const switchMode = (newMode) => {
    if (newMode === mode) return
    
    if (mode === 'voice' && isConnected) {
      disconnectRealtime()
    }
    
    setMode(newMode)
    setConnectionError('')
  }

  const wrapperClass = embedded ? 'voice-chat-page' : 'voice-chat-overlay'
  const containerClass = embedded ? 'voice-chat-container embedded' : 'voice-chat-container'

  return (
    <div
      className={wrapperClass}
      onClick={embedded ? undefined : (e) => e.target === e.currentTarget && onClose && onClose()}
    >
      <div className={containerClass}>
        {/* 頭部 */}
        <div className="voice-chat-header">
          <div className="header-title">
            <h2>AI 命理顧問</h2>
            <p className="header-subtitle">
              {mode === 'voice' 
                ? (isConnected ? '🎙️ 即時語音對話中' : '🎙️ 語音對話模式')
                : '💬 文字對話模式'}
            </p>
          </div>
        
          {/* 模式切換 */}
          <div className="mode-switch">
            <button
              className={`mode-btn ${mode === 'text' ? 'active' : ''}`}
              onClick={() => switchMode('text')}
              disabled={loading}
            >
              💬 文字
            </button>
            <button
              className={`mode-btn ${mode === 'voice' ? 'active' : ''}`}
              onClick={() => switchMode('voice')}
              disabled={loading}
            >
              🎙️ 語音
            </button>
          </div>

          {!embedded && onClose && (
            <button className="close-btn" onClick={onClose}>✕</button>
          )}
        </div>

        {/* 語音設定區（僅語音模式） */}
        {mode === 'voice' && !isConnected && (
          <div className="voice-settings">
            <div className="voice-select-group">
              <label>選擇語音風格：</label>
              <select 
                value={selectedVoice} 
                onChange={(e) => setSelectedVoice(e.target.value)}
                disabled={loading}
              >
                {availableVoices.map(v => (
                  <option key={v.id} value={v.id}>
                    {v.name} - {v.description}
                  </option>
                ))}
              </select>
            </div>
            {connectionError && (
              <div className="connection-error">⚠️ {connectionError}</div>
            )}
          </div>
        )}

        {/* 訊息列表 */}
        <div className="voice-chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">🔮</div>
              <p>您好！我是命理顧問</p>
              <p className="empty-hint">
                {mode === 'voice' 
                  ? (isConnected 
                      ? '請開始說話，我在聆聽...'
                      : '點擊「開始語音」連線後即可對話')
                  : '輸入您的問題開始諮詢'}
              </p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : msg.role === 'system' ? 'ℹ️' : '🔮'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
                
                {/* 引用來源 */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="message-citations">
                    <div className="citations-title">📚 依據：</div>
                    {msg.citations.map((cite, i) => (
                      <div key={i} className="citation-item">
                        <span className="citation-system">{cite.system || '未知'}</span>
                        <span className="citation-excerpt">
                          {cite.excerpt?.substring(0, 50)}...
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* 載入中 / 正在說話 指示 */}
          {(loading || isSpeaking) && (
            <div className="message assistant loading">
              <div className="message-avatar">🔮</div>
              <div className="message-content">
                <div className="loading-dots">
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* 輸入區域 */}
        <div className="voice-chat-input">
          {mode === 'voice' && (
            <div className="voice-controls">
              {!isConnected ? (
                <button
                  className="voice-btn connect"
                  onClick={connectRealtime}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="voice-icon">⏳</span>
                      <span>連線中...</span>
                    </>
                  ) : (
                    <>
                      <span className="voice-icon">🎙️</span>
                      <span>開始語音</span>
                    </>
                  )}
                </button>
              ) : (
                <>
                  <button
                    className={`voice-btn ${isListening ? 'listening' : ''}`}
                    disabled={true}
                  >
                    {isListening ? (
                      <>
                        <span className="pulse-ring"></span>
                        <span className="voice-icon">🎙️</span>
                        <span>正在聆聽...</span>
                      </>
                    ) : isSpeaking ? (
                      <>
                        <span className="voice-icon">🔊</span>
                        <span>AI 回答中...</span>
                      </>
                    ) : (
                      <>
                        <span className="voice-icon">🎤</span>
                        <span>請說話...</span>
                      </>
                    )}
                  </button>
                  <button
                    className="voice-btn disconnect"
                    onClick={disconnectRealtime}
                  >
                    ⏹️ 結束
                  </button>
                </>
              )}
            </div>
          )}

          <div className="input-row">
            <input
              type="text"
              className="chat-input"
              placeholder={mode === 'voice' ? '或輸入文字...' : '輸入您的問題...'}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !loading && (mode === 'voice' ? sendVoiceText() : sendTextMessage())}
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={mode === 'voice' ? sendVoiceText : sendTextMessage}
              disabled={!inputText.trim() || loading}
            >
              {loading ? '...' : '發送'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default VoiceChat
