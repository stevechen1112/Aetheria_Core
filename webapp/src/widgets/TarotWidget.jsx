import './TarotWidget.css'

function buildConfirmMessage(confirmPrefix, question, spread) {
  const prefix = confirmPrefix || '[TAROT_DRAW_CONFIRM]'
  const payload = {
    question: (question || '').trim(),
    spread: (spread || 'three_card').trim() || 'three_card'
  }
  return `${prefix}${JSON.stringify(payload)}`
}

export function TarotDrawWidget({ data, onSendMessage }) {
  const question = data?.question || ''
  const spreadType = data?.spread_type || 'three_card'
  const spreadName = data?.spread_name || '三張牌（過去-現在-未來）'
  const positions = Array.isArray(data?.positions) ? data.positions : []
  const confirmPrefix = data?.confirm_prefix || '[TAROT_DRAW_CONFIRM]'

  const handleDraw = () => {
    if (!onSendMessage) return
    const msg = buildConfirmMessage(confirmPrefix, question, spreadType)
    onSendMessage(msg)
  }

  const slots = positions.length ? positions : (spreadType === 'single' ? ['當前指引'] : ['過去', '現在', '未來'])

  return (
    <div className="tarot-widget tarot-draw">
      <div className="tarot-header">
        <div className="tarot-title">🃏 {spreadName}</div>
        {question && <div className="tarot-question">問題：{question}</div>}
      </div>

      <div className="tarot-slots" role="group" aria-label="塔羅牌位">
        {slots.map((label, idx) => (
          <div className="tarot-slot" key={`${label}-${idx}`}>
            <div className="tarot-card-back" aria-hidden="true" />
            <div className="tarot-slot-label">{label}</div>
          </div>
        ))}
      </div>

      <button className="tarot-draw-btn" onClick={handleDraw} aria-label="抽牌">
        抽牌
      </button>

      <div className="tarot-hint">
        點擊後將以你的問題進行抽牌（不會自動抽）。
      </div>
    </div>
  )
}

export function TarotSpreadWidget({ data }) {
  const spreadName = data?.spread_name || data?.spread_type || '塔羅牌陣'
  const question = data?.question || ''
  const cards = Array.isArray(data?.cards) ? data.cards : []

  return (
    <div className="tarot-widget tarot-spread">
      <div className="tarot-header">
        <div className="tarot-title">🃏 {spreadName}</div>
        {question && <div className="tarot-question">問題：{question}</div>}
      </div>

      <div className="tarot-cards-row" role="group" aria-label="塔羅抽到的牌">
        {cards.map((c, idx) => {
          const reversed = !!c?.is_reversed
          const orientation = reversed ? '逆位' : '正位'
          const title = `${c?.position_index + 1 || idx + 1}. ${c?.position || ''}：${c?.name || ''}（${orientation}）`
          return (
            <div className="tarot-card" key={`${c?.id ?? idx}-${idx}`}>
              {c?.image_url ? (
                <img
                  className={`tarot-card-img ${reversed ? 'reversed' : ''}`}
                  src={c.image_url}
                  alt={title}
                  loading="lazy"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
              ) : (
                <div className="tarot-card-fallback" />
              )}
              <div className="tarot-card-meta">
                <div className="tarot-card-position">{c?.position || `第 ${idx + 1} 張`}</div>
                <div className="tarot-card-name">{c?.name || '—'}（{orientation}）</div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
