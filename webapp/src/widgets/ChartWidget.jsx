import { useState } from 'react'
import './ChartWidget.css'

/**
 * ChartWidget - 嵌入式命盤卡片組件
 * 
 * 用途：在對話中顯示命盤快照
 * 支援：紫微、八字、西洋占星等系統
 * 模式：compact (簡要) / full (完整)
 */
function normalizeChartData(raw) {
  if (!raw) return null

  if (raw.chart_data || raw.analysis || raw.birth_info) {
    return raw
  }

  const chart_data = raw.chart_data || raw
  const analysis = raw.analysis || {
    summary: raw.summary || ''
  }

  return {
    system: raw.system,
    user_name: raw.user_name,
    birth_info: raw.birth_info,
    analysis,
    chart_data
  }
}

function ChartWidget({ data, compact = true }) {
  const [expanded, setExpanded] = useState(!compact)

  const normalized = normalizeChartData(data)

  if (!normalized) {
    return <div className="chart-widget chart-loading">載入命盤資料...</div>
  }

  const { system, user_name, birth_info, analysis, chart_data } = normalized

  // 系統圖示映射
  const systemIcons = {
    'ziwei': '🌟',
    'bazi': '☯️',
    'astrology': '♈',
    'numerology': '🔢',
    'name': '✍️',
    'tarot': '🃏'
  }

  const systemNames = {
    'ziwei': '紫微斗數',
    'bazi': '八字命理',
    'astrology': '西洋占星',
    'numerology': '生命靈數',
    'name': '姓名學',
    'tarot': '塔羅占卜'
  }

  const icon = systemIcons[system] || '⭐'
  const systemName = systemNames[system] || system

  // Compact 模式：簡潔卡片
  if (!expanded) {
    return (
      <div className="chart-widget chart-compact" onClick={() => setExpanded(true)}>
        <div className="chart-header">
          <span className="chart-icon">{icon}</span>
          <div className="chart-info">
            <div className="chart-title">{systemName}</div>
            <div className="chart-subtitle">
              {user_name && <span>{user_name}</span>}
              {birth_info?.birth_date && (
                <span className="birth-date">{birth_info.birth_date}</span>
              )}
            </div>
          </div>
          <button className="btn-expand">展開 ▼</button>
        </div>
        {analysis?.summary && (
          <div className="chart-summary">
            {analysis.summary.slice(0, 60)}...
          </div>
        )}
      </div>
    )
  }

  // Expanded 模式：詳細資訊
  return (
    <div className="chart-widget chart-expanded">
      <div className="chart-header">
        <span className="chart-icon">{icon}</span>
        <div className="chart-info">
          <div className="chart-title">{systemName}</div>
          <div className="chart-subtitle">
            {user_name && <span>{user_name}</span>}
            {birth_info?.birth_date && (
              <span className="birth-date">{birth_info.birth_date}</span>
            )}
            {birth_info?.birth_time && (
              <span className="birth-time">{birth_info.birth_time}</span>
            )}
          </div>
        </div>
        <button className="btn-collapse" onClick={() => setExpanded(false)}>
          收起 ▲
        </button>
      </div>

      {/* 命盤核心資訊 */}
      {system === 'ziwei' && chart_data?.ming_gong && (
        <div className="chart-section">
          <div className="section-title">命宮資訊</div>
          <div className="chart-grid">
            <div className="chart-item">
              <span className="label">命宮位置:</span>
              <span className="value">{chart_data.ming_gong.position}</span>
            </div>
            {chart_data.ming_gong.main_stars && (
              <div className="chart-item">
                <span className="label">主星:</span>
                <span className="value">{chart_data.ming_gong.main_stars.join('、')}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {system === 'bazi' && chart_data?.four_pillars && (
        <div className="chart-section">
          <div className="section-title">四柱八字</div>
          <div className="bazi-pillars">
            <div className="pillar">
              <div className="pillar-label">年柱</div>
              <div className="pillar-value">{chart_data.four_pillars.year}</div>
            </div>
            <div className="pillar">
              <div className="pillar-label">月柱</div>
              <div className="pillar-value">{chart_data.four_pillars.month}</div>
            </div>
            <div className="pillar">
              <div className="pillar-label">日柱</div>
              <div className="pillar-value">{chart_data.four_pillars.day}</div>
            </div>
            <div className="pillar">
              <div className="pillar-label">時柱</div>
              <div className="pillar-value">{chart_data.four_pillars.hour}</div>
            </div>
          </div>
        </div>
      )}

      {system === 'astrology' && chart_data?.sun_sign && (
        <div className="chart-section">
          <div className="section-title">主要星座</div>
          <div className="chart-grid">
            <div className="chart-item">
              <span className="label">太陽星座:</span>
              <span className="value">{chart_data.sun_sign}</span>
            </div>
            {chart_data.moon_sign && (
              <div className="chart-item">
                <span className="label">月亮星座:</span>
                <span className="value">{chart_data.moon_sign}</span>
              </div>
            )}
            {chart_data.rising_sign && (
              <div className="chart-item">
                <span className="label">上升星座:</span>
                <span className="value">{chart_data.rising_sign}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 分析摘要 */}
      {analysis?.summary && (
        <div className="chart-section">
          <div className="section-title">分析摘要</div>
          <div className="chart-analysis">
            {analysis.summary}
          </div>
        </div>
      )}

      {/* 關鍵洞察 */}
      {analysis?.key_insights && analysis.key_insights.length > 0 && (
        <div className="chart-section">
          <div className="section-title">關鍵洞察</div>
          <ul className="insights-list">
            {analysis.key_insights.map((insight, idx) => (
              <li key={idx}>{insight}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 查看完整命盤按鈕 */}
      <div className="chart-actions">
        <button className="btn-view-full" onClick={() => {
          // TODO: 觸發父組件開啟完整命盤 Modal
          console.log('Open full chart for', system)
        }}>
          查看完整命盤 →
        </button>
      </div>
    </div>
  )
}

export default ChartWidget
