import { useState, useEffect, useRef } from 'react'

/**
 * VoiceChat Component - 语音/文字混合AI咨询界面
 * 使用浏览器 Web Speech API 实现语音识别和合成
 */
function VoiceChat({ apiBase, token, onClose }) {
  const [mode, setMode] = useState('text') // 'text' or 'voice'
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const recognitionRef = useRef(null)
  const synthesisRef = useRef(null)
  const messagesEndRef = useRef(null)

  // 初始化 Web Speech API
  useEffect(() => {
    // 检查浏览器支持
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn('浏览器不支持语音识别')
    }
    if (!('speechSynthesis' in window)) {
      console.warn('浏览器不支持语音合成')
    }

    // 初始化语音识别
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

      recognitionRef.current.onerror = (event) => {
        console.error('语音识别错误:', event.error)
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 开始/停止语音识别
  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('浏览器不支持语音识别功能')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (error) {
        console.error('启动语音识别失败:', error)
      }
    }
  }

  // 语音合成
  const speak = (text) => {
    if (!window.speechSynthesis) {
      console.warn('浏览器不支持语音合成')
      return
    }

    // 停止当前播放
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-TW'
    utterance.rate = 0.9 // 语速
    utterance.pitch = 1.0 // 音调

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }

  // 停止语音播放
  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  // 发送消息
  const sendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setLoading(true)

    try {
      const response = await fetch(`${apiBase}/api/chat/consult`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputText,
          session_id: sessionId,
          voice_mode: mode === 'voice' // 传递语音模式标记
        })
      })

      const data = await response.json()

      if (data.status === 'success') {
        if (!sessionId) {
          setSessionId(data.session_id)
        }

        const assistantMessage = {
          role: 'assistant',
          content: data.reply,
          citations: data.citations || [],
          used_systems: data.used_systems || [],
          confidence: data.confidence || 0,
          timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, assistantMessage])

        // 语音模式下自动播放回复
        if (mode === 'voice') {
          speak(data.reply)
        }
      } else {
        throw new Error(data.error || '请求失败')
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      alert('发送失败：' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // 切换模式
  const switchMode = (newMode) => {
    if (newMode !== mode) {
      stopSpeaking()
      if (isListening) {
        recognitionRef.current?.stop()
      }
      setMode(newMode)
    }
  }

  return (
    <div className="voice-chat-container">
      {/* 头部 */}
      <div className="voice-chat-header">
        <div className="header-title">
          <h2>AI 命理顾问</h2>
          <p className="header-subtitle">
            {mode === 'voice' ? '🎙️ 语音对话模式' : '💬 文字对话模式'}
          </p>
        </div>
        
        {/* 模式切换 */}
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
            🎙️ 语音
          </button>
        </div>

        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      {/* 消息列表 */}
      <div className="voice-chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🔮</div>
            <p>您好！我是命理顾问</p>
            <p className="empty-hint">
              {mode === 'voice' 
                ? '点击麦克风按钮开始语音对话'
                : '输入您的问题开始咨询'}
            </p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🔮'}
            </div>
            <div className="message-content">
              <div className="message-text">{msg.content}</div>
              
              {/* 引用来源 */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="message-citations">
                  <div className="citations-title">📚 依据：</div>
                  {msg.citations.map((cite, i) => (
                    <div key={i} className="citation-item">
                      <span className="citation-system">
                        {cite.system || '未知'}
                      </span>
                      <span className="citation-excerpt">
                        {cite.excerpt?.substring(0, 50)}...
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* 语音模式下显示播放控制 */}
              {mode === 'voice' && msg.role === 'assistant' && (
                <div className="message-actions">
                  {isSpeaking ? (
                    <button className="action-btn" onClick={stopSpeaking}>
                      🔊 停止播放
                    </button>
                  ) : (
                    <button className="action-btn" onClick={() => speak(msg.content)}>
                      🔈 重新播放
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
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

      {/* 输入区域 */}
      <div className="voice-chat-input">
        {mode === 'voice' && (
          <div className="voice-controls">
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleListening}
              disabled={loading}
            >
              {isListening ? (
                <>
                  <span className="pulse-ring"></span>
                  <span className="voice-icon">🎙️</span>
                  <span>正在聆听...</span>
                </>
              ) : (
                <>
                  <span className="voice-icon">🎤</span>
                  <span>点击说话</span>
                </>
              )}
            </button>
            
            {isSpeaking && (
              <div className="speaking-indicator">
                <span className="speaker-icon">🔊</span>
                <span>AI 正在回答...</span>
              </div>
            )}
          </div>
        )}

        <div className="input-row">
          <input
            type="text"
            className="chat-input"
            placeholder={mode === 'voice' ? '或输入文字...' : '输入您的问题...'}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={!inputText.trim() || loading}
          >
            {loading ? '...' : '发送'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default VoiceChat
