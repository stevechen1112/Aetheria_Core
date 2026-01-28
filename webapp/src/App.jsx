import { useEffect, useState, useMemo } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.v2.css'
import VoiceChat from './VoiceChat'

/* ==========================================
   Aetheria Core - v2.0 完全重新設計
   現代化命理分析平台
========================================== */

function App() {
  // ========== State Management ==========
  const [apiBase, setApiBase] = useState(
    localStorage.getItem('aetheria_api_base') || 'http://localhost:5001'
  )
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [profile, setProfile] = useState(null)
  const [birthInfo, setBirthInfo] = useState(null)
  const [currentView, setCurrentView] = useState('home') // home, chart, systems, strategic, settings, profile
  const [currentSystem, setCurrentSystem] = useState(null) // ziwei, bazi, astrology, etc.
  
  // Loading & Toast
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ show: false, message: '', type: 'info' })
  
  // Auth Modal
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState('login') // login or register
  const [authForm, setAuthForm] = useState({
    email: '',
    password: '',
    display_name: ''
  })
  
  // Chart Data
  const [chartLocked, setChartLocked] = useState(false)
  const [chartSummary, setChartSummary] = useState(null)
  const [chartAnalysis, setChartAnalysis] = useState(null) // 完整的綜合分析
  const [systemAnalysis, setSystemAnalysis] = useState({}) // 各系統詳細分析
  const [overviewData, setOverviewData] = useState(null)
  const [overviewLoading, setOverviewLoading] = useState(false)
  const [systemData, setSystemData] = useState(null)
  const [systemLoading, setSystemLoading] = useState(false)
  const [astrologyMode, setAstrologyMode] = useState('report')
  const [astrologyTransitDate, setAstrologyTransitDate] = useState(
    new Date().toISOString().slice(0, 10)
  )
  const [astrologyResult, setAstrologyResult] = useState(null)
  const [astrologyLoading, setAstrologyLoading] = useState(false)
  const [astrologyError, setAstrologyError] = useState('')
  const [tarotForm, setTarotForm] = useState({
    spread_type: 'three_card',
    question: '',
    context: 'general',
    allow_reversed: true,
    use_ai: false
  })
  const [tarotResult, setTarotResult] = useState(null)
  const [tarotLoading, setTarotLoading] = useState(false)
  const [tarotError, setTarotError] = useState('')
  
  // Voice Chat
  const [showVoiceChat, setShowVoiceChat] = useState(false)
  
  // Wizard for chart creation
  const [wizardStep, setWizardStep] = useState(1)
  const [chartForm, setChartForm] = useState({
    birth_date: '',
    birth_time: '',
    birth_location: '',
    gender: '男',
    chinese_name: '',
    english_name: '',
    ziwei_ruleset: 'no_day_advance'
  })

  // Profile View State (Lifted up)
  const [profileEditMode, setProfileEditMode] = useState(false)
  const [profileEditForm, setProfileEditForm] = useState({
    name: '',
    gender: '男',
    birth_date: '',
    birth_time: '',
    birth_location: ''
  })
  const [profileSaving, setProfileSaving] = useState(false)

  // ========== API Helpers ==========
  const authHeaders = useMemo(() => {
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    return headers
  }, [token])

  const apiCall = async (path, payload = null, method = 'POST') => {
    try {
      const options = {
        method: payload ? method : 'GET',
        headers: authHeaders
      }
      if (payload) {
        options.body = JSON.stringify(payload)
      }
      const response = await fetch(`${apiBase}${path}`, options)
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.message || data.error || 'API 失敗')
      }
      return data
    } catch (error) {
      showToast(error.message, 'error')
      throw error
    }
  }

  // 不彈 Toast 的狀態查詢（避免初始化時干擾使用者）
  const apiCallSilent = async (path, payload = null, method = 'POST') => {
    try {
      const options = {
        method: payload ? method : 'GET',
        headers: authHeaders
      }
      if (payload) options.body = JSON.stringify(payload)
      const response = await fetch(`${apiBase}${path}`, options)
      const data = await response.json().catch(() => null)
      if (!response.ok) return null
      return data
    } catch {
      return null
    }
  }

  const getTarotImageFilename = (card) => {
    if (!card) return null
    const nameEn = (card.name_en || '').trim()
    if (!nameEn) return null
    const normalized = nameEn.replace(/\s+/g, '_')
    const isMajor = card.meaning?.arcana === 'major' || card.id <= 21
    if (isMajor) {
      const prefix = String(card.id).padStart(2, '0')
      return `${prefix}_${normalized}.jpg`
    }
    return `${normalized}.jpg`
  }

  const getTarotImageUrl = (card) => {
    const filename = getTarotImageFilename(card)
    if (!filename) return null
    return `/tarot/${filename}`
  }

  const TarotCardImage = ({ imageUrl, alt, expectedFilename }) => {
    const [errored, setErrored] = useState(false)

    if (!imageUrl || errored) {
      return (
        <div
          style={{
            width: '120px',
            height: '180px',
            background: 'var(--color-bg-secondary)',
            border: '1px dashed var(--color-border)',
            borderRadius: 'var(--radius-sm)',
            display: 'grid',
            placeItems: 'center',
            padding: 'var(--spacing-sm)',
            textAlign: 'center',
            color: 'var(--color-text-muted)'
          }}
        >
          <div style={{display: 'grid', gap: '6px'}}>
            <div style={{fontSize: '20px'}}>🎴</div>
            <div style={{fontSize: '12px', fontWeight: 600}}>缺少牌圖</div>
            {expectedFilename && (
              <div style={{fontSize: '11px', wordBreak: 'break-all'}}>預期：{expectedFilename}</div>
            )}
          </div>
        </div>
      )
    }

    return (
      <img
        src={imageUrl}
        alt={alt}
        style={{width: '100%', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--shadow-sm)'}}
        onError={() => setErrored(true)}
      />
    )
  }

  const getChartPayload = () => {
    const birth_date = chartForm.birth_date || chartSummary?.birth_date
    const birth_time = chartForm.birth_time || chartSummary?.birth_time
    const birth_location = chartForm.birth_location || chartSummary?.birth_location
    return { birth_date, birth_time, birth_location }
  }

  const getBirthParts = () => {
    const { birth_date, birth_time, birth_location } = getChartPayload()
    if (!birth_date || !birth_time) return null
    const [year, month, day] = birth_date.split('-').map((v) => parseInt(v, 10))
    const [hour, minute] = birth_time.split(':').map((v) => parseInt(v, 10))
    if ([year, month, day, hour, minute].some((v) => Number.isNaN(v))) return null
    return { year, month, day, hour, minute, birth_location }
  }

  const ensureChartPayload = () => {
    const { birth_date, birth_time, birth_location } = getChartPayload()
    if (!birth_date || !birth_time || !birth_location) return null
    return { birth_date, birth_time, birth_location }
  }

  // ========== Toast System ==========
  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000)
  }

  // ========== Auth Functions ==========
  const handleLogin = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/auth/login', {
        email: authForm.email.trim(),
        password: authForm.password.trim()
      })
      localStorage.setItem('aetheria_token', data.token)
      setToken(data.token)
      setShowAuthModal(false)
      showToast('登入成功！', 'success')
      setAuthForm({ email: '', password: '', display_name: '' })
    } catch (error) {
      // Error already shown by apiCall
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/auth/register', {
        email: authForm.email.trim(),
        password: authForm.password.trim(),
        display_name: authForm.display_name.trim(),
        consents: { terms_accepted: true, data_usage_accepted: true }
      })
      localStorage.setItem('aetheria_token', data.token)
      setToken(data.token)
      setShowAuthModal(false)
      showToast('註冊成功！', 'success')
      setAuthForm({ email: '', password: '', display_name: '' })
    } catch (error) {
      // Error already shown by apiCall
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('aetheria_token')
    setToken('')
    setProfile(null)
    setChartLocked(false)
    setChartSummary(null)
    setCurrentView('home')
    showToast('已登出', 'info')
  }

  // ========== Profile & Chart ==========
  const fetchProfile = async () => {
    if (!token) return
    try {
      const data = await apiCall('/api/profile', null, 'GET')
      setProfile(data.profile)
      setBirthInfo(data.birth_info)
    } catch (error) {
      localStorage.removeItem('aetheria_token')
      setToken('')
    }
  }

  const checkChartLock = async () => {
    if (!profile) return
    try {
      const userId = profile.user_id
      const lockData = await apiCallSilent(`/api/chart/get-lock?user_id=${encodeURIComponent(userId)}`, null, 'GET')
      const reportsData = await apiCallSilent(`/api/reports/get?user_id=${encodeURIComponent(userId)}`, null, 'GET')

      if (!lockData || !lockData.locked) {
        setChartLocked(false)
        setChartSummary(null)
        return
      }

      const reports = reportsData?.reports || {}
      const available = reportsData?.available_systems || Object.keys(reports)
      const reportsGenerated = {}
      for (const key of available) reportsGenerated[key] = true

      setChartLocked(true)
      setChartSummary({
        reports_generated: reportsGenerated,
        generation_errors: {},
        available_systems: available,
        ziwei: lockData.chart_structure || null,
        bazi: reports.bazi?.report?.bazi_chart || null,
        numerology: reports.numerology?.report?.profile || null,
        name: reports.name?.report?.five_grids || reports.name?.report || null,
        astrology: reports.astrology?.report?.natal_chart || null
      })
    } catch (error) {
      // No chart locked yet
    }
  }

  const refreshAfterRegenerate = async (userId) => {
    await fetchProfile()
    const lockData = await apiCallSilent(`/api/chart/get-lock?user_id=${encodeURIComponent(userId)}`, null, 'GET')
    const reportsData = await apiCallSilent(`/api/reports/get?user_id=${encodeURIComponent(userId)}`, null, 'GET')

    if (!lockData || !lockData.locked) {
      setChartLocked(false)
      setChartSummary(null)
      return
    }

    const reports = reportsData?.reports || {}
    const available = reportsData?.available_systems || Object.keys(reports)
    const reportsGenerated = {}
    for (const key of available) reportsGenerated[key] = true

    setChartLocked(true)
    setChartSummary({
      reports_generated: reportsGenerated,
      generation_errors: {},
      available_systems: available,
      ziwei: lockData.chart_structure || null,
      bazi: reports.bazi?.report?.bazi_chart || null,
      numerology: reports.numerology?.report?.profile || null,
      name: reports.name?.report?.five_grids || reports.name?.report || null,
      astrology: reports.astrology?.report?.natal_chart || null
    })
  }

  useEffect(() => {
    fetchProfile()
  }, [token])

  useEffect(() => {
    if (profile) {
      checkChartLock()
    }
  }, [profile])

  useEffect(() => {
    if (currentView !== 'overview' || !chartLocked || !profile?.user_id || overviewData) return
    const payload = ensureChartPayload()
    if (!payload) {
      showToast('缺少出生資料，請重新建立命盤', 'error')
      return
    }

    let isActive = true
    setOverviewLoading(true)
    apiCall('/api/integrated/profile', {
      user_id: profile.user_id,
      ...payload
    })
      .then((data) => {
        if (!isActive) return
        setOverviewData(data)
        setChartAnalysis(data)
      })
      .catch(() => {
        if (isActive) showToast('載入失敗', 'error')
      })
      .finally(() => {
        if (isActive) setOverviewLoading(false)
      })

    return () => {
      isActive = false
    }
  }, [currentView, chartLocked, profile?.user_id, overviewData])

  useEffect(() => {
    if (currentView !== 'system-detail' || !currentSystem || !chartLocked || !profile?.user_id) return

    if (systemAnalysis[currentSystem]) {
      setSystemData(systemAnalysis[currentSystem])
      return
    }

    setSystemData(null)

    // 塔羅牌特殊處理（按需抽牌）
    if (currentSystem === 'tarot') {
      setSystemLoading(false)
      setSystemData(null)
      setTarotError('')
      return
    }

    let isActive = true
    setSystemLoading(true)

    const run = async () => {
      try {
        // 從已生成的報告中獲取資料
        const data = await apiCall(`/api/reports/get?user_id=${encodeURIComponent(profile.user_id)}&system=${currentSystem}`, null, 'GET')
        if (!isActive) return
        
        if (data.found) {
          setSystemData(data)
          setSystemAnalysis((prev) => ({ ...prev, [currentSystem]: data }))
        } else {
          showToast(`尚未生成${currentSystem}報告，請先建立命盤`, 'info')
        }
      } catch (error) {
        if (isActive) showToast(`載入${currentSystem}失敗`, 'error')
      } finally {
        if (isActive) setSystemLoading(false)
      }
    }

    run()

    return () => {
      isActive = false
    }
  }, [currentView, currentSystem, chartLocked, profile?.user_id, systemAnalysis])

  // ========== Chart Creation Wizard ==========
  const handleCreateChart = async () => {
    setLoading(true)
    try {
      // 使用新的 save-and-analyze API，一次生成五大系統報告
      // 如果沒有 profile，根據姓名和出生日期生成 user_id
      const userId = profile?.user_id || `${chartForm.chinese_name || 'user'}_${chartForm.birth_date?.replace(/-/g, '') || Date.now()}`
      
      const data = await apiCall('/api/profile/save-and-analyze', {
        user_id: userId,
        chinese_name: chartForm.chinese_name || '',
        gender: chartForm.gender,
        birth_date: chartForm.birth_date,
        birth_time: chartForm.birth_time,
        birth_location: chartForm.birth_location,
        ziwei_ruleset: chartForm.ziwei_ruleset
      })

      if (data.status !== 'success') {
        throw new Error(data.error || '分析失敗')
      }
      
      // 整合所有報告結果
      const summary = {
        reports_generated: data.reports_generated || {},
        generation_errors: data.generation_errors || {},
        available_systems: data.available_systems || [],
        // 各系統詳細資料
        ziwei: data.ziwei_structure || null,
        bazi: data.bazi_chart || null,
        numerology: data.numerology_profile || null,
        name: data.name_result || null,
        astrology: data.astrology_chart || null,
        // 保存 user_id 供後續使用
        user_id: userId
      }
      
      setChartSummary(summary)
      // 如果沒有 profile，創建一個臨時 profile
      if (!profile) {
        setProfile({
          user_id: userId,
          display_name: chartForm.chinese_name || '用戶'
        })
      }
      setWizardStep(5)
      
      // 顯示生成結果
      const successCount = Object.values(data.reports_generated || {}).filter(v => v).length
      const totalCount = Object.keys(data.reports_generated || {}).length
      if (successCount === totalCount) {
        showToast(`五大系統報告生成完成！(${successCount}/${totalCount})`, 'success')
      } else {
        showToast(`報告生成完成 (${successCount}/${totalCount})，部分系統失敗`, 'warning')
      }
    } catch (error) {
      console.error('命盤建立失敗:', error)
      showToast(error.message || '分析失敗', 'error')
      setWizardStep(3)
    } finally {
      setLoading(false)
    }
  }

  const _extractZiweiAsciiChart = (text) => {
    if (!text || typeof text !== 'string') return { cleaned: text || '', chart: '' }

    // 盡量只抓「命盤圖」那段（通常是 ```text ... ```），避免把前面的 JSON code block 也抓走。
    const textBlockRe = /```text\s*([\s\S]*?)```/m
    const match = text.match(textBlockRe)
    if (!match) return { cleaned: text, chart: '' }

    const chart = (match[1] || '').trim()
    let cleaned = text.replace(match[0], '').trim()

    // 如果有「【紫微鬥數命盤圖】」標題，也順便去掉，避免留下突兀空白。
    cleaned = cleaned.replace(/\n?\s*【紫微[鬥斗]數命盤圖】\s*\n?/g, '\n').trim()
    return { cleaned, chart }
  }

  const _normalizeEarthlyBranch = (value) => {
    const s = (value ?? '').toString().trim()
    if (!s) return ''
    const m = s.match(/[子丑寅卯辰巳午未申酉戌亥]/)
    return m ? m[0] : ''
  }

  const _getZiweiChartStructure = (data) => {
    if (!data) return null
    const direct = data.chart_structure
    if (direct && typeof direct === 'object') return direct

    const report = data.report
    if (report?.chart_structure && typeof report.chart_structure === 'object') return report.chart_structure

    // 向後相容：有些匯出/歷史格式會把 chart_structure 放在 report.wrapper 或 data.ziwei 等位置
    if (report?.report?.chart_structure && typeof report.report.chart_structure === 'object') return report.report.chart_structure
    if (data.ziwei?.chart_structure && typeof data.ziwei.chart_structure === 'object') return data.ziwei.chart_structure
    return null
  }

  const _buildZiweiBranchToPalace = (structure) => {
    const twelve = structure?.十二宮 && typeof structure.十二宮 === 'object' ? structure.十二宮 : null
    if (!twelve) return {}

    const map = {}
    for (const [palaceName, palaceData] of Object.entries(twelve)) {
      const branch = _normalizeEarthlyBranch(palaceData?.宮位 || palaceData?.地支 || '')
      if (!branch) continue
      map[branch] = { palaceName, palaceData }
    }
    return map
  }

  const _renderZiweiGrid = (structure) => {
    if (!structure) return null

    const branchToPalace = _buildZiweiBranchToPalace(structure)
    const patterns = Array.isArray(structure.格局) ? structure.格局 : []
    const five = structure.五行局 || structure.局 || ''
    const four = structure.四化 && typeof structure.四化 === 'object' ? structure.四化 : null

    const branchCells = [
      { branch: '巳', row: 1, col: 1 },
      { branch: '午', row: 1, col: 2 },
      { branch: '未', row: 1, col: 3 },
      { branch: '申', row: 1, col: 4 },
      { branch: '辰', row: 2, col: 1 },
      { branch: '酉', row: 2, col: 4 },
      { branch: '卯', row: 3, col: 1 },
      { branch: '戌', row: 3, col: 4 },
      { branch: '寅', row: 4, col: 1 },
      { branch: '丑', row: 4, col: 2 },
      { branch: '子', row: 4, col: 3 },
      { branch: '亥', row: 4, col: 4 }
    ]

    return (
      <div className="ziwei-chart-grid" aria-label="紫微斗數十二宮命盤">
        {/* 中央區塊 */}
        <div className="ziwei-chart-center" style={{ gridRow: '2 / span 2', gridColumn: '2 / span 2' }}>
          <div className="ziwei-center-title">紫微斗數命盤</div>
          <div className="ziwei-center-meta">
            {five && <div>五行局：{five}</div>}
            {patterns.length > 0 && <div>格局：{patterns.join('、')}</div>}
          </div>
          {four && (
            <div className="ziwei-center-si-hua">
              <div>四化：
                {['化祿', '化權', '化科', '化忌']
                  .filter((k) => four[k])
                  .map((k) => `${k}${four[k]}`)
                  .join('／') || '（無）'}
              </div>
            </div>
          )}
        </div>

        {branchCells.map(({ branch, row, col }) => {
          const slot = branchToPalace[branch]
          const palaceName = slot?.palaceName || ''
          const palaceData = slot?.palaceData || null
          const rawMainStars = Array.isArray(palaceData?.主星) ? palaceData.主星 : []
          // 過濾「(空宮)」並提取借星資訊
          const borrowedMatch = rawMainStars.find((s) => typeof s === 'string' && s.startsWith('借星:'))
          const borrowedStars = borrowedMatch ? borrowedMatch.replace('借星:', '').split(',').map((s) => s.trim()) : []
          const mainStars = rawMainStars.filter((s) => typeof s === 'string' && !s.startsWith('(空宮)') && !s.startsWith('借星:'))
          const isEmptyPalace = rawMainStars.some((s) => typeof s === 'string' && s.includes('空宮'))
          const assistStars = Array.isArray(palaceData?.輔星) ? palaceData.輔星 : []
          const isMing = palaceName === '命宮'
          return (
            <div
              key={branch}
              className={`ziwei-chart-cell ${isMing ? 'ziwei-chart-cell--ming' : ''}`}
              style={{ gridRow: row, gridColumn: col }}
            >
              <div className="ziwei-cell-head">
                <span className="ziwei-cell-branch">{branch}</span>
                <span className="ziwei-cell-palace">{palaceName || '（未標記）'}</span>
              </div>
              <div className="ziwei-cell-body">
                <div className="ziwei-stars">
                  <span className="ziwei-stars-label">主星</span>
                  <span className="ziwei-stars-value">
                    {mainStars.length > 0
                      ? mainStars.join('、')
                      : isEmptyPalace
                        ? <span style={{color: 'var(--color-text-muted)'}}>空宮</span>
                        : '（無主星）'}
                  </span>
                </div>
                {borrowedStars.length > 0 && (
                  <div className="ziwei-stars">
                    <span className="ziwei-stars-label">借星</span>
                    <span className="ziwei-stars-value" style={{color: 'var(--color-text-muted)'}}>{borrowedStars.join('、')}</span>
                  </div>
                )}
                {assistStars.length > 0 && (
                  <div className="ziwei-stars">
                    <span className="ziwei-stars-label">輔星</span>
                    <span className="ziwei-stars-value">{assistStars.join('、')}</span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  const handleConfirmLock = async () => {
    // 新流程不需要額外確認，save-and-analyze 已自動鎖定
    setChartLocked(true)
    setWizardStep(6)
    showToast('命盤已鎖定！', 'success')
  }

  const handleTarotReading = async () => {
    if (!tarotForm.spread_type) {
      showToast('請選擇牌陣', 'info')
      return
    }
    if (tarotForm.spread_type !== 'single' && !tarotForm.question.trim()) {
      showToast('請輸入問題', 'info')
      return
    }

    setTarotLoading(true)
    setTarotError('')
    try {
      const data = await apiCall('/api/tarot/reading', {
        spread_type: tarotForm.spread_type,
        question: tarotForm.question.trim() || '今日指引',
        context: tarotForm.context,
        allow_reversed: tarotForm.allow_reversed,
        fast_mode: !tarotForm.use_ai
      })
      if (data.status === 'success') {
        setTarotResult(data.data)
      } else {
        throw new Error(data.message || '塔羅解讀失敗')
      }
    } catch (error) {
      setTarotError(error.message || '塔羅解讀失敗')
    } finally {
      setTarotLoading(false)
    }
  }

  const handleTarotDaily = async () => {
    setTarotLoading(true)
    setTarotError('')
    try {
      const data = await apiCall('/api/tarot/reading', {
        spread_type: 'single',
        question: '今日指引',
        context: 'general',
        allow_reversed: true,
        fast_mode: !tarotForm.use_ai
      })
      if (data.status === 'success') {
        setTarotResult(data.data)
      } else {
        throw new Error(data.message || '每日一牌失敗')
      }
    } catch (error) {
      setTarotError(error.message || '每日一牌失敗')
    } finally {
      setTarotLoading(false)
    }
  }

  const handleAstrologyTransit = async () => {
    const parts = getBirthParts()
    if (!parts) {
      showToast('缺少出生資料，請先建立命盤', 'error')
      return
    }
    if (!astrologyTransitDate) {
      showToast('請選擇流年日期', 'info')
      return
    }

    setAstrologyLoading(true)
    setAstrologyError('')
    try {
      const data = await apiCall('/api/astrology/transit', {
        name: profile?.display_name || chartForm.chinese_name || '用戶',
        year: parts.year,
        month: parts.month,
        day: parts.day,
        hour: parts.hour,
        minute: parts.minute,
        city: parts.birth_location || '台灣',
        transit_date: astrologyTransitDate
      })

      if (data.status === 'success') {
        setAstrologyResult(data.data)
      } else {
        throw new Error(data.message || '流年分析失敗')
      }
    } catch (error) {
      setAstrologyError(error.message || '流年分析失敗')
    } finally {
      setAstrologyLoading(false)
    }
  }

  // ========== Render Functions ==========
  
  // Landing Page (未登入)
  const renderLanding = () => (
    <div className="landing">
      <div className="landing-header">
        <div className="landing-brand">
          <div className="landing-logo">A</div>
          <div>
            <div className="landing-title">Aetheria</div>
            <div className="landing-subtitle">超個人化命理分析系統</div>
          </div>
        </div>
        <div className="landing-actions">
          <button 
            className="btn btn-ghost" 
            onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
          >
            登入
          </button>
          <button 
            className="btn btn-primary" 
            onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
          >
            開始使用
          </button>
        </div>
      </div>

      <div className="landing-hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span>✨</span>
            <span>v1.9.0 戰略側寫系統上線</span>
          </div>
          <h1 className="hero-title">
            從算命到戰略<br />AI 命理決策顧問
          </h1>
          <p className="hero-description">
            整合六大命理系統，結合 Gemini AI 深度推理，
            提供結論優先、證據充足、可執行的戰略建議
          </p>
          <div className="hero-cta">
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => { setAuthMode('register'); setShowAuthModal(true); }}
            >
              免費開始分析
            </button>
            <button className="btn btn-secondary btn-lg">
              了解更多
            </button>
          </div>
        </div>
      </div>

      <div className="landing-features">
        <h2 className="features-title">六大命理系統 + 戰略側寫</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔮</div>
            <div className="feature-title">紫微斗數</div>
            <div className="feature-desc">
              LLM-First 排盤，深度格局分析，流年運勢預測
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">☯️</div>
            <div className="feature-title">八字命理</div>
            <div className="feature-desc">
              四柱排盤，十神分析，大運流年推算
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⭐</div>
            <div className="feature-title">西洋占星術</div>
            <div className="feature-desc">
              Swiss Ephemeris 專業星曆，本命盤合盤分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔢</div>
            <div className="feature-title">靈數學</div>
            <div className="feature-desc">
              生命靈數，天賦潛能，流年週期分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <div className="feature-title">姓名學</div>
            <div className="feature-desc">
              五格剖象法，81數理，三才配置分析
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎴</div>
            <div className="feature-title">塔羅牌</div>
            <div className="feature-desc">
              多種牌陣，每日一牌，情境解讀指引
            </div>
          </div>
          {/* 戰略側寫特色卡已隱藏 */}
          {/* <div className="feature-card" style={{gridColumn: 'span 2', background: 'var(--color-strategic-bg)', borderColor: 'var(--color-strategic)'}}>
            <div className="feature-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
            <div className="feature-title" style={{color: 'var(--color-strategic)'}}>
              ✨ 戰略側寫系統
            </div>
            <div className="feature-desc">
              全息圖譜、生辰校正、關係生態位、決策沙盒 - 四大戰略工具，
              從被動算命升級為主動決策支援
            </div>
          </div> */}
        </div>
      </div>
    </div>
  )

  // Dashboard Home (已登入首頁)
  const renderDashboardHome = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">歡迎回來，{profile?.display_name || '用戶'}</h1>
        <p className="content-subtitle">
          {chartLocked 
            ? '您的命盤已鎖定，可以開始使用各項分析功能'
            : '請先建立並鎖定您的命盤'}
        </p>
      </div>
      <div className="content-body">
        {!chartLocked ? (
          <div className="card">
            <div className="card-header">
              <div className="card-title">🔮 建立您的專屬命盤</div>
              <div className="card-subtitle">
                命盤是所有分析的基礎，建立後將永久鎖定，確保一致性
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-primary"
                onClick={() => setCurrentView('chart')}
              >
                開始建立命盤
              </button>
            </div>
          </div>
        ) : (
          <div className="dashboard-grid">
            <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-primary)'}}>🔮</div>
              <div className="stat-content">
                <div className="stat-value">已鎖定</div>
                <div className="stat-label">命盤狀態</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-accent)'}}>📊</div>
              <div className="stat-content">
                <div className="stat-value">6 + 1</div>
                <div className="stat-label">可用系統</div>
              </div>
            </div>
            {/* 戰略側寫統計已隱藏 */}
            {/* <div className="stat-card">
              <div className="stat-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
              <div className="stat-content">
                <div className="stat-value">戰略版</div>
                <div className="stat-label">進階功能</div>
              </div>
            </div> */}
          </div>
        )}

        <div style={{marginTop: 'var(--spacing-2xl)'}}>
          <h2 style={{fontSize: '24px', fontWeight: 700, marginBottom: 'var(--spacing-lg)'}}>
            快速開始
          </h2>
          <div className="dashboard-grid">
            {/* AI 命理顧問 - 主要入口 */}
            <div 
              className="card" 
              style={{cursor: 'pointer', borderColor: 'var(--color-accent)', borderWidth: '2px'}}
              onClick={() => setShowVoiceChat(true)}
            >
              <div className="card-header">
                <div className="card-title" style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  🔮 AI 命理顧問
                  <span style={{background: 'var(--color-accent)', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '12px'}}>NEW</span>
                </div>
              </div>
              <div className="card-body">
                支援語音與文字對話，整合五大命理系統，有所本的 AI 諮詢
              </div>
            </div>
            <div 
              className="card" 
              style={{cursor: 'pointer'}}
              onClick={() => setCurrentView('systems')}
            >
              <div className="card-header">
                <div className="card-title">📚 六大命理系統</div>
              </div>
              <div className="card-body">
                紫微斗數、八字命理、西洋占星術、靈數學、姓名學、塔羅牌
              </div>
            </div>
            {/* 戰略側寫已隱藏 - AI 諮詢可完全取代 */}
            {/* <div 
              className="card card-strategic" 
              style={{cursor: 'pointer'}}
              onClick={() => setCurrentView('strategic')}
            >
              <div className="card-header">
                <div className="card-title" style={{color: 'var(--color-strategic)'}}>
                  🎯 戰略側寫系統
                </div>
              </div>
              <div className="card-body">
                全息圖譜、生辰校正、關係生態位、決策沙盒
              </div>
            </div> */}
          </div>
        </div>
      </div>
    </>
  )

  // Chart Creation View
  const renderChartView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">建立專屬命盤</h1>
        <p className="content-subtitle">請按照步驟填寫完整的出生資料</p>
      </div>
      <div className="content-body">
        {/* Wizard Progress */}
        <div className="progress-wizard">
          {[
            { step: 1, label: '基本資料' },
            { step: 2, label: '出生資訊' },
            { step: 3, label: '確認資料' },
            { step: 4, label: '分析中' },
            { step: 5, label: '預覽結果' },
            { step: 6, label: '完成' }
          ].map(item => (
            <div 
              key={item.step}
              className={`wizard-step ${wizardStep === item.step ? 'active' : ''} ${wizardStep > item.step ? 'completed' : ''}`}
            >
              <div className="wizard-circle">
                {wizardStep > item.step ? '✓' : item.step}
              </div>
              <div className="wizard-label">{item.label}</div>
            </div>
          ))}
        </div>

        {/* Step 1: Basic Info */}
        {wizardStep === 1 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 1：基本資料</div>
              <div className="card-subtitle">請提供您的姓名與性別</div>
            </div>
            <div className="card-body">
              <div className="form-group">
                <label className="form-label">中文姓名</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.chinese_name}
                  onChange={(e) => setChartForm({...chartForm, chinese_name: e.target.value})}
                  placeholder="例：張小明"
                />
              </div>
              <div className="form-group">
                <label className="form-label">英文姓名（選填，用於靈數學分析）</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.english_name}
                  onChange={(e) => setChartForm({...chartForm, english_name: e.target.value})}
                  placeholder="例：ZHANG XIAO MING"
                />
              </div>
              <div className="form-group">
                <label className="form-label">性別</label>
                <select 
                  className="form-select"
                  value={chartForm.gender}
                  onChange={(e) => setChartForm({...chartForm, gender: e.target.value})}
                >
                  <option value="男">男</option>
                  <option value="女">女</option>
                  <option value="未指定">未指定</option>
                </select>
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-primary"
                onClick={() => setWizardStep(2)}
                disabled={!chartForm.chinese_name}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Birth Info */}
        {wizardStep === 2 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 2：出生資訊</div>
              <div className="card-subtitle">請提供準確的出生日期、時間與地點</div>
            </div>
            <div className="card-body">
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">出生日期</label>
                  <input 
                    type="date"
                    className="form-input"
                    value={chartForm.birth_date}
                    onChange={(e) => setChartForm({...chartForm, birth_date: e.target.value})}
                  />
                  <div className="form-hint">請使用國曆日期</div>
                </div>
                <div className="form-group">
                  <label className="form-label">出生時間</label>
                  <input 
                    type="time"
                    className="form-input"
                    value={chartForm.birth_time}
                    onChange={(e) => setChartForm({...chartForm, birth_time: e.target.value})}
                  />
                  <div className="form-hint">請盡可能提供準確時間</div>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">紫微晚子時換日規則</label>
                <select
                  className="form-select"
                  value={chartForm.ziwei_ruleset}
                  onChange={(e) => setChartForm({...chartForm, ziwei_ruleset: e.target.value})}
                >
                  <option value="no_day_advance">日不進位（23:00-00:00 仍以當日排盤）</option>
                  <option value="day_advance">日進位（晚子時視為隔日排盤）</option>
                </select>
                <div className="form-hint">建議：除非你明確採用其他門派，通常選「日不進位」</div>
              </div>

              <div className="form-group">
                <label className="form-label">出生地點</label>
                <input 
                  type="text"
                  className="form-input"
                  value={chartForm.birth_location}
                  onChange={(e) => setChartForm({...chartForm, birth_location: e.target.value})}
                  placeholder="例：台灣台北市"
                />
                <div className="form-hint">用於計算經緯度與時區</div>
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => setWizardStep(1)}
              >
                上一步
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setWizardStep(3)}
                disabled={!chartForm.birth_date || !chartForm.birth_time || !chartForm.birth_location}
              >
                下一步
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirmation */}
        {wizardStep === 3 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 3：確認資料</div>
              <div className="card-subtitle">請仔細核對資料無誤後送出</div>
            </div>
            <div className="card-body">
              <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                <div><strong>姓名：</strong>{chartForm.chinese_name}</div>
                {chartForm.english_name && <div><strong>英文名：</strong>{chartForm.english_name}</div>}
                <div><strong>性別：</strong>{chartForm.gender}</div>
                <div><strong>出生日期：</strong>{chartForm.birth_date}</div>
                <div><strong>出生時間：</strong>{chartForm.birth_time}</div>
                <div>
                  <strong>紫微晚子時換日規則：</strong>
                  {chartForm.ziwei_ruleset === 'day_advance' ? '日進位（晚子時視為隔日）' : '日不進位（晚子時仍以當日）'}
                </div>
                <div><strong>出生地點：</strong>{chartForm.birth_location}</div>
              </div>
              <div style={{marginTop: 'var(--spacing-lg)', padding: 'var(--spacing-md)', background: 'var(--color-warning)', opacity: 0.1, borderRadius: 'var(--radius-md)', color: 'var(--color-text)'}}>
                ⚠️ 命盤一旦鎖定後無法修改，請確保資料正確
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => setWizardStep(2)}
              >
                上一步
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setWizardStep(4)
                  handleCreateChart()
                }}
                disabled={loading}
              >
                {loading ? '分析中...' : '開始分析'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Loading */}
        {wizardStep === 4 && (
          <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
            <div style={{textAlign: 'center'}}>
              <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
              <div style={{fontSize: '18px', fontWeight: 600, marginBottom: 'var(--spacing-sm)'}}>
                AI 正在分析您的命盤...
              </div>
              <div style={{color: 'var(--color-text-muted)'}}>
                這可能需要 30-60 秒
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Preview - 五大系統報告總攬 */}
        {wizardStep === 5 && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">步驟 5：五大系統報告總攬</div>
              <div className="card-subtitle">{chartSummary ? '您的專屬命盤已生成，請確認資訊無誤' : '命盤生成中...'}</div>
            </div>
            <div className="card-body">
              {!chartSummary ? (
                <div style={{textAlign: 'center', padding: 'var(--spacing-2xl)'}}>
                  <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                  <div>正在處理命盤資料...</div>
                </div>
              ) : (
                <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
                  {/* 生成狀態總覽 */}
                  <div style={{padding: 'var(--spacing-md)', background: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)'}}>
                    <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-md)'}}>📊 報告生成狀態</div>
                    <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)'}}>
                      {[
                        { key: 'ziwei', name: '紫微斗數', icon: '🔮' },
                        { key: 'bazi', name: '八字命理', icon: '☯️' },
                        { key: 'astrology', name: '西洋占星', icon: '⭐' },
                        { key: 'numerology', name: '靈數學', icon: '🔢' },
                        { key: 'name', name: '姓名學', icon: '📝' }
                      ].map(sys => {
                        const generated = chartSummary.reports_generated?.[sys.key]
                        const error = chartSummary.generation_errors?.[sys.key]
                        return (
                          <div key={sys.key} style={{
                            padding: '8px 12px',
                            borderRadius: '20px',
                            background: generated ? 'var(--color-success)' : error ? 'var(--color-error)' : 'var(--color-text-muted)',
                            color: 'white',
                            fontSize: '14px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                          }}>
                            <span>{sys.icon}</span>
                            <span>{sys.name}</span>
                            <span>{generated ? '✓' : error ? '✗' : '—'}</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  {/* 紫微斗數 - 完整命盤 */}
                  {chartSummary.reports_generated?.ziwei && chartSummary.ziwei && (
                    <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                      <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>🔮 紫微斗數命盤</div>
                      
                      {/* 基本資訊 */}
                      <div style={{display: 'grid', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)'}}>
                        <div><strong>命宮：</strong>{chartSummary.ziwei?.命宮?.宮位 || chartSummary.ziwei?.命宮?.地支 || ''}宮 - {chartSummary.ziwei?.命宮?.主星?.join('、') || '命無正曜'}{chartSummary.ziwei?.命宮?.輔星?.length > 0 ? ` (${chartSummary.ziwei.命宮.輔星.join('、')})` : ''}</div>
                        {chartSummary.ziwei?.身宮 && <div><strong>身宮：</strong>{chartSummary.ziwei.身宮?.宮位 || chartSummary.ziwei.身宮?.地支 || ''}宮 - {chartSummary.ziwei.身宮?.主星?.join('、') || ''}</div>}
                        {chartSummary.ziwei?.格局 && chartSummary.ziwei.格局.length > 0 && chartSummary.ziwei.格局[0] !== '未明確提及' && <div><strong>格局：</strong>{chartSummary.ziwei.格局.join('、')}</div>}
                        {chartSummary.ziwei?.五行局 && <div><strong>五行局：</strong>{chartSummary.ziwei.五行局}</div>}
                        {chartSummary.ziwei?.命主 && <div><strong>命主：</strong>{chartSummary.ziwei.命主}</div>}
                        {chartSummary.ziwei?.身主 && <div><strong>身主：</strong>{chartSummary.ziwei.身主}</div>}
                      </div>
                      
                      {/* 四化 */}
                      {chartSummary.ziwei?.四化 && (
                        <div style={{marginBottom: 'var(--spacing-md)', padding: 'var(--spacing-sm)', background: 'var(--color-bg-primary)', borderRadius: 'var(--radius-sm)'}}>
                          <div style={{fontWeight: 600, marginBottom: 'var(--spacing-xs)', color: 'var(--color-text-secondary)'}}>四化星</div>
                          <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)'}}>
                            {chartSummary.ziwei.四化.化祿 && <span style={{padding: '2px 8px', background: '#4ade80', color: '#000', borderRadius: '4px', fontSize: '13px'}}>祿: {chartSummary.ziwei.四化.化祿}</span>}
                            {chartSummary.ziwei.四化.化權 && <span style={{padding: '2px 8px', background: '#f97316', color: '#fff', borderRadius: '4px', fontSize: '13px'}}>權: {chartSummary.ziwei.四化.化權}</span>}
                            {chartSummary.ziwei.四化.化科 && <span style={{padding: '2px 8px', background: '#3b82f6', color: '#fff', borderRadius: '4px', fontSize: '13px'}}>科: {chartSummary.ziwei.四化.化科}</span>}
                            {chartSummary.ziwei.四化.化忌 && <span style={{padding: '2px 8px', background: '#ef4444', color: '#fff', borderRadius: '4px', fontSize: '13px'}}>忌: {chartSummary.ziwei.四化.化忌}</span>}
                          </div>
                        </div>
                      )}
                      
                      {/* 十二宮完整顯示 */}
                      {chartSummary.ziwei?.十二宮 && (
                        <div>
                          <div style={{fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-text-secondary)'}}>十二宮配置</div>
                          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 'var(--spacing-sm)'}}>
                            {['命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮', '遷移宮', '交友宮', '官祿宮', '田宅宮', '福德宮', '父母宮'].map(palace => {
                              const info = chartSummary.ziwei.十二宮[palace]
                              if (!info) return null
                              const stars = info.主星?.join('、') || '空宮'
                              const position = info.宮位 || info.地支 || ''
                              const sihua = info.四化 || ''
                              return (
                                <div key={palace} style={{
                                  padding: 'var(--spacing-sm)',
                                  background: palace === '命宮' ? 'var(--color-primary-alpha)' : 'var(--color-bg-primary)',
                                  borderRadius: 'var(--radius-sm)',
                                  border: palace === '命宮' ? '2px solid var(--color-primary)' : '1px solid var(--color-border)'
                                }}>
                                  <div style={{fontWeight: 600, fontSize: '13px', color: palace === '命宮' ? 'var(--color-primary)' : 'var(--color-text-primary)'}}>{palace} {position && `(${position})`}</div>
                                  <div style={{fontSize: '12px', color: 'var(--color-text-secondary)'}}>{stars}</div>
                                  {sihua && <div style={{fontSize: '11px', color: 'var(--color-accent)', marginTop: '2px'}}>{sihua}</div>}
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* 八字命理 */}
                  {chartSummary.reports_generated?.bazi && chartSummary.bazi && (
                    <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                      <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>☯️ 八字命理</div>
                      <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                        <div>
                          <strong>四柱：</strong>
                          {(() => {
                            const bazi = chartSummary.bazi
                            const p = bazi?.pillars
                            if (p?.year?.full || p?.month?.full || p?.day?.full || p?.hour?.full) {
                              return `${p?.year?.full || ''} ${p?.month?.full || ''} ${p?.day?.full || ''} ${p?.hour?.full || ''}`.trim()
                            }
                            const four = bazi?.四柱 || bazi?.['四柱']
                            const y = four?.年柱
                            const m = four?.月柱
                            const d = four?.日柱
                            const h = four?.時柱 || four?.时柱
                            const fmt = (x) => (x?.天干 && x?.地支 ? `${x.天干}${x.地支}` : '')
                            const txt = `${fmt(y)} ${fmt(m)} ${fmt(d)} ${fmt(h)}`.trim()
                            return txt || '（四柱資料已生成，但摘要格式未對齊；請至八字報告查看）'
                          })()}
                        </div>
                        {(() => {
                          const bazi = chartSummary.bazi
                          const dayMaster = bazi?.day_master || bazi?.日主?.天干 || bazi?.['日主']?.天干
                          const dayMasterWx = bazi?.日主?.五行 || bazi?.['日主']?.五行
                          if (!dayMaster && !dayMasterWx) return null
                          return <div><strong>日主：</strong>{dayMaster || ''}{dayMasterWx ? `（${dayMasterWx}）` : ''}</div>
                        })()}
                        {(() => {
                          const bazi = chartSummary.bazi
                          const strength = bazi?.day_master_strength || bazi?.强弱?.结论 || bazi?.強弱?.结论 || bazi?.['强弱']?.结论 || bazi?.['強弱']?.结论
                          return strength ? <div><strong>身強/弱：</strong>{strength}</div> : null
                        })()}
                      </div>
                    </div>
                  )}
                  
                  {/* 西洋占星 */}
                  {chartSummary.reports_generated?.astrology && chartSummary.astrology && (
                    <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                      <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>⭐ 西洋占星</div>
                      <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                        {(() => {
                          const a = chartSummary.astrology
                          const planets = a?.planets
                          const sun = a?.sun_sign || a?.sun?.sign_zh || a?.sun?.sign || planets?.sun?.sign_zh || planets?.sun?.sign
                          const moon = a?.moon_sign || a?.moon?.sign_zh || a?.moon?.sign || planets?.moon?.sign_zh || planets?.moon?.sign
                          const asc = a?.ascendant || a?.ascendant?.sign_zh || a?.ascendant?.sign || planets?.ascendant?.sign_zh || planets?.ascendant?.sign
                          return (
                            <>
                              {sun && <div><strong>太陽星座：</strong>{sun}</div>}
                              {moon && <div><strong>月亮星座：</strong>{moon}</div>}
                              {asc && <div><strong>上升星座：</strong>{asc}</div>}
                              {!sun && !moon && !asc && <div style={{color: 'var(--color-text-secondary)'}}>（已生成占星資料，但摘要欄位不足；請至占星報告查看）</div>}
                            </>
                          )
                        })()}
                      </div>
                    </div>
                  )}
                  
                  {/* 靈數學 */}
                  {chartSummary.reports_generated?.numerology && chartSummary.numerology && (
                    <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                      <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>🔢 靈數學</div>
                      <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                        {(() => {
                          const n = chartSummary.numerology
                          const lifePath = n?.life_path_number ?? n?.core_numbers?.life_path?.number
                          const expression = n?.expression_number ?? n?.core_numbers?.expression?.number
                          const soulUrge = n?.soul_urge_number ?? n?.core_numbers?.soul_urge?.number
                          return (
                            <>
                              {lifePath != null && <div><strong>生命靈數：</strong>{lifePath}</div>}
                              {expression != null && <div><strong>表達數：</strong>{expression}</div>}
                              {soulUrge != null && <div><strong>靈魂渴望數：</strong>{soulUrge}</div>}
                              {lifePath == null && expression == null && soulUrge == null && <div style={{color: 'var(--color-text-secondary)'}}>（已生成靈數資料，但摘要欄位不足；請至靈數報告查看）</div>}
                            </>
                          )
                        })()}
                      </div>
                    </div>
                  )}
                  
                  {/* 姓名學 */}
                  {chartSummary.reports_generated?.name && chartSummary.name && (
                    <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                      <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>📝 姓名學</div>
                      <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                        {(() => {
                          const x = chartSummary.name
                          const displayName = x?.name || x?.name_info?.full_name || x?.five_grids?.name_info?.full_name
                          const totalStrokes = x?.total_strokes ?? x?.name_info?.total_strokes ?? x?.five_grids?.name_info?.total_strokes
                          const fiveGrids = x?.five_grids?.five_grids || x?.five_grids || x?.grid_analyses?.five_grids

                          const getFiveGridsText = () => {
                            if (!fiveGrids || typeof fiveGrids !== 'object') return null
                            const t = fiveGrids?.天格
                            const r = fiveGrids?.人格
                            const d = fiveGrids?.地格
                            const w = fiveGrids?.外格
                            const z = fiveGrids?.總格
                            if ([t, r, d, w, z].every(v => v == null)) return null
                            return `天${t ?? '—'}／人${r ?? '—'}／地${d ?? '—'}／外${w ?? '—'}／總${z ?? '—'}`
                          }

                          const gridsText = getFiveGridsText()

                          return (
                            <>
                              {displayName && <div><strong>姓名：</strong>{displayName}</div>}
                              {totalStrokes != null && <div><strong>總筆劃：</strong>{totalStrokes}</div>}
                              {gridsText && <div><strong>五格：</strong>{gridsText}</div>}
                              {!displayName && totalStrokes == null && !gridsText && <div style={{color: 'var(--color-text-secondary)'}}>（已生成姓名資料，但摘要欄位不足；請至姓名報告查看）</div>}
                            </>
                          )
                        })()}
                      </div>
                    </div>
                  )}
                  
                  {/* 塔羅牌提示 */}
                  <div style={{padding: 'var(--spacing-md)', background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent))', borderRadius: 'var(--radius-md)', color: 'white'}}>
                    <div>🎴 <strong>塔羅牌</strong>隨時可用，無需事先設定！點擊「六大系統」即可抽牌</div>
                  </div>
                </div>
              )}
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-ghost"
                onClick={() => {
                  setWizardStep(1)
                  setChartSummary(null)
                }}
              >
                重新建立
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleConfirmLock}
                disabled={loading}
              >
                確認完成
              </button>
            </div>
          </div>
        )}

        {/* Step 6: Complete */}
        {wizardStep === 6 && (
          <div className="card" style={{textAlign: 'center', padding: 'var(--spacing-3xl)'}}>
            <div style={{fontSize: '64px', marginBottom: 'var(--spacing-lg)'}}>✨</div>
            <div style={{fontSize: '28px', fontWeight: 700, marginBottom: 'var(--spacing-md)'}}>
              命盤建立完成！
            </div>
            <div style={{color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-2xl)'}}>
              您現在可以使用所有分析功能了
            </div>
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => setCurrentView('home')}
            >
              開始探索
            </button>
          </div>
        )}
      </div>
    </>
  )

  // Systems View
  const renderSystemsView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">六大命理系統</h1>
        <p className="content-subtitle">選擇您想使用的分析系統</p>
      </div>
      <div className="content-body">
        <div className="dashboard-grid">
          {[
            { id: 'ziwei', icon: '🔮', name: '紫微斗數', desc: 'LLM-First 排盤與格局分析' },
            { id: 'bazi', icon: '☯️', name: '八字命理', desc: '四柱排盤與十神分析' },
            { id: 'astrology', icon: '⭐', name: '西洋占星術', desc: '本命盤與合盤分析' },
            { id: 'numerology', icon: '🔢', name: '靈數學', desc: '生命靈數與天賦分析' },
            { id: 'name', icon: '📝', name: '姓名學', desc: '五格剖象法分析' },
            { id: 'tarot', icon: '🎴', name: '塔羅牌', desc: '牌陣占卜與指引' }
          ].map(system => (
            <div 
              key={system.id}
              className="card"
              style={{cursor: 'pointer'}}
              onClick={() => {
                if (!chartLocked) {
                  showToast('請先建立並鎖定命盤', 'warning')
                  return
                }
                setCurrentSystem(system.id)
                setCurrentView('system-detail')
              }}
            >
              <div style={{fontSize: '48px', marginBottom: 'var(--spacing-md)'}}>{system.icon}</div>
              <div className="card-title">{system.name}</div>
              <div className="card-body">{system.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )

  // Strategic View
  const renderStrategicView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title" style={{color: 'var(--color-strategic)'}}>
          🎯 戰略側寫系統
        </h1>
        <p className="content-subtitle">從算命到戰略 - 四大決策工具</p>
      </div>
      <div className="content-body">
        <div className="dashboard-grid">
          {[
            { 
              id: 'profile', 
              icon: '🌐', 
              name: '全息生命圖譜', 
              desc: 'Meta Profile 整合，結論優先架構，資源流向分析' 
            },
            { 
              id: 'rectify', 
              icon: '🕐', 
              name: '生辰校正器', 
              desc: '反推時辰邏輯，多系統驗證，Top 3 可能性' 
            },
            { 
              id: 'ecosystem', 
              icon: '🤝', 
              name: '關係生態位', 
              desc: '資源流動分析，功能互補評估，合作風險與紅利' 
            },
            { 
              id: 'decision', 
              icon: '⚖️', 
              name: '決策沙盒', 
              desc: '雙路徑模擬，因果推演，代價收益分析' 
            }
          ].map(tool => (
            <div 
              key={tool.id}
              className="card card-strategic"
              style={{cursor: 'pointer'}}
              onClick={() => showToast(`${tool.name} 功能開發中`, 'info')}
            >
              <div style={{fontSize: '48px', marginBottom: 'var(--spacing-md)'}}>{tool.icon}</div>
              <div className="card-title" style={{color: 'var(--color-strategic)'}}>{tool.name}</div>
              <div className="card-body">{tool.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )

  // Overview View (我的命盤總攬)
  const renderOverviewView = () => (
      <>
        <div className="content-header">
          <h1 className="content-title">我的命盤總攬</h1>
          <p className="content-subtitle">綜合六大系統的完整分析</p>
        </div>
        <div className="content-body">
          {overviewLoading ? (
            <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                <div>正在載入您的命盤分析...</div>
              </div>
            </div>
          ) : overviewData ? (
            <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
              <div className="card">
                <div className="card-header">
                  <div className="card-title">📊 綜合分析</div>
                </div>
                <div 
                  className="card-body" 
                  style={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
                  }}
                >
                  {overviewData.analysis || overviewData.summary || '分析資料載入中...'}
                </div>
              </div>
              
              <div className="dashboard-grid">
                {[
                  { id: 'ziwei', icon: '🔮', name: '紫微斗數' },
                  { id: 'bazi', icon: '☯️', name: '八字命理' },
                  { id: 'astrology', icon: '⭐', name: '西洋占星' },
                  { id: 'numerology', icon: '🔢', name: '靈數學' },
                  { id: 'name', icon: '📝', name: '姓名學' },
                  { id: 'tarot', icon: '🎴', name: '塔羅牌' }
                ].map(system => (
                  <div 
                    key={system.id}
                    className="card"
                    style={{cursor: 'pointer'}}
                    onClick={() => {
                      setCurrentSystem(system.id)
                      setCurrentView('system-detail')
                    }}
                  >
                    <div className="card-header">
                      <div className="card-title">{system.icon} {system.name}</div>
                    </div>
                    <div className="card-footer">
                      <button className="btn btn-ghost">查看詳細</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="card-body">尚無分析資料</div>
            </div>
          )}
        </div>
      </>
    )

  // System Detail View (單一系統詳細分析)
  const renderSystemDetailView = () => {
    const getSystemInfo = (id) => {
      const systems = {
        ziwei: { icon: '🔮', name: '紫微斗數' },
        bazi: { icon: '☯️', name: '八字命理' },
        astrology: { icon: '⭐', name: '西洋占星術' },
        numerology: { icon: '🔢', name: '靈數學' },
        name: { icon: '📝', name: '姓名學' },
        tarot: { icon: '🎴', name: '塔羅牌' }
      }
      return systems[id] || { icon: '❓', name: '未知系統' }
    }

    const systemInfo = getSystemInfo(currentSystem)

    return (
      <>
        <div className="content-header">
          <button 
            className="btn btn-ghost" 
            onClick={() => setCurrentView('systems')}
            style={{marginBottom: 'var(--spacing-md)'}}
          >
            ← 返回
          </button>
          <h1 className="content-title">{systemInfo.icon} {systemInfo.name}</h1>
          <p className="content-subtitle">詳細分析報告</p>
        </div>
        <div className="content-body">
          {currentSystem === 'tarot' ? (
            <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
              <div className="card">
                <div className="card-header">
                  <div className="card-title">🎴 塔羅牌抽牌設定</div>
                </div>
                <div className="card-body" style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                  <div className="form-group">
                    <label className="form-label">牌陣</label>
                    <select
                      className="form-input"
                      value={tarotForm.spread_type}
                      onChange={(e) => setTarotForm({ ...tarotForm, spread_type: e.target.value })}
                    >
                      <option value="single">單張牌</option>
                      <option value="three_card">三張牌（過去-現在-未來）</option>
                      <option value="celtic_cross">賽爾特十字</option>
                      <option value="relationship">關係牌陣</option>
                      <option value="decision">決策牌陣</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">問題情境</label>
                    <select
                      className="form-input"
                      value={tarotForm.context}
                      onChange={(e) => setTarotForm({ ...tarotForm, context: e.target.value })}
                    >
                      <option value="general">一般</option>
                      <option value="love">感情</option>
                      <option value="career">事業</option>
                      <option value="finance">財務</option>
                      <option value="health">健康</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">問題（可留空為今日指引）</label>
                    <input
                      className="form-input"
                      type="text"
                      value={tarotForm.question}
                      onChange={(e) => setTarotForm({ ...tarotForm, question: e.target.value })}
                      placeholder="例如：我該不該換工作？"
                    />
                  </div>
                  <div className="form-group" style={{display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)'}}>
                    <input
                      type="checkbox"
                      checked={tarotForm.allow_reversed}
                      onChange={(e) => setTarotForm({ ...tarotForm, allow_reversed: e.target.checked })}
                    />
                    <label className="form-label" style={{margin: 0}}>允許逆位</label>
                  </div>
                  <div className="form-group" style={{display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)'}}>
                    <input
                      type="checkbox"
                      checked={tarotForm.use_ai}
                      onChange={(e) => setTarotForm({ ...tarotForm, use_ai: e.target.checked })}
                    />
                    <label className="form-label" style={{margin: 0}}>使用 AI 深度解讀（較慢）</label>
                  </div>
                  <div style={{display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap'}}>
                    <button className="btn btn-primary" onClick={handleTarotReading} disabled={tarotLoading}>
                      {tarotLoading ? '抽牌中...' : '抽牌解讀'}
                    </button>
                    <button className="btn btn-ghost" onClick={handleTarotDaily} disabled={tarotLoading}>
                      今日一牌
                    </button>
                  </div>
                  {tarotError && (
                    <div style={{color: 'var(--color-danger)'}}>{tarotError}</div>
                  )}
                </div>
              </div>

              {tarotResult && (
                <div className="card">
                  <div className="card-header">
                    <div className="card-title">🧭 抽牌結果</div>
                    <div className="card-subtitle">
                      {tarotResult.spread_name || '塔羅牌解讀'}
                      {tarotResult.question ? `｜${tarotResult.question}` : ''}
                    </div>
                  </div>
                  <div className="card-body" style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
                    <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                      {tarotResult.cards?.map((card, index) => {
                        const imageUrl = getTarotImageUrl(card)
                        const expectedFilename = getTarotImageFilename(card)
                        const orientation = card.is_reversed ? '逆位' : '正位'
                        return (
                          <div key={`${card.reading_id || 'card'}-${index}`} style={{display: 'grid', gridTemplateColumns: '120px 1fr', gap: 'var(--spacing-md)', alignItems: 'start'}}>
                            <div style={{width: '120px'}}>
                              <TarotCardImage imageUrl={imageUrl} alt={card.name} expectedFilename={expectedFilename} />
                            </div>
                            <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                              <div style={{fontWeight: 600}}>
                                {card.position_index + 1}. {card.position}｜{card.name}（{orientation}）
                              </div>
                              {card.name_en && <div style={{color: 'var(--color-text-muted)'}}>{card.name_en}</div>}
                              {card.meaning?.keywords?.length > 0 && (
                                <div>關鍵詞：{card.meaning.keywords.join('、')}</div>
                              )}
                              {card.meaning?.meaning && (
                                <div>牌義：{card.meaning.meaning}</div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {tarotResult.interpretation && (
                      <div style={{whiteSpace: 'pre-wrap', paddingTop: 'var(--spacing-md)', borderTop: '1px solid var(--color-border)'}}>
                        {tarotResult.interpretation}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : systemLoading ? (
            <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                <div>正在分析...</div>
              </div>
            </div>
          ) : currentSystem === 'astrology' ? (
            <div className="card">
              <div className="card-body" style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
                <div style={{display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap'}}>
                  <button
                    className={`btn ${astrologyMode === 'report' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setAstrologyMode('report')}
                  >
                    本命盤報告
                  </button>
                  <button
                    className={`btn ${astrologyMode === 'transit' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setAstrologyMode('transit')}
                  >
                    流年分析
                  </button>
                </div>

                {astrologyMode === 'transit' ? (
                  <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                    <div className="form-group">
                      <label className="form-label">流年日期</label>
                      <input
                        type="date"
                        className="form-input"
                        value={astrologyTransitDate}
                        onChange={(e) => setAstrologyTransitDate(e.target.value)}
                      />
                    </div>
                    <div style={{display: 'flex', gap: 'var(--spacing-sm)'}}>
                      <button className="btn btn-primary" onClick={handleAstrologyTransit} disabled={astrologyLoading}>
                        {astrologyLoading ? '分析中...' : '開始分析'}
                      </button>
                    </div>
                    {astrologyError && <div style={{color: 'var(--color-danger)'}}>{astrologyError}</div>}
                    {astrologyResult?.transit_analysis && (
                      <div className="card" style={{background: 'var(--color-bg-secondary)'}}>
                        <div className="card-body markdown-content">
                          <ReactMarkdown>{astrologyResult.transit_analysis}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="card" style={{background: 'var(--color-bg-secondary)'}}>
                    <div className="card-body markdown-content">
                      <ReactMarkdown>{systemData?.report?.analysis || systemData?.analysis || '尚無本命盤報告'}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : systemData ? (
            <div className="card">
              <div className="card-body">
                {(() => {
                  const rawText = systemData.report?.analysis || systemData.report?.interpretation || systemData.analysis || systemData.interpretation
                  if (!rawText) {
                    return <pre style={{fontSize: '12px', overflow: 'auto'}}>{JSON.stringify(systemData.report || systemData, null, 2)}</pre>
                  }

                  if (currentSystem === 'ziwei') {
                    const structure = _getZiweiChartStructure(systemData)
                    const { cleaned, chart } = _extractZiweiAsciiChart(rawText)
                    return (
                      <div className="markdown-content">
                        {structure && (
                          <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                            {_renderZiweiGrid(structure)}
                          </div>
                        )}
                        {chart && (
                          <details style={{marginBottom: 'var(--spacing-md)'}}>
                            <summary style={{cursor: 'pointer', fontWeight: 600}}>顯示 ASCII 命盤圖（備援）</summary>
                            <pre style={{overflow: 'auto', marginTop: 'var(--spacing-sm)'}}><code>{chart}</code></pre>
                          </details>
                        )}
                        <ReactMarkdown>{cleaned}</ReactMarkdown>
                      </div>
                    )
                  }

                  return (
                    <div className="markdown-content">
                      <ReactMarkdown>{rawText}</ReactMarkdown>
                    </div>
                  )
                })()}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="card-body">尚無分析資料</div>
            </div>
          )}
        </div>
      </>
    )
  }

  // Profile View (個人資料)
  const renderProfileView = () => {
    // Hooks lifted to App component scope to prevent conditional hook call errors

    const handleSave = async () => {
      if (!profileEditForm.birth_date || !profileEditForm.birth_time || !profileEditForm.birth_location) {
        showToast('請填寫完整的生辰資料', 'error')
        return
      }

      setProfileSaving(true)
      try {
        await apiCall('/api/profile/birth-info', profileEditForm, 'PUT')
        showToast('個人資料已更新', 'success')
        setProfileEditMode(false)
        fetchProfile() // 重新載入資料
      } catch (error) {
        showToast('更新失敗：' + error.message, 'error')
      } finally {
        setProfileSaving(false)
      }
    }

    return (
      <>
        <div className="content-header">
          <h1 className="content-title">個人資料</h1>
          <p className="content-subtitle">管理您的生辰資料與命盤狀態</p>
        </div>
        <div className="content-body">
          {/* 基本資料卡片 */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">生辰資料</div>
              <div className="card-subtitle">
                {birthInfo?.has_chart && <span style={{color: 'var(--color-success)'}}>✓ 已建立命盤</span>}
                {!birthInfo?.has_chart && birthInfo && <span style={{color: 'var(--color-warning)'}}>尚未建立命盤</span>}
                {!birthInfo && <span style={{color: 'var(--color-text-tertiary)'}}>尚未填寫資料</span>}
              </div>
            </div>
            <div className="card-body">
              {!birthInfo && !profileEditMode && (
                <div style={{textAlign: 'center', padding: 'var(--spacing-xl)', color: 'var(--color-text-secondary)'}}>
                  <div style={{fontSize: '3rem', marginBottom: 'var(--spacing-md)'}}>📝</div>
                  <p>尚未填寫生辰資料</p>
                  <p style={{fontSize: '0.9rem', marginTop: 'var(--spacing-sm)'}}>
                    填寫資料後即可建立專屬命盤
                  </p>
                </div>
              )}

              {birthInfo && !profileEditMode && (
                <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                  <div className="info-row">
                    <span className="info-label">姓名：</span>
                    <span className="info-value">{birthInfo.name || '未填寫'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">性別：</span>
                    <span className="info-value">{birthInfo.gender || '未指定'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">出生日期：</span>
                    <span className="info-value">{birthInfo.birth_date || '未填寫'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">出生時間：</span>
                    <span className="info-value">{birthInfo.birth_time || '未填寫'}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">出生地點：</span>
                    <span className="info-value">{birthInfo.birth_location || '未填寫'}</span>
                  </div>
                  {birthInfo.longitude && birthInfo.latitude && (
                    <div className="info-row">
                      <span className="info-label">經緯度：</span>
                      <span className="info-value" style={{fontSize: '0.9rem', color: 'var(--color-text-secondary)'}}>
                        {birthInfo.longitude.toFixed(4)}, {birthInfo.latitude.toFixed(4)}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {profileEditMode && (
                <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
                  <div className="form-group">
                    <label className="form-label">姓名</label>
                    <input 
                      type="text"
                      className="form-input"
                      value={profileEditForm.name}
                      onChange={(e) => setProfileEditForm({...profileEditForm, name: e.target.value})}
                      placeholder="例：張小明"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">性別</label>
                    <select 
                      className="form-select"
                      value={profileEditForm.gender}
                      onChange={(e) => setProfileEditForm({...profileEditForm, gender: e.target.value})}
                    >
                      <option value="男">男</option>
                      <option value="女">女</option>
                      <option value="未指定">未指定</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">出生日期（國曆）</label>
                    <input 
                      type="date"
                      className="form-input"
                      value={profileEditForm.birth_date}
                      onChange={(e) => setProfileEditForm({...profileEditForm, birth_date: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">出生時間</label>
                    <input 
                      type="time"
                      className="form-input"
                      value={profileEditForm.birth_time}
                      onChange={(e) => setProfileEditForm({...profileEditForm, birth_time: e.target.value})}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">出生地點</label>
                    <input 
                      type="text"
                      className="form-input"
                      value={profileEditForm.birth_location}
                      onChange={(e) => setProfileEditForm({...profileEditForm, birth_location: e.target.value})}
                      placeholder="例：台灣台北市"
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="card-footer">
              {!profileEditMode && (
                <button 
                  className="btn btn-primary"
                  onClick={() => {
                    setProfileEditForm({
                      name: birthInfo?.name || '',
                      gender: birthInfo?.gender || '男',
                      birth_date: birthInfo?.birth_date || '',
                      birth_time: birthInfo?.birth_time || '',
                      birth_location: birthInfo?.birth_location || ''
                    })
                    setProfileEditMode(true)
                  }}
                >
                  {birthInfo ? '編輯資料' : '填寫資料'}
                </button>
              )}
              {profileEditMode && (
                <>
                  <button 
                    className="btn btn-ghost"
                    onClick={() => setProfileEditMode(false)}
                    disabled={profileSaving}
                  >
                    取消
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handleSave}
                    disabled={profileSaving}
                  >
                    {profileSaving ? '儲存中...' : '儲存'}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* 命盤狀態卡片 */}
          {birthInfo?.has_chart && (
            <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
              <div className="card-header">
                <div className="card-title">命盤狀態</div>
              </div>
              <div className="card-body">
                <div style={{display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)'}}>
                  <div style={{fontSize: '2rem'}}>📊</div>
                  <div>
                    <div style={{fontWeight: 600, marginBottom: 'var(--spacing-xs)'}}>
                      命盤已鎖定
                    </div>
                    <div style={{fontSize: '0.9rem', color: 'var(--color-text-secondary)'}}>
                      您的專屬命盤已建立完成，可以開始進行各系統分析
                    </div>
                  </div>
                </div>
              </div>
              <div className="card-footer" style={{display: 'flex', gap: 'var(--spacing-md)'}}>
                <button 
                  className="btn btn-primary"
                  style={{flex: 1}}
                  onClick={() => setCurrentView('overview')}
                >
                  查看命盤
                </button>
                <button 
                  className="btn btn-outline-danger"
                  style={{flex: 1}}
                  onClick={async () => {
                    if (confirm('確定要清空六大系統報告內容嗎？\n\n這不會重新生成，因此會立即完成。')) {
                      setProfileSaving(true)
                      try {
                        // 先清空前端快取（避免看起來像「沒重置」）
                        setOverviewData(null)
                        setSystemAnalysis({})
                        setSystemData(null)
                        setChartAnalysis(null)
                        setChartSummary(null)

                        const res = await apiCall('/api/profile/clear-reports', {
                          user_id: profile.user_id,
                          clear_chart_lock: false
                        })

                        if (res.status === 'success') {
                          showToast('已清空六大系統報告', 'success')
                          await refreshAfterRegenerate(profile.user_id)
                        } else {
                          showToast('清空失敗', 'error')
                        }
                      } catch (e) {
                        showToast('清空過程中發生錯誤', 'error')
                      } finally {
                        setProfileSaving(false)
                      }
                    }
                  }}
                  disabled={profileSaving}
                >
                  {profileSaving ? '處理中...' : '清空六大系統報告'}
                </button>
              </div>
            </div>
          )}

          {/* 提示卡片 */}
          {birthInfo && !birthInfo.has_chart && (
            <div className="card" style={{marginTop: 'var(--spacing-xl)', borderLeft: '4px solid var(--color-warning)'}}>
              <div className="card-body">
                <div style={{display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)'}}>
                  <div style={{fontSize: '2rem'}}>💡</div>
                  <div>
                    <div style={{fontWeight: 600, marginBottom: 'var(--spacing-xs)', color: 'var(--color-warning)'}}>
                      尚未建立命盤
                    </div>
                    <div style={{fontSize: '0.9rem', color: 'var(--color-text-secondary)'}}>
                      填寫完生辰資料後，請前往「建立命盤」頁面建立您的專屬命盤
                    </div>
                  </div>
                </div>
              </div>
              <div className="card-footer">
                <button 
                  className="btn btn-primary"
                  onClick={() => setCurrentView('chart')}
                >
                  前往建立命盤
                </button>
              </div>
            </div>
          )}
        </div>
      </>
    )
  }

  // Settings View
  const renderSettingsView = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">設定</h1>
        <p className="content-subtitle">管理您的帳號與偏好設定</p>
      </div>
      <div className="content-body">
        <div className="card">
          <div className="card-header">
            <div className="card-title">個人資料</div>
          </div>
          <div className="card-body">
            <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
              <div><strong>User ID：</strong>{profile?.user_id}</div>
              <div><strong>Email：</strong>{profile?.email}</div>
              <div><strong>顯示名稱：</strong>{profile?.display_name || '未設定'}</div>
            </div>
          </div>
        </div>

        <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
          <div className="card-header">
            <div className="card-title">API 設定</div>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">API 位址</label>
              <input 
                type="text"
                className="form-input"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
              />
            </div>
          </div>
          <div className="card-footer">
            <button 
              className="btn btn-primary"
              onClick={() => {
                localStorage.setItem('aetheria_api_base', apiBase)
                showToast('API 位址已更新', 'success')
              }}
            >
              儲存
            </button>
          </div>
        </div>

        <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
          <div className="card-header">
            <div className="card-title">帳號管理</div>
          </div>
          <div className="card-footer">
            <button 
              className="btn btn-secondary"
              onClick={handleLogout}
            >
              登出
            </button>
          </div>
        </div>
      </div>
    </>
  )

  // Sidebar Navigation
  const renderSidebar = () => (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-logo">A</div>
          <div>
            <div className="sidebar-title">Aetheria</div>
          </div>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-section">
          <div 
            className={`nav-item ${currentView === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentView('home')}
          >
            <div className="nav-icon">🏠</div>
            <div>首頁</div>
          </div>
          <div 
            className={`nav-item ${currentView === 'chart' ? 'active' : ''}`}
            onClick={() => setCurrentView('chart')}
          >
            <div className="nav-icon">🔮</div>
            <div>建立命盤</div>
            {!chartLocked && <div className="nav-badge">!</div>}
          </div>
          {chartLocked && (
            <div 
              className={`nav-item ${currentView === 'overview' ? 'active' : ''}`}
              onClick={() => setCurrentView('overview')}
            >
              <div className="nav-icon">📊</div>
              <div>我的命盤</div>
            </div>
          )}
        </div>

        <div className="nav-section">
          <div className="nav-label">命理系統</div>
          <div 
            className={`nav-item ${currentView === 'systems' ? 'active' : ''}`}
            onClick={() => setCurrentView('systems')}
          >
            <div className="nav-icon">📚</div>
            <div>六大系統</div>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-label">AI 諮詢</div>
          <div 
            className="nav-item ai-consult"
            onClick={() => setShowVoiceChat(true)}
          >
            <div className="nav-icon">🔮</div>
            <div>命理顧問</div>
            <div className="nav-badge" style={{background: 'var(--color-accent)'}}>AI</div>
          </div>
        </div>

        {/* 戰略側寫已隱藏 - AI 諮詢可完全取代 */}
        {/* <div className="nav-section">
          <div className="nav-label">進階功能</div>
          <div 
            className={`nav-item strategic ${currentView === 'strategic' ? 'active' : ''}`}
            onClick={() => setCurrentView('strategic')}
          >
            <div className="nav-icon">🎯</div>
            <div>戰略側寫</div>
            <div className="nav-badge">NEW</div>
          </div>
        </div> */}

        <div className="nav-section">
          <div 
            className={`nav-item ${currentView === 'profile' ? 'active' : ''}`}
            onClick={() => setCurrentView('profile')}
          >
            <div className="nav-icon">👤</div>
            <div>個人資料</div>
          </div>
          <div 
            className={`nav-item ${currentView === 'settings' ? 'active' : ''}`}
            onClick={() => setCurrentView('settings')}
          >
            <div className="nav-icon">⚙️</div>
            <div>設定</div>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-card">
          <div className="user-avatar">
            {profile?.display_name?.charAt(0) || profile?.email?.charAt(0) || 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{profile?.display_name || '用戶'}</div>
            <div className="user-email">{profile?.email}</div>
          </div>
        </div>
      </div>
    </div>
  )

  // Auth Modal
  const renderAuthModal = () => {
    if (!showAuthModal) return null

    const handleSubmit = (e) => {
      e.preventDefault()
      if (authMode === 'login') {
        handleLogin()
      } else {
        handleRegister()
      }
    }

    return (
      <div className="modal-backdrop" onClick={() => setShowAuthModal(false)}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <div className="modal-title">
              {authMode === 'login' ? '登入 Aetheria' : '註冊 Aetheria'}
            </div>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {authMode === 'register' && (
                <div className="form-group">
                  <label className="form-label">顯示名稱</label>
                  <input 
                    type="text"
                    className="form-input"
                    value={authForm.display_name}
                    onChange={(e) => setAuthForm({...authForm, display_name: e.target.value})}
                    placeholder="您想被稱呼的名字"
                    autoComplete="name"
                  />
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Email</label>
                <input 
                  type="email"
                  className="form-input"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  placeholder="your@email.com"
                  autoComplete="email"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">密碼</label>
                <input 
                  type="password"
                  className="form-input"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                  placeholder="至少 8 碼"
                  autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
                  required
                  minLength={8}
                />
              </div>
              <div style={{fontSize: '13px', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-md)'}}>
                {authMode === 'login' ? (
                  <>
                    還沒有帳號？
                    <span 
                      style={{color: 'var(--color-primary)', cursor: 'pointer', marginLeft: 'var(--spacing-xs)'}}
                      onClick={() => setAuthMode('register')}
                    >
                      立即註冊
                    </span>
                  </>
                ) : (
                  <>
                    已有帳號？
                    <span 
                      style={{color: 'var(--color-primary)', cursor: 'pointer', marginLeft: 'var(--spacing-xs)'}}
                      onClick={() => setAuthMode('login')}
                    >
                      直接登入
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <button 
                type="button"
                className="btn btn-ghost"
                onClick={() => setShowAuthModal(false)}
              >
                取消
              </button>
              <button 
                type="submit"
                className="btn btn-primary"
                disabled={loading || !authForm.email || !authForm.password || (authMode === 'register' && authForm.password.length < 8)}
              >
                {loading ? '處理中...' : (authMode === 'login' ? '登入' : '註冊')}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // Toast Notification
  const renderToast = () => {
    if (!toast.show) return null

    const icons = {
      success: '✓',
      error: '✕',
      info: 'ℹ'
    }

    return (
      <div className="toast-container">
        <div className={`toast toast-${toast.type}`}>
          <div className="toast-icon">{icons[toast.type]}</div>
          <div className="toast-content">
            <div className="toast-message">{toast.message}</div>
          </div>
        </div>
      </div>
    )
  }

  // ========== Main Render ==========
  return (
    <div className="app">
      <div className="app-bg"></div>
      
      {!token ? (
        // Landing Page
        renderLanding()
      ) : (
        // Dashboard
        <div className="dashboard">
          {renderSidebar()}
          <div className="main-content">
            {currentView === 'home' && renderDashboardHome()}
            {currentView === 'chart' && renderChartView()}
            {currentView === 'overview' && renderOverviewView()}
            {currentView === 'systems' && renderSystemsView()}
            {currentView === 'system-detail' && renderSystemDetailView()}
            {currentView === 'strategic' && renderStrategicView()}
            {currentView === 'profile' && renderProfileView()}
            {currentView === 'settings' && renderSettingsView()}
          </div>
        </div>
      )}

      {renderAuthModal()}
      {renderToast()}
      
      {/* AI 命理顧問 */}
      {showVoiceChat && (
        <VoiceChat 
          apiBase={apiBase}
          token={token}
          onClose={() => setShowVoiceChat(false)}
        />
      )}
    </div>
  )
}

export default App
