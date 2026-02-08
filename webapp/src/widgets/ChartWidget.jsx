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
  const [showFullChart, setShowFullChart] = useState(false)

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
              <span className="value">{chart_data.ming_gong.position || '—'}</span>
            </div>
            {chart_data.ming_gong.main_stars?.length > 0 ? (
              <div className="chart-item">
                <span className="label">主星:</span>
                <span className="value">
                  {chart_data.ming_gong.main_stars.join('、')}
                  {chart_data.ming_gong.borrowed_palace && (
                    <span className="borrowed-note">（借{chart_data.ming_gong.borrowed_palace}）</span>
                  )}
                </span>
              </div>
            ) : (
              <div className="chart-item">
                <span className="label">主星:</span>
                <span className="value">空宮</span>
              </div>
            )}
            {chart_data.ming_gong.auxiliary_stars?.length > 0 && (
              <div className="chart-item">
                <span className="label">輔星:</span>
                <span className="value">{chart_data.ming_gong.auxiliary_stars.join('、')}</span>
              </div>
            )}
            {chart_data.five_elements && (
              <div className="chart-item">
                <span className="label">五行局:</span>
                <span className="value">{chart_data.five_elements}</span>
              </div>
            )}
            {chart_data.ming_zhu && (
              <div className="chart-item">
                <span className="label">命主:</span>
                <span className="value">{chart_data.ming_zhu}</span>
              </div>
            )}
            {chart_data.shen_zhu && (
              <div className="chart-item">
                <span className="label">身主:</span>
                <span className="value">{chart_data.shen_zhu}</span>
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
          setShowFullChart(prev => !prev)
        }}>
          {showFullChart ? '收起完整命盤 ▲' : '查看完整命盤 →'}
        </button>
      </div>

      {/* 完整命盤展開區 — 結構化呈現 */}
      {showFullChart && (
        <div className="chart-full-detail">
          {system === 'ziwei' && <ZiweiFullDetail data={chart_data} />}
          {system === 'bazi' && <BaziFullDetail data={chart_data} />}
          {system === 'astrology' && <AstrologyFullDetail data={chart_data} />}
          {!['ziwei', 'bazi', 'astrology'].includes(system) && (
            <GenericFullDetail data={chart_data} />
          )}
        </div>
      )}
    </div>
  )
}

