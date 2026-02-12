import { useState, useCallback, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import ChartWidget from './widgets/ChartWidget'
import { TarotDrawWidget, TarotSpreadWidget } from './widgets/TarotWidget'
import './MessageRenderer.css'

/**
 * MessageRenderer - 統一訊息渲染器
 * 
 * 支援類型：
 * - text: 純文字/Markdown 訊息
 * - widget: 嵌入式互動組件 (chart, insight, system_card, progress)
 * - system_event: 系統事件通知
 * 
 * §11.2: 包含回饋按鈕（👍👎）供用戶評價
 */
function MessageRenderer({ message, apiBase, token, sessionId, onSendMessage }) {
  const [feedbackGiven, setFeedbackGiven] = useState(null) // 'helpful' | 'not_helpful' | null
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [copyStatus, setCopyStatus] = useState('') // '' | 'success' | 'error'
  const [renderedText, setRenderedText] = useState('')
  const renderIndexRef = useRef(0)

  // 長文閾值（字元數）
  const COLLAPSE_THRESHOLD = 600

  // 打字機效果（僅 assistant 訊息）
  useEffect(() => {
    if (message.role !== 'assistant') {
      setRenderedText(message.content || '')
      return
    }

    renderIndexRef.current = 0
    setRenderedText('')
  }, [message.id, message.role])

  useEffect(() => {
    if (message.role !== 'assistant') return

    const target = message.content || ''
    if (!target) {
      setRenderedText('')
      renderIndexRef.current = 0
      return
    }

    let timerId = null
    const stepSize = target.length > 1200 ? 3 : target.length > 600 ? 2 : 1
    const speedMs = 12

    const tick = () => {
      if (renderIndexRef.current >= target.length) return
      renderIndexRef.current = Math.min(renderIndexRef.current + stepSize, target.length)
      setRenderedText(target.slice(0, renderIndexRef.current))
      timerId = window.setTimeout(tick, speedMs)
    }

    tick()
    return () => {
      if (timerId) window.clearTimeout(timerId)
    }
  }, [message.content, message.role])

  // 複製訊息內容
  const copyContent = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content || '')
      setCopyStatus('success')
      setTimeout(() => setCopyStatus(''), 2000)
    } catch {
      // Fallback
      try {
        const ta = document.createElement('textarea')
        ta.value = message.content || ''
        document.body.appendChild(ta)
        ta.select()
        const success = document.execCommand('copy')
        document.body.removeChild(ta)
        if (!success) throw new Error('copy failed')
        setCopyStatus('success')
        setTimeout(() => setCopyStatus(''), 2000)
      } catch {
        setCopyStatus('error')
        setTimeout(() => setCopyStatus(''), 2000)
      }
    }
  }, [message.content])

  // §11.2 回饋提交
  const submitFeedback = useCallback(async (rating) => {
    if (!sessionId) {
      console.warn('回饋提交失敗: 缺少 session_id')
      return
    }
    setFeedbackGiven(rating)
    try {
      await fetch(`${apiBase || ''}/api/chat/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          session_id: sessionId || '',
          message_id: message.id,
          rating: rating
        })
      })
    } catch (e) {
      console.warn('回饋提交失敗:', e)
    }
  }, [apiBase, token, message.id, sessionId])
  // 文字訊息
  if (message.type === 'text') {
    return (
      <div className={`message message-${message.role}`}>
        <div className="message-avatar">
          {message.role === 'user' ? '👤' : '🔮'}
        </div>
        <div className="message-content">
          <div className="message-body">
            {message.streaming ? (
              <div className="streaming-text">
                {message.role === 'assistant' ? renderedText : message.content}
                <span className="cursor">▊</span>
              </div>
            ) : (
              <>
                {message.role === 'assistant' && message.content && message.content.length > COLLAPSE_THRESHOLD ? (
                  <div className={`collapsible-text ${isCollapsed ? 'collapsed' : 'expanded'}`}>
                    <div className="collapsible-content">
                      <ReactMarkdown>{message.role === 'assistant' ? renderedText : message.content}</ReactMarkdown>
                    </div>
                    <button
                      className="btn-collapse-toggle"
                      onClick={() => setIsCollapsed(prev => !prev)}
                      aria-label={isCollapsed ? '展開全文' : '收起全文'}
                    >
                      {isCollapsed ? '展開全文 ▼' : '收起 ▲'}
                    </button>
                  </div>
                ) : (
                  <ReactMarkdown>{message.role === 'assistant' ? renderedText : (message.content || '...')}</ReactMarkdown>
                )}
              </>
            )}
          </div>
          {message.citations && message.citations.length > 0 && (
            <div className="message-citations">
              <details>
                <summary>📚 參考來源 ({message.citations.length})</summary>
                <ul>
                  {message.citations.map((cite, idx) => (
                    <li key={idx}>
                      <strong>{cite.system}:</strong> {cite.source}
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
          {message.used_systems && message.used_systems.length > 0 && (
            <div className="message-systems">
              {message.used_systems.map((sys, idx) => (
                <span key={idx} className="system-badge">{sys}</span>
              ))}
            </div>
          )}
          <div className="message-timestamp">
            {new Date(message.timestamp).toLocaleTimeString('zh-TW', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
          {/* §11.2 回饋按鈕 + 複製 — 僅 assistant 且非串流中 */}
          {message.role === 'assistant' && !message.streaming && (
            <div className="message-actions">
              <button
                className="action-btn copy-btn"
                onClick={copyContent}
                title="複製內容"
                aria-label="複製內容"
              >
                {copyStatus === 'success' ? '✅ 已複製' : copyStatus === 'error' ? '⚠️ 複製失敗' : '📋 複製'}
              </button>
              <div className="message-feedback">
                {feedbackGiven ? (
                  <span className="feedback-thanks">
                    {feedbackGiven === 'helpful' ? '👍' : '👎'} 感謝回饋
                  </span>
                ) : (
                  <>
                    <button
                      className="feedback-btn feedback-up"
                      onClick={() => submitFeedback('helpful')}
                      title="有幫助"
                      aria-label="有幫助"
                    >👍</button>
                    <button
                      className="feedback-btn feedback-down"
                      onClick={() => submitFeedback('not_helpful')}
                      title="沒幫助"
                      aria-label="沒幫助"
                    >👎</button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Widget 訊息
  if (message.type === 'widget') {
    return (
      <div className="message message-widget">
        <div className="message-avatar">🔮</div>
        <div className="message-content">
          {message.widget_type === 'chart' && (
            <ChartWidget 
              data={message.widget_data}
              compact={message.compact}
              apiBase={apiBase}
              token={token}
            />
          )}
          {message.widget_type === 'insight' && (
            <div className="widget-insight">
              <div className="insight-header">
                <span className="insight-icon">{message.widget_data.icon || '💡'}</span>
                <span className="insight-title">{message.widget_data.title}</span>
              </div>
              <div className="insight-body">
                <ReactMarkdown>{message.widget_data.content}</ReactMarkdown>
              </div>
              {message.widget_data.confidence && (
                <div className="insight-confidence">
                  可信度: {(message.widget_data.confidence * 100).toFixed(0)}%
                </div>
              )}
            </div>
          )}
          {message.widget_type === 'system_card' && (
            <div className="widget-system-card">
              <div className="system-card-header">
                <span className="system-icon">{message.widget_data.icon || '⭐'}</span>
                <span className="system-name">{message.widget_data.system_name}</span>
              </div>
              <div className="system-card-content">
                {message.widget_data.summary}
              </div>
              {message.widget_data.details && (
                <details>
                  <summary>查看詳情</summary>
                  <div className="system-card-details">
                    <ReactMarkdown>{message.widget_data.details}</ReactMarkdown>
                  </div>
                </details>
              )}
            </div>
          )}
          {message.widget_type === 'progress' && (
            <div className="widget-progress">
              <div className="progress-header">
                <span className="progress-icon">
                  {message.widget_data.status === 'completed' ? '✅' : 
                   message.widget_data.status === 'error' ? '❌' : 
                   message.widget_data.status === 'running' ? '⏳' : '⏸️'}
                </span>
                <span className="progress-task">{message.widget_data.task_name}</span>
              </div>
              <div className="progress-bar-container">
                <div 
                  className={`progress-bar progress-${message.widget_data.status}`}
                  style={{width: `${message.widget_data.progress * 100}%`}}
                />
              </div>
              {message.widget_data.message && (
                <div className="progress-message">{message.widget_data.message}</div>
              )}
              <div className="progress-percentage">
                {(message.widget_data.progress * 100).toFixed(0)}%
              </div>
            </div>
          )}

          {message.widget_type === 'tarot_draw' && (
            <TarotDrawWidget
              data={message.widget_data}
              onSendMessage={onSendMessage}
            />
          )}

          {message.widget_type === 'tarot_spread' && (
            <TarotSpreadWidget data={message.widget_data} />
          )}
          <div className="message-timestamp">
            {new Date(message.timestamp).toLocaleTimeString('zh-TW', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        </div>
      </div>
    )
  }

  // 系統事件
  if (message.type === 'system_event') {
    return (
      <div className="message message-system-event">
        <div className="event-content">
          <span className="event-icon">ℹ️</span>
          <span className="event-text">{message.content}</span>
        </div>
      </div>
    )
  }

  return null
}

export default MessageRenderer