/* ========== 紫微斗數完整命盤 ========== */
function ZiweiFullDetail({ data }) {
  if (!data) return null

  return (
    <div className="full-detail-sections">
      {/* 四化 */}
      {data.si_hua && typeof data.si_hua === 'object' && !Array.isArray(data.si_hua) && (
        <div className="detail-block">
          <div className="detail-block-title">四化星</div>
          <div className="chart-grid">
            {Object.entries(data.si_hua).map(([key, val]) => (
              <div className="chart-item" key={key}>
                <span className="label">{key}:</span>
                <span className="value">{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 命宮完整資訊 */}
      {data.ming_gong && (
        <div className="detail-block">
          <div className="detail-block-title">命宮詳情</div>
          <div className="chart-grid">
            <div className="chart-item">
              <span className="label">宮位:</span>
              <span className="value">{data.ming_gong.position || '—'}</span>
            </div>
            <div className="chart-item">
              <span className="label">主星:</span>
              <span className="value">
                {data.ming_gong.main_stars?.join('、') || '空宮'}
                {data.ming_gong.borrowed_palace && (
                  <span className="borrowed-note">（借{data.ming_gong.borrowed_palace}）</span>
                )}
              </span>
            </div>
            {data.ming_gong.auxiliary_stars?.length > 0 && (
              <div className="chart-item">
                <span className="label">輔星:</span>
                <span className="value">{data.ming_gong.auxiliary_stars.join('、')}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 基本命盤資訊 */}
      <div className="detail-block">
        <div className="detail-block-title">命盤基礎</div>
        <div className="chart-grid">
          {data.five_elements && (
            <div className="chart-item">
              <span className="label">五行局:</span>
              <span className="value">{data.five_elements}</span>
            </div>
          )}
          {data.ming_zhu && (
            <div className="chart-item">
              <span className="label">命主:</span>
              <span className="value">{data.ming_zhu}</span>
            </div>
          )}
          {data.shen_zhu && (
            <div className="chart-item">
              <span className="label">身主:</span>
              <span className="value">{data.shen_zhu}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ========== 八字完整命盤 ========== */
function BaziFullDetail({ data }) {
  if (!data) return null

  return (
    <div className="full-detail-sections">
      {/* 四柱 */}
      {data.four_pillars && (
        <div className="detail-block">
          <div className="detail-block-title">四柱排盤</div>
          <div className="bazi-pillars">
            {['year', 'month', 'day', 'hour'].map(key => {
              const labels = { year: '年柱', month: '月柱', day: '日柱', hour: '時柱' }
              return (
                <div className="pillar" key={key}>
                  <div className="pillar-label">{labels[key]}</div>
                  <div className="pillar-value">{data.four_pillars[key] || '—'}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* 日主與強弱 */}
      <div className="detail-block">
        <div className="detail-block-title">日主分析</div>
        <div className="chart-grid">
          {data.day_master && (
            <div className="chart-item">
              <span className="label">日主五行:</span>
              <span className="value">{data.day_master}</span>
            </div>
          )}
          {data.strength && (
            <div className="chart-item">
              <span className="label">身強/身弱:</span>
              <span className="value">{data.strength}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ========== 西洋占星完整命盤 ========== */
function AstrologyFullDetail({ data }) {
  if (!data) return null

  const planetNames = {
    sun: '☀️ 太陽', moon: '🌙 月亮', mercury: '☿ 水星', venus: '♀ 金星',
    mars: '♂ 火星', jupiter: '♃ 木星', saturn: '♄ 土星',
    uranus: '♅ 天王星', neptune: '♆ 海王星', pluto: '♇ 冥王星',
    ascendant: '⬆ 上升點', midheaven: 'MC 天頂'
  }

  return (
    <div className="full-detail-sections">
      {/* 主要三大星座 */}
      <div className="detail-block">
        <div className="detail-block-title">三大星座</div>
        <div className="chart-grid">
          {data.sun_sign && (
            <div className="chart-item">
              <span className="label">☀️ 太陽:</span>
              <span className="value">{data.sun_sign}</span>
            </div>
          )}
          {data.moon_sign && (
            <div className="chart-item">
              <span className="label">🌙 月亮:</span>
              <span className="value">{data.moon_sign}</span>
            </div>
          )}
          {data.rising_sign && (
            <div className="chart-item">
              <span className="label">⬆ 上升:</span>
              <span className="value">{data.rising_sign}</span>
            </div>
          )}
        </div>
      </div>

      {/* 所有行星 */}
      {data.planets && Object.keys(data.planets).length > 0 && (
        <div className="detail-block">
          <div className="detail-block-title">行星位置</div>
          <div className="chart-grid">
            {Object.entries(data.planets).map(([key, planet]) => {
              if (!planet || typeof planet !== 'object') return null
              const name = planetNames[key] || key
              const sign = planet.sign_zh || planet.sign || ''
              const degree = planet.degree != null ? `${planet.degree.toFixed?.(1) ?? planet.degree}°` : ''
              const house = planet.house ? `第${planet.house}宮` : ''
              return (
                <div className="chart-item" key={key}>
                  <span className="label">{name}:</span>
                  <span className="value">{sign} {degree} {house}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

/* ========== 通用展示（其他命理系統） ========== */
function GenericFullDetail({ data }) {
  if (!data) return null

  const renderValue = (val) => {
    if (val == null) return '—'
    if (typeof val === 'string' || typeof val === 'number') return String(val)
    if (Array.isArray(val)) return val.join('、')
    if (typeof val === 'object') {
      return (
        <div className="nested-grid">
          {Object.entries(val).map(([k, v]) => (
            <div className="chart-item" key={k}>
              <span className="label">{k}:</span>
              <span className="value">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
            </div>
          ))}
        </div>
      )
    }
    return String(val)
  }

  return (
    <div className="full-detail-sections">
      <div className="detail-block">
        <div className="detail-block-title">完整資料</div>
        <div className="chart-grid">
          {Object.entries(data).map(([key, val]) => (
            <div className="chart-item" key={key}>
              <span className="label">{key}:</span>
              <span className="value">{renderValue(val)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ChartWidget
