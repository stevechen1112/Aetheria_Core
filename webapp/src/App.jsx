import { useEffect, useState, useMemo } from 'react'
import pinyin from 'pinyin'
import ReactMarkdown from 'react-markdown'
import './App.v2.css'

/* ==========================================
   Aetheria Core - v2.0 完全重新設計
   現代化命理分析平台
========================================== */

// 系統名稱中英對照
const SYSTEM_NAME_MAP = {
  ziwei: '紫微斗數',
  bazi: '八字',
  astrology: '西洋占星',
  numerology: '靈數學',
  name: '姓名學',
  tarot: '塔羅'
}

const getSystemNameZh = (system) => SYSTEM_NAME_MAP[system] || system

// 紫微斗數命盤可視化組件
const ZiweiChart = ({ structure }) => {
  if (!structure) return null;
  const palaceNames = [
    '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
    '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮'
  ]
  const twelvePalaces = structure['十二宮']
  const palaces = twelvePalaces && Object.keys(twelvePalaces).length > 0
    ? twelvePalaces
    : palaceNames.reduce((acc, name) => {
        if (structure[name]) acc[name] = structure[name]
        return acc
      }, {})
  
  // 地支配置 (標準盤面: 巳在左上)
  const branchPositions = {
    '巳': { gridArea: '1 / 1 / 2 / 2' },
    '午': { gridArea: '1 / 2 / 2 / 3' },
    '未': { gridArea: '1 / 3 / 2 / 4' },
    '申': { gridArea: '1 / 4 / 2 / 5' },
    '酉': { gridArea: '2 / 4 / 3 / 5' },
    '戌': { gridArea: '3 / 4 / 4 / 5' },
    '亥': { gridArea: '4 / 4 / 5 / 5' },
    '子': { gridArea: '4 / 3 / 5 / 4' },
    '丑': { gridArea: '4 / 2 / 5 / 3' },
    '寅': { gridArea: '4 / 1 / 5 / 2' },
    '卯': { gridArea: '3 / 1 / 4 / 2' },
    '辰': { gridArea: '2 / 1 / 3 / 2' }
  };
  
  const getPalaceByBranch = (branch) => {
    for (const [name, data] of Object.entries(palaces)) {
      if (data.宮位 && data.宮位.indexOf(branch) !== -1) return { name, ...data };
    }
    return null;
  };

  return (
    <div className="ziwei-chart" style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gridTemplateRows: 'repeat(4, 1fr)',
      gap: '4px',
      aspectRatio: '1',
      width: '100%',
      maxWidth: '600px',
      margin: '0 auto var(--spacing-lg)',
      background: '#f8f9fa',
      padding: '4px',
      borderRadius: '8px',
      border: '1px solid #ddd',
      color: '#333'
    }}>
       {/* 中宮 */}
       <div style={{
         gridArea: '2 / 2 / 4 / 4',
         background: 'white',
         display: 'flex',
         flexDirection: 'column',
         alignItems: 'center',
         justifyContent: 'center',
         padding: '10px',
         textAlign: 'center',
         borderRadius: '4px'
       }}>
         <div style={{fontWeight: 'bold', fontSize: '1.2rem', marginBottom: '8px', color: '#5e4b8b'}}>紫微斗數</div>
         <div style={{marginBottom: '4px'}}>{structure.五行局 || structure.局 || ''}</div>
         <div style={{fontSize: '0.9rem'}}>{structure.格局 ? structure.格局.join('、') : ''}</div>
       </div>

       {Object.entries(branchPositions).map(([branch, style]) => {
          const palaceData = getPalaceByBranch(branch);
          const isMing = palaceData?.name === '命宮';
          
          return (
            <div key={branch} style={{
               ...style,
               background: 'white',
               border: isMing ? '2px solid #ffd700' : '1px solid #eee',
               borderRadius: '4px',
               padding: '6px',
               fontSize: '0.85rem',
               display: 'flex',
               flexDirection: 'column',
               overflow: 'hidden',
               boxShadow: isMing ? '0 0 10px rgba(255, 215, 0, 0.2)' : 'none'
            }}>
               <div style={{
                 display: 'flex', 
                 justifyContent: 'space-between', 
                 borderBottom: '1px solid #f0f0f0', 
                 marginBottom: '4px', 
                 paddingBottom: '2px'
               }}>
                 <span style={{fontWeight: 'bold'}}>{branch}</span>
                 <span style={{color: isMing ? '#d4af37' : '#666', fontWeight: isMing ? 'bold' : 'normal'}}>
                   {palaceData?.name}
                 </span>
               </div>
               
               {palaceData && (
                 <>
                   <div style={{
                     color: '#d63031', 
                     fontWeight: 'bold', 
                     marginBottom: '2px',
                     display: 'flex',
                     flexWrap: 'wrap',
                     gap: '2px'
                   }}>
                     {palaceData.主星?.map(star => <span key={star}>{star}</span>)}
                   </div>
                   <div style={{
                     fontSize: '0.75rem', 
                     color: '#636e72',
                     lineHeight: 1.2
                   }}>
                     {palaceData.輔星?.join(' ')}
                   </div>
                 </>
               )}
               {!palaceData && (
                 <div style={{
                   fontSize: '0.75rem',
                   color: '#b2bec3',
                   lineHeight: 1.2
                 }}>
                   資料未提供
                 </div>
               )}
            </div>
          );
       })}
    </div>
  );
};

function App() {
  // ========== State Management ==========
  const [apiBase, setApiBase] = useState(
    localStorage.getItem('aetheria_api_base') || 'http://localhost:5001'
  )
  const [token, setToken] = useState(localStorage.getItem('aetheria_token') || '')
  const [profile, setProfile] = useState(null)
  const [currentView, setCurrentView] = useState('home') // home, chart, systems, strategic, settings
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
  
  // 預計算報告相關（移到這裡，與其他 Chart Data 一起）
  const [precomputedReports, setPrecomputedReports] = useState({})
  const [generationProgress, setGenerationProgress] = useState({
    current: '',
    completed: [],
    total: 0,
    errors: {}
  })

  // AI 命理顧問對話
  const [consultSessionId, setConsultSessionId] = useState(
    localStorage.getItem('aetheria_consult_session') || ''
  )
  const [consultMessages, setConsultMessages] = useState([])
  const [consultInput, setConsultInput] = useState('')
  const [consultSending, setConsultSending] = useState(false)
  const [consultExpanded, setConsultExpanded] = useState({}) // {index: boolean}
  const [consultSessions, setConsultSessions] = useState([])
  const [showSessionList, setShowSessionList] = useState(false)
  
  // 新設計：用戶檔案（漸進式資料收集）
  const [userProfile, setUserProfile] = useState({
    chinese_name: '',      // 姓名 → 解鎖姓名學
    birth_date: '',        // 出生日期 → 解鎖靈數學
    birth_time: '',        // 出生時辰 → 解鎖紫微、八字
    birth_location: '',    // 出生地點 → 解鎖西洋占星
    gender: '男'
  })
  
  // 系統可用性檢查
  const systemRequirements = useMemo(() => ({
    tarot: { 
      available: true, // 塔羅永遠可用
      icon: '🎴',
      name: '塔羅牌',
      needs: []
    },
    name: { 
      available: !!userProfile.chinese_name,
      icon: '📝',
      name: '姓名學',
      needs: ['chinese_name']
    },
    numerology: { 
      available: !!userProfile.birth_date,
      icon: '🔢',
      name: '靈數學',
      needs: ['birth_date']
    },
    ziwei: { 
      available: !!userProfile.birth_date && !!userProfile.birth_time,
      icon: '⭐',
      name: '紫微斗數',
      needs: ['birth_date', 'birth_time']
    },
    bazi: { 
      available: !!userProfile.birth_date && !!userProfile.birth_time,
      icon: '🏛️',
      name: '八字命理',
      needs: ['birth_date', 'birth_time']
    },
    astrology: { 
      available: !!userProfile.birth_date && !!userProfile.birth_time && !!userProfile.birth_location,
      icon: '🌟',
      name: '西洋占星',
      needs: ['birth_date', 'birth_time', 'birth_location']
    }
  }), [userProfile])
  
  // 計算已解鎖的系統數量
  const unlockedSystemCount = useMemo(() => {
    return Object.values(systemRequirements).filter(s => s.available).length
  }, [systemRequirements])
  
  // 塔羅占卜相關
  const [tarotForm, setTarotForm] = useState({
    spread_type: 'three_card',
    question: '',
    context: 'general'
  })
  const [tarotReading, setTarotReading] = useState(null)
  const [tarotLoading, setTarotLoading] = useState(false)
  const [tarotAdvancedMode, setTarotAdvancedMode] = useState(false)  // 進階模式開關
  
  // 塔羅牌圖片 URL 生成（使用本地圖片）
  const getTarotCardImage = (cardNameEn) => {
    if (!cardNameEn) return null
    
    // 大阿爾克那映射
    const majorArcana = {
      'The Fool': '00_The_Fool',
      'The Magician': '01_The_Magician',
      'The High Priestess': '02_The_High_Priestess',
      'The Empress': '03_The_Empress',
      'The Emperor': '04_The_Emperor',
      'The Hierophant': '05_The_Hierophant',
      'The Lovers': '06_The_Lovers',
      'The Chariot': '07_The_Chariot',
      'Strength': '08_Strength',
      'The Hermit': '09_The_Hermit',
      'Wheel of Fortune': '10_Wheel_of_Fortune',
      'Justice': '11_Justice',
      'The Hanged Man': '12_The_Hanged_Man',
      'Death': '13_Death',
      'Temperance': '14_Temperance',
      'The Devil': '15_The_Devil',
      'The Tower': '16_The_Tower',
      'The Star': '17_The_Star',
      'The Moon': '18_The_Moon',
      'The Sun': '19_The_Sun',
      'Judgement': '20_Judgement',
      'The World': '21_The_World'
    }
    
    if (majorArcana[cardNameEn]) {
      return `/tarot/${majorArcana[cardNameEn]}.jpg`
    }
    
    // 小阿爾克那：直接用英文名稱（空格轉底線）
    // 例如：Ace of Wands -> Ace_of_Wands.jpg
    const minorName = cardNameEn.replace(/ /g, '_')
    return `/tarot/${minorName}.jpg`
  }
  
  // Wizard for profile creation (新設計：5步驟)
  const [wizardStep, setWizardStep] = useState(1)
  const [chartForm, setChartForm] = useState({
    birth_date: '',
    birth_time: '',
    birth_location: '',
    gender: '男',
    chinese_name: '',
    english_name: ''
  })

  // ========== API Helpers ==========
  const authHeaders = useMemo(() => {
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    return headers
  }, [token])

  const apiCall = async (path, payload = null, method = 'POST') => {
    try {
      // 決定 HTTP 方法：明確指定 > 有 payload 用 POST > 無 payload 用 GET
      const httpMethod = method || (payload ? 'POST' : 'GET')
      const options = {
        method: httpMethod,
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

  const getChartPayload = () => {
    const birth_date = chartForm.birth_date || chartSummary?.birth_date || userProfile?.birth_date
    const birth_time = chartForm.birth_time || chartSummary?.birth_time || userProfile?.birth_time
    const birth_location = chartForm.birth_location || chartSummary?.birth_location || userProfile?.birth_location
    return { birth_date, birth_time, birth_location }
  }

  const ensureChartPayload = () => {
    const { birth_date, birth_time, birth_location } = getChartPayload()
    if (!birth_date || !birth_time || !birth_location) return null
    return { birth_date, birth_time, birth_location }
  }

  // 解析出生資料為 API 需要的格式
  const parseChartPayload = () => {
    const { birth_date, birth_time, birth_location } = getChartPayload()
    if (!birth_date || !birth_time) return null
    
    const [year, month, day] = birth_date.split('-').map(Number)
    const [hour, minute] = birth_time.split(':').map(Number)
    
    return {
      year,
      month,
      day,
      hour,
      minute,
      city: birth_location || 'Taipei'
    }
  }

  // ========== Toast System ==========
  const showToast = (message, type = 'info') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast({ show: false, message: '', type: 'info' }), 3000)
  }

  // ========== AI Consult Chat ===========
  const fetchConsultSessions = async () => {
    try {
      const resp = await apiCall('/api/chat/sessions', null, 'GET')
      if (resp.sessions) {
        setConsultSessions(resp.sessions)
      }
    } catch (error) {
      console.error('Failed to fetch chat sessions', error)
    }
  }

  const loadSessionMessages = async (sessionId) => {
    try {
      const resp = await apiCall(`/api/chat/messages?session_id=${sessionId}`, null, 'GET')
      if (resp.messages && Array.isArray(resp.messages)) {
        const formatted = resp.messages.map((m, idx) => ({
          ...m,
          ts: new Date(m.created_at).getTime() || Date.now() + idx
        }))
        setConsultMessages(formatted)
      }
    } catch (error) {
      console.error('Failed to load session messages', error)
      showToast('載入對話歷史失敗', 'error')
    }
  }

  const switchConsultSession = async (sessionId) => {
    localStorage.setItem('aetheria_consult_session', sessionId)
    setConsultSessionId(sessionId)
    setConsultExpanded({})
    setShowSessionList(false)
    // 載入該對話的歷史訊息
    await loadSessionMessages(sessionId)
    showToast('已切換對話', 'info')
  }

  const deleteConsultSession = async (sessionId, e) => {
    e.stopPropagation() // 阻止觸發 switchConsultSession
    if (!window.confirm('確定要刪除這個對話嗎？')) return
    
    try {
      await apiCall(`/api/chat/sessions/${sessionId}`, null, 'DELETE')
      // 如果刪除的是當前對話，清空
      if (sessionId === consultSessionId) {
        localStorage.removeItem('aetheria_consult_session')
        setConsultSessionId('')
        setConsultMessages([])
      }
      // 重新載入列表
      fetchConsultSessions()
      showToast('對話已刪除', 'success')
    } catch (error) {
      showToast('刪除失敗', 'error')
    }
  }

  const startNewConsult = () => {
    localStorage.removeItem('aetheria_consult_session')
    setConsultSessionId('')
    setConsultMessages([])
    setConsultExpanded({})
    setShowSessionList(false)
    showToast('已開始新的諮詢對話', 'info')
  }

  const sendConsult = async () => {
    const text = consultInput.trim()
    if (!text || consultSending) return

    setConsultInput('')
    setConsultSending(true)
    setConsultMessages(prev => ([
      ...prev,
      { role: 'user', content: text, ts: Date.now() }
    ]))

    // Add typing indicator
    const typingId = Date.now() + 1
    setConsultMessages(prev => ([
      ...prev,
      { role: 'typing', content: '', ts: typingId, id: typingId }
    ]))

    try {
      const payload = {
        message: text,
        ...(consultSessionId ? { session_id: consultSessionId } : {})
      }
      const resp = await apiCall('/api/chat/consult', payload)
      if (resp.session_id && !consultSessionId) {
        setConsultSessionId(resp.session_id)
        localStorage.setItem('aetheria_consult_session', resp.session_id)
      }
      // Remove typing indicator and add real response
      setConsultMessages(prev => {
        const filtered = prev.filter(m => m.id !== typingId)
        return [
          ...filtered,
          {
            role: 'assistant',
            content: resp.reply,
            citations: resp.citations || [],
            used_systems: resp.used_systems || [],
            confidence: resp.confidence,
            next_steps: resp.next_steps || [],
            ts: Date.now()
          }
        ]
      })
      // Refresh session list
      fetchConsultSessions()
    } catch (error) {
      // Remove typing indicator and show error
      setConsultMessages(prev => {
        const filtered = prev.filter(m => m.id !== typingId)
        return [
          ...filtered,
          {
            role: 'assistant',
            content: '目前諮詢服務暫時無法使用，請稍後再試。',
            citations: [],
            used_systems: [],
            confidence: 0.0,
            next_steps: [],
            ts: Date.now()
          }
        ]
      })
    } finally {
      setConsultSending(false)
    }
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
    setPrecomputedReports({})
    setCurrentView('home')
    showToast('已登出', 'info')
  }

  // ========== Profile & Chart ==========
  const fetchProfile = async () => {
    if (!token) return
    try {
      const data = await apiCall('/api/profile', null, 'GET')
      setProfile(data.profile)
    } catch (error) {
      localStorage.removeItem('aetheria_token')
      setToken('')
    }
  }

  const checkChartLock = async () => {
    if (!profile) return
    try {
      const data = await apiCall(`/api/chart/get-lock?user_id=${profile.user_id}`, null, 'GET')
      if (data.locked) {
        setChartLocked(true)
        setChartSummary(data.chart_structure)
      }
    } catch (error) {
      // No chart locked yet
    }
  }
  
  // 新增：獲取預計算報告
  const fetchPrecomputedReports = async () => {
    if (!profile?.user_id) return
    try {
      const data = await apiCall(`/api/reports/get?user_id=${profile.user_id}`, null, 'GET')
      if (data.found && data.reports) {
        setPrecomputedReports(data.reports)
        // 更新 userProfile 根據已有報告
        const availableSystems = data.available_systems || []
        if (availableSystems.length > 1) {  // 超過塔羅
          // 從紫微報告中提取用戶資料
          if (data.reports.ziwei?.report) {
            const ziweiData = data.reports.ziwei.report
            setUserProfile(prev => ({
              ...prev,
              birth_date: ziweiData.birth_date || prev.birth_date,
              birth_time: ziweiData.birth_time || prev.birth_time,
              birth_location: ziweiData.birth_location || prev.birth_location,
              gender: ziweiData.gender || prev.gender
            }))
            // 設定命盤摘要
            if (ziweiData.chart_structure) {
              setChartSummary(ziweiData.chart_structure)
              setChartLocked(true)
            }
          }
          // 從姓名報告提取姓名
          if (data.reports.name?.report) {
            setUserProfile(prev => ({
              ...prev,
              chinese_name: data.reports.name.report.chinese_name || prev.chinese_name
            }))
          }
        }
      }
    } catch (error) {
      console.log('獲取預計算報告失敗', error)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [token])

  useEffect(() => {
    if (profile) {
      checkChartLock()
      fetchPrecomputedReports()  // 新增
    }
  }, [profile])

  useEffect(() => {
    if (currentView !== 'consult') return
    fetchConsultSessions()
    if (consultMessages.length > 0) return
    setConsultMessages([
      {
        role: 'assistant',
        content: '我是你的 AI 命理顧問。你可以直接問：感情、工作、財務、健康、決策時機等。我會以資料為依據並附上「依據」引用；如果資料不足也會明確說明。',
        citations: [],
        used_systems: [],
        confidence: 0.0,
        next_steps: ['感情走向細節', '近期職場策略', '重要決策時間點'],
        ts: Date.now()
      }
    ])
  }, [currentView, consultMessages.length])

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

    const payload = ensureChartPayload()
    if (!payload) {
      showToast('缺少出生資料，請重新建立命盤', 'error')
      return
    }

    const parsed = parseChartPayload()
    const chineseName = chartForm.chinese_name || userProfile?.chinese_name || profile?.display_name
    const gender = chartForm.gender || userProfile?.gender || 'male'

    let isActive = true
    setSystemLoading(true)

    const run = async () => {
      try {
        let endpoint = ''
        let requestPayload = {}

        switch (currentSystem) {
          case 'ziwei':
            setSystemData({ analysis: '紫微斗數詳細分析請使用「流年運勢」等專門功能' })
            setSystemLoading(false)
            return
          case 'bazi':
            endpoint = '/api/bazi/analysis'
            requestPayload = {
              user_id: profile.user_id,
              year: parsed.year,
              month: parsed.month,
              day: parsed.day,
              hour: parsed.hour,
              minute: parsed.minute,
              gender: gender
            }
            break
          case 'astrology':
            endpoint = '/api/astrology/natal'
            requestPayload = {
              name: chineseName || 'User',
              year: parsed.year,
              month: parsed.month,
              day: parsed.day,
              hour: parsed.hour,
              minute: parsed.minute,
              city: parsed.city
            }
            break
          case 'numerology':
            endpoint = '/api/numerology/profile'
            
            // 處理中文姓名，轉換為拼音以正確計算數字
            let numerologyName = chineseName || profile.display_name || ''
            if (numerologyName && /[\u4e00-\u9fa5]/.test(numerologyName)) {
              try {
                // 使用 pinyin 庫轉換為無聲調拼音
                const style = pinyin.STYLE_NORMAL || 0
                const pinyinResult = pinyin(numerologyName, { style })
                numerologyName = pinyinResult.flat().join('') // 靈數學通常合併字母計算
                console.log('Numerology: Converted to pinyin:', numerologyName)
              } catch (e) {
                console.warn('Pinyin conversion failed, using original:', e)
              }
            }

            requestPayload = {
              name: numerologyName,
              birth_date: payload.birth_date
            }
            break
          case 'name':
            endpoint = '/api/name/analyze'
            requestPayload = {
              name: chineseName
            }
            break
          case 'tarot':
            showToast('塔羅牌需要選擇牌陣和問題', 'info')
            setSystemLoading(false)
            return
          default:
            showToast('系統不存在', 'error')
            setSystemLoading(false)
            return
        }

        const data = await apiCall(endpoint, requestPayload)
        if (!isActive) return
        setSystemData(data)
        setSystemAnalysis((prev) => ({ ...prev, [currentSystem]: data }))
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
  }, [currentView, currentSystem, chartLocked, profile?.user_id, chartForm.chinese_name, chartForm.gender, systemAnalysis])

  // ========== Chart Creation Wizard ==========
  
  // 新流程：儲存資料並批次生成報告
  const handleSaveAndAnalyze = async () => {
    setLoading(true)
    setWizardStep(6) // 進入分析階段
    
    // 計算要生成的系統
    const systemsToGenerate = ['tarot']
    if (chartForm.chinese_name) systemsToGenerate.push('name')
    if (chartForm.birth_date) systemsToGenerate.push('numerology')
    if (chartForm.birth_date && chartForm.birth_time) {
      systemsToGenerate.push('bazi', 'ziwei')
    }
    if (chartForm.birth_date && chartForm.birth_time && chartForm.birth_location) {
      systemsToGenerate.push('astrology')
    }
    
    setGenerationProgress({
      current: '準備中...',
      completed: [],
      total: systemsToGenerate.filter(s => s !== 'tarot').length,
      errors: {}
    })
    
    try {
      const data = await apiCall('/api/profile/save-and-analyze', {
        user_id: profile.user_id,
        chinese_name: chartForm.chinese_name,
        gender: chartForm.gender,
        birth_date: chartForm.birth_date,
        birth_time: chartForm.birth_time,
        birth_location: chartForm.birth_location
      })
      
      // 更新狀態
      setUserProfile({
        chinese_name: chartForm.chinese_name,
        birth_date: chartForm.birth_date,
        birth_time: chartForm.birth_time,
        birth_location: chartForm.birth_location,
        gender: chartForm.gender
      })
      
      // 如果有紫微命盤，更新 chartSummary
      if (data.reports_generated?.ziwei) {
        // 獲取紫微報告
        try {
          const ziweiReport = await apiCall(`/api/reports/get?user_id=${profile.user_id}&system=ziwei`, null, 'GET')
          if (ziweiReport.found && ziweiReport.report?.chart_structure) {
            setChartSummary(ziweiReport.report.chart_structure)
            setChartLocked(true)
          }
        } catch (e) {
          console.log('獲取紫微報告失敗', e)
        }
      }
      
      // 載入所有預計算報告
      try {
        const allReports = await apiCall(`/api/reports/get?user_id=${profile.user_id}`, null, 'GET')
        if (allReports.found) {
          setPrecomputedReports(allReports.reports)
        }
      } catch (e) {
        console.log('載入報告失敗', e)
      }
      
      setGenerationProgress({
        current: '完成',
        completed: Object.keys(data.reports_generated || {}).filter(k => data.reports_generated[k]),
        total: systemsToGenerate.filter(s => s !== 'tarot').length,
        errors: data.generation_errors || {}
      })
      
      setWizardStep(8) // 直接跳到完成
      showToast(`已生成 ${Object.values(data.reports_generated || {}).filter(v => v).length} 個系統報告！`, 'success')
      
    } catch (error) {
      console.error('儲存失敗:', error)
      setWizardStep(5) // 返回確認頁
    } finally {
      setLoading(false)
    }
  }
  
  // 塔羅占卜函數
  const handleTarotReading = async () => {
    setTarotLoading(true)
    try {
      const data = await apiCall('/api/tarot/reading', {
        spread_type: tarotForm.spread_type,
        question: tarotForm.question || undefined,
        context: tarotForm.context,
        allow_reversed: true
      })
      setTarotReading(data.data)
      showToast('塔羅牌占卜完成！', 'success')
    } catch (error) {
      console.error('塔羅占卜失敗:', error)
    } finally {
      setTarotLoading(false)
    }
  }
  
  // 重置塔羅占卜
  const resetTarotReading = () => {
    setTarotReading(null)
    setTarotForm({
      spread_type: 'three_card',
      question: '',
      context: 'general'
    })
  }
  
  // 保留舊的 handleCreateChart 作為備用
  const handleCreateChart = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/api/chart/initial-analysis', {
        user_id: profile.user_id,
        birth_date: chartForm.birth_date,
        birth_time: chartForm.birth_time,
        birth_location: chartForm.birth_location,
        gender: chartForm.gender
      })

      if (data.warning) {
        showToast(data.warning, 'warning')
      }
      
      // API 回傳 structure 或 chart_structure
      const structure = data.structure || data.chart_structure
      
      if (!structure) {
        showToast('命盤結構解析失敗，請檢查輸入資料', 'error')
        console.error('API 回傳資料:', data)
        setWizardStep(5) // 返回確認頁
        return
      }
      
      setChartSummary(structure)
      setWizardStep(7) // 新版：步驟7是預覽
      showToast('命盤建立成功！', 'success')
    } catch (error) {
      console.error('命盤建立失敗:', error)
      setWizardStep(5) // 返回確認頁
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmLock = async () => {
    setLoading(true)
    try {
      await apiCall('/api/chart/confirm-lock', {
        user_id: profile.user_id
      })
      setChartLocked(true)
      setWizardStep(8) // 新版：步驟8是完成
      showToast('命盤已鎖定！', 'success')
    } catch (error) {
      // Error already shown
    } finally {
      setLoading(false)
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
            <button 
              className="btn btn-secondary btn-lg"
              onClick={() => showToast('塔羅訪客功能開發中', 'info')}
              style={{display: 'flex', alignItems: 'center', gap: '8px'}}
            >
              🎴 免登入抽塔羅
            </button>
          </div>
        </div>
      </div>

      <div className="landing-features">
        <h2 className="features-title">六大命理系統 + 戰略側寫</h2>
        <p style={{textAlign: 'center', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-xl)', marginTop: '-10px'}}>
          💡 不同系統需要不同資料，塔羅牌無需任何資料即可使用
        </p>
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
          <div className="feature-card" style={{gridColumn: 'span 2', background: 'var(--color-strategic-bg)', borderColor: 'var(--color-strategic)'}}>
            <div className="feature-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
            <div className="feature-title" style={{color: 'var(--color-strategic)'}}>
              ✨ 戰略側寫系統
            </div>
            <div className="feature-desc">
              全息圖譜、生辰校正、關係生態位、決策沙盒 - 四大戰略工具，
              從被動算命升級為主動決策支援
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  // Dashboard Home (已登入首頁) - 新設計：顯示解鎖進度
  const renderDashboardHome = () => (
    <>
      <div className="content-header">
        <h1 className="content-title">歡迎回來，{profile?.display_name || '用戶'}</h1>
        <p className="content-subtitle">
          已解鎖 {unlockedSystemCount}/6 個命理系統
          {unlockedSystemCount < 6 && ' - 補充更多資料以解鎖更多系統'}
        </p>
      </div>
      <div className="content-body">
        {/* 系統解鎖狀態卡片 */}
        <div className="dashboard-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{background: 'var(--color-primary)'}}>📋</div>
            <div className="stat-content">
              <div className="stat-value">{unlockedSystemCount}/6</div>
              <div className="stat-label">已解鎖系統</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{background: chartLocked ? 'var(--color-success)' : 'var(--color-warning)'}}>
              {chartLocked ? '✓' : '⏳'}
            </div>
            <div className="stat-content">
              <div className="stat-value">{chartLocked ? '已鎖定' : '未建立'}</div>
              <div className="stat-label">命盤狀態</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{background: 'var(--color-strategic)'}}>🎯</div>
            <div className="stat-content">
              <div className="stat-value">戰略版</div>
              <div className="stat-label">進階功能</div>
            </div>
          </div>
        </div>

        {/* 資料完成度提示 */}
        {unlockedSystemCount < 6 && (
          <div className="card" style={{marginTop: 'var(--spacing-xl)'}}>
            <div className="card-header">
              <div className="card-title">📝 補充資料以解鎖更多系統</div>
              <div className="card-subtitle">
                每個命理系統需要不同的資料，您可以隨時補充
              </div>
            </div>
            <div className="card-body">
              <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)'}}>
                {Object.entries(systemRequirements).map(([id, sys]) => (
                  <span 
                    key={id}
                    style={{
                      padding: '6px 12px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '13px',
                      background: sys.available ? 'var(--color-success)' : 'var(--color-bg-tertiary)',
                      color: sys.available ? 'white' : 'var(--color-text-muted)'
                    }}
                  >
                    {sys.icon} {sys.name} {sys.available ? '✓' : ''}
                  </span>
                ))}
              </div>
            </div>
            <div className="card-footer">
              <button 
                className="btn btn-primary"
                onClick={() => setCurrentView('chart')}
              >
                補充個人資料
              </button>
            </div>
          </div>
        )}

        <div style={{marginTop: 'var(--spacing-2xl)'}}>
          <h2 style={{fontSize: '24px', fontWeight: 700, marginBottom: 'var(--spacing-lg)'}}>
            快速開始
          </h2>
          <div className="dashboard-grid">
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
            <div 
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
            </div>
          </div>
        </div>
      </div>
    </>
  )

  // Chart/Profile Creation View - 新設計：漸進式資料收集
  const renderChartView = () => {
    // 計算當前進度和可解鎖系統
    const hasName = !!chartForm.chinese_name
    const hasDate = !!chartForm.birth_date
    const hasTime = !!chartForm.birth_time
    const hasLocation = !!chartForm.birth_location
    
    // 根據已填資料計算可使用的系統
    const getAvailableSystems = () => {
      const systems = []
      systems.push({ id: 'tarot', name: '塔羅牌', icon: '🎴', ready: true })
      if (hasName) systems.push({ id: 'name', name: '姓名學', icon: '📝', ready: true })
      if (hasDate) systems.push({ id: 'numerology', name: '靈數學', icon: '🔢', ready: true })
      if (hasDate && hasTime) {
        systems.push({ id: 'ziwei', name: '紫微斗數', icon: '⭐', ready: true })
        systems.push({ id: 'bazi', name: '八字命理', icon: '🏛️', ready: true })
      }
      if (hasDate && hasTime && hasLocation) {
        systems.push({ id: 'astrology', name: '西洋占星', icon: '🌟', ready: true })
      }
      return systems
    }
    
    return (
      <>
        <div className="content-header">
          <h1 className="content-title">建立個人檔案</h1>
          <p className="content-subtitle">根據您提供的資料，系統會自動解鎖相應的命理分析</p>
        </div>
        <div className="content-body">
          {/* 新版進度指示器 - 5步驟 */}
          <div className="progress-wizard">
            {[
              { step: 1, label: '姓名', desc: '解鎖姓名學' },
              { step: 2, label: '出生日期', desc: '解鎖靈數學' },
              { step: 3, label: '出生時辰', desc: '解鎖紫微/八字' },
              { step: 4, label: '出生地點', desc: '解鎖占星' },
              { step: 5, label: '完成', desc: '開始使用' }
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

          {/* 已解鎖系統預覽 */}
          <div style={{marginBottom: 'var(--spacing-xl)', padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-lg)'}}>
            <div style={{fontSize: '14px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-text-muted)'}}>
              可使用的命理系統（{getAvailableSystems().length}/6）
            </div>
            <div style={{display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap'}}>
              {getAvailableSystems().map(sys => (
                <span key={sys.id} style={{
                  padding: '4px 12px',
                  background: 'var(--color-primary)',
                  color: 'white',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {sys.icon} {sys.name}
                </span>
              ))}
              {/* 待解鎖系統 */}
              {!hasName && (
                <span style={{padding: '4px 12px', background: 'var(--color-bg-tertiary)', color: 'var(--color-text-muted)', borderRadius: 'var(--radius-full)', fontSize: '13px'}}>
                  📝 姓名學（需要姓名）
                </span>
              )}
              {!hasDate && (
                <span style={{padding: '4px 12px', background: 'var(--color-bg-tertiary)', color: 'var(--color-text-muted)', borderRadius: 'var(--radius-full)', fontSize: '13px'}}>
                  🔢 靈數學（需要出生日期）
                </span>
              )}
              {(!hasDate || !hasTime) && (
                <>
                  <span style={{padding: '4px 12px', background: 'var(--color-bg-tertiary)', color: 'var(--color-text-muted)', borderRadius: 'var(--radius-full)', fontSize: '13px'}}>
                    ⭐ 紫微斗數（需要日期+時辰）
                  </span>
                  <span style={{padding: '4px 12px', background: 'var(--color-bg-tertiary)', color: 'var(--color-text-muted)', borderRadius: 'var(--radius-full)', fontSize: '13px'}}>
                    🏛️ 八字命理（需要日期+時辰）
                  </span>
                </>
              )}
              {(!hasDate || !hasTime || !hasLocation) && (
                <span style={{padding: '4px 12px', background: 'var(--color-bg-tertiary)', color: 'var(--color-text-muted)', borderRadius: 'var(--radius-full)', fontSize: '13px'}}>
                  🌟 西洋占星（需要日期+時辰+地點）
                </span>
              )}
            </div>
          </div>

          {/* Step 1: 姓名 */}
          {wizardStep === 1 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">步驟 1：姓名</div>
                <div className="card-subtitle">提供姓名可解鎖姓名學分析（五格剖象法）</div>
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
                  <label className="form-label">英文姓名（選填）</label>
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
                  className="btn btn-ghost"
                  onClick={() => {
                    // 允許跳過，直接完成（只有塔羅可用）
                    setWizardStep(5)
                  }}
                >
                  跳過（僅使用塔羅）
                </button>
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

          {/* Step 2: 出生日期 */}
          {wizardStep === 2 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">步驟 2：出生日期</div>
                <div className="card-subtitle">提供出生日期可解鎖靈數學分析</div>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">出生日期（國曆）</label>
                  <input 
                    type="date"
                    className="form-input"
                    value={chartForm.birth_date}
                    onChange={(e) => setChartForm({...chartForm, birth_date: e.target.value})}
                  />
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
                  className="btn btn-secondary"
                  onClick={() => setWizardStep(5)}
                >
                  完成（不需時辰/地點）
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => setWizardStep(3)}
                  disabled={!chartForm.birth_date}
                >
                  繼續填寫時辰
                </button>
              </div>
            </div>
          )}

          {/* Step 3: 出生時辰 */}
          {wizardStep === 3 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">步驟 3：出生時辰</div>
                <div className="card-subtitle">提供出生時辰可解鎖紫微斗數、八字命理</div>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">出生時間</label>
                  <input 
                    type="time"
                    className="form-input"
                    value={chartForm.birth_time}
                    onChange={(e) => setChartForm({...chartForm, birth_time: e.target.value})}
                  />
                  <div className="form-hint">請盡可能提供準確的時間，這對紫微斗數和八字命理至關重要</div>
                </div>
                <div style={{marginTop: 'var(--spacing-md)', padding: 'var(--spacing-md)', background: 'var(--color-info)', opacity: 0.7, borderRadius: 'var(--radius-md)', fontSize: '14px'}}>
                  <strong>💡 為什麼時辰很重要？</strong><br/>
                  紫微斗數的命宮位置和八字的時柱都取決於出生時辰。不同的時辰會產生完全不同的命盤結構。
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
                  className="btn btn-secondary"
                  onClick={() => setWizardStep(5)}
                >
                  完成（不需地點）
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => setWizardStep(4)}
                  disabled={!chartForm.birth_time}
                >
                  繼續填寫地點
                </button>
              </div>
            </div>
          )}

          {/* Step 4: 出生地點 */}
          {wizardStep === 4 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">步驟 4：出生地點</div>
                <div className="card-subtitle">提供出生地點可解鎖西洋占星術（本命盤）</div>
              </div>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">出生地點</label>
                  <input 
                    type="text"
                    className="form-input"
                    value={chartForm.birth_location}
                    onChange={(e) => setChartForm({...chartForm, birth_location: e.target.value})}
                    placeholder="例：台灣台北市"
                  />
                  <div className="form-hint">用於計算經緯度與真太陽時</div>
                </div>
              </div>
              <div className="card-footer">
                <button 
                  className="btn btn-ghost"
                  onClick={() => setWizardStep(3)}
                >
                  上一步
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => setWizardStep(5)}
                >
                  完成設定
                </button>
              </div>
            </div>
          )}

          {/* Step 5: 確認與儲存 */}
          {wizardStep === 5 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">確認您的資料</div>
                <div className="card-subtitle">
                  將解鎖 {getAvailableSystems().length} 個命理系統，並自動生成完整報告
                </div>
              </div>
              <div className="card-body">
                <div style={{display: 'grid', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)'}}>
                  {chartForm.chinese_name && <div><strong>姓名：</strong>{chartForm.chinese_name}{chartForm.english_name ? ` (${chartForm.english_name})` : ''}</div>}
                  {chartForm.gender && <div><strong>性別：</strong>{chartForm.gender}</div>}
                  {chartForm.birth_date && <div><strong>出生日期：</strong>{chartForm.birth_date}</div>}
                  {chartForm.birth_time && <div><strong>出生時辰：</strong>{chartForm.birth_time}</div>}
                  {chartForm.birth_location && <div><strong>出生地點：</strong>{chartForm.birth_location}</div>}
                  {!chartForm.chinese_name && !chartForm.birth_date && (
                    <div style={{color: 'var(--color-text-muted)'}}>
                      您尚未填寫任何資料，目前只能使用塔羅牌
                    </div>
                  )}
                </div>
                
                {/* 顯示將生成的報告 */}
                <div style={{padding: 'var(--spacing-md)', background: 'rgba(var(--color-success-rgb), 0.1)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-success)'}}>
                  <div style={{fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-success)'}}>
                    📊 將自動生成以下完整報告：
                  </div>
                  <div style={{display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap'}}>
                    {getAvailableSystems().map(sys => (
                      <span key={sys.id} style={{
                        padding: '4px 10px',
                        background: 'var(--color-success)',
                        color: 'white',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '13px'
                      }}>
                        {sys.icon} {sys.name}
                      </span>
                    ))}
                  </div>
                </div>
                
                {/* 時間提醒 */}
                <div style={{marginTop: 'var(--spacing-md)', padding: 'var(--spacing-md)', background: 'rgba(var(--color-info-rgb), 0.1)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-info)'}}>
                  <strong>⏱️ 預估時間：</strong>
                  系統將為您生成 {getAvailableSystems().filter(s => s.id !== 'tarot').length} 份完整命理報告，
                  大約需要 {Math.max(30, getAvailableSystems().filter(s => s.id !== 'tarot').length * 15)}-{Math.max(60, getAvailableSystems().filter(s => s.id !== 'tarot').length * 25)} 秒。
                  生成後可直接查看，無需再等待。
                </div>
              </div>
              <div className="card-footer">
                <button 
                  className="btn btn-ghost"
                  onClick={() => {
                    // 返回最後一個有資料的步驟
                    if (chartForm.birth_location) setWizardStep(4)
                    else if (chartForm.birth_time) setWizardStep(3)
                    else if (chartForm.birth_date) setWizardStep(2)
                    else setWizardStep(1)
                  }}
                >
                  返回修改
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={handleSaveAndAnalyze}
                  disabled={loading}
                >
                  💾 儲存資料並生成報告
                </button>
              </div>
            </div>
          )}

          {/* Step 6: AI 批次分析中 */}
          {wizardStep === 6 && (
            <div className="card" style={{minHeight: '450px', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: 'var(--spacing-2xl)'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)', width: '60px', height: '60px'}}></div>
                <div style={{fontSize: '20px', fontWeight: 600, marginBottom: 'var(--spacing-md)'}}>
                  🔮 AI 正在為您生成完整命理報告...
                </div>
                <div style={{color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-xl)'}}>
                  正在分析 {generationProgress.total} 個命理系統，請稍候
                </div>
                
                {/* 進度條 */}
                <div style={{
                  width: '100%', 
                  maxWidth: '400px', 
                  margin: '0 auto var(--spacing-lg)',
                  background: 'var(--color-bg-tertiary)',
                  borderRadius: 'var(--radius-full)',
                  height: '8px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${generationProgress.total > 0 ? (generationProgress.completed.length / generationProgress.total) * 100 : 0}%`,
                    height: '100%',
                    background: 'var(--color-primary)',
                    transition: 'width 0.5s ease',
                    borderRadius: 'var(--radius-full)'
                  }}></div>
                </div>
                
                {/* 系統進度 */}
                <div style={{display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap', justifyContent: 'center'}}>
                  {['name', 'numerology', 'bazi', 'ziwei', 'astrology'].map(sys => {
                    const isCompleted = generationProgress.completed.includes(sys)
                    const hasError = generationProgress.errors[sys]
                    const systemNames = {
                      name: '📝 姓名學',
                      numerology: '🔢 靈數學',
                      bazi: '🏛️ 八字',
                      ziwei: '⭐ 紫微',
                      astrology: '🌟 占星'
                    }
                    return (
                      <span key={sys} style={{
                        padding: '6px 12px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '13px',
                        background: isCompleted ? 'var(--color-success)' : hasError ? 'var(--color-error)' : 'var(--color-bg-tertiary)',
                        color: isCompleted || hasError ? 'white' : 'var(--color-text-muted)',
                        opacity: generationProgress.total === 0 ? 0.5 : 1
                      }}>
                        {isCompleted ? '✓ ' : hasError ? '✗ ' : ''}{systemNames[sys]}
                      </span>
                    )
                  })}
                </div>
                
                <div style={{marginTop: 'var(--spacing-xl)', fontSize: '14px', color: 'var(--color-text-muted)'}}>
                  💡 生成完成後，您可以直接查看各系統的完整報告，無需再等待
                </div>
              </div>
            </div>
          )}

          {/* Step 7: 預覽結果（保留作為備用） */}
          {wizardStep === 7 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">命盤預覽</div>
                <div className="card-subtitle">{chartSummary ? 'AI 排盤完成，請確認資訊' : '處理中...'}</div>
              </div>
              <div className="card-body">
                {!chartSummary ? (
                  <div style={{textAlign: 'center', padding: 'var(--spacing-2xl)'}}>
                    <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                    <div>正在處理命盤資料...</div>
                  </div>
                ) : (
                  <div style={{display: 'grid', gap: 'var(--spacing-lg)'}}>
                    {/* 紫微斗數 */}
                    {chartSummary.命宮 ? (
                      <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                        <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>⭐ 紫微斗數</div>
                        <div style={{display: 'grid', gap: 'var(--spacing-xs)'}}>
                          <div><strong>命宮：</strong>{chartSummary.命宮?.宮位 || '未知'}宮 - {chartSummary.命宮?.主星?.length > 0 ? chartSummary.命宮.主星.join('、') : '命無正曜'}{chartSummary.命宮?.輔星?.length > 0 ? ` (${chartSummary.命宮.輔星.join('、')})` : ''}</div>
                          {chartSummary.格局 && chartSummary.格局.length > 0 && <div><strong>格局：</strong>{chartSummary.格局.join('、')}</div>}
                          {chartSummary.五行局 && <div><strong>五行局：</strong>{chartSummary.五行局}</div>}
                        </div>
                      </div>
                    ) : (
                      <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                        <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>⭐ 命盤資料</div>
                        <div>命盤結構已生成，詳細資訊請鎖定後查看</div>
                      </div>
                    )}
                    
                    {/* 八字命理 */}
                    {chartSummary.八字 && (
                      <div style={{padding: 'var(--spacing-md)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)'}}>
                        <div style={{fontSize: '16px', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-primary)'}}>🏛️ 八字命理</div>
                        <div><strong>四柱：</strong>{chartSummary.八字.年柱} {chartSummary.八字.月柱} {chartSummary.八字.日柱} {chartSummary.八字.時柱}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="card-footer">
                <button 
                  className="btn btn-ghost"
                  onClick={() => {
                    setWizardStep(5)
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
                  {loading ? '鎖定中...' : '確認鎖定命盤'}
                </button>
              </div>
            </div>
          )}

          {/* Step 8: 完成 */}
          {wizardStep === 8 && (
            <div className="card" style={{textAlign: 'center', padding: 'var(--spacing-3xl)'}}>
              <div style={{fontSize: '64px', marginBottom: 'var(--spacing-lg)'}}>✨</div>
              <div style={{fontSize: '28px', fontWeight: 700, marginBottom: 'var(--spacing-md)'}}>
                設定完成！
              </div>
              <div style={{color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-lg)'}}>
                已解鎖 {unlockedSystemCount} 個命理系統
              </div>
              <div style={{display: 'flex', gap: 'var(--spacing-sm)', justifyContent: 'center', flexWrap: 'wrap', marginBottom: 'var(--spacing-2xl)'}}>
                {Object.entries(systemRequirements).filter(([_, s]) => s.available).map(([id, sys]) => (
                  <span key={id} style={{
                    padding: '8px 16px',
                    background: 'var(--color-primary)',
                    color: 'white',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '14px'
                  }}>
                    {sys.icon} {sys.name}
                  </span>
                ))}
              </div>
              <button 
                className="btn btn-primary btn-lg"
                onClick={() => setCurrentView('systems')}
              >
                開始探索六大系統
              </button>
            </div>
          )}
        </div>
      </>
    )
  }

  // Systems View - 新設計：根據已提供的資料顯示可用系統
  const renderSystemsView = () => {
    // 根據 userProfile 檢查系統可用性的輔助函數
    const getSystemStatus = (systemId) => {
      const req = systemRequirements[systemId]
      if (!req) return { available: false, reason: '未知系統' }
      if (req.available) return { available: true }
      
      // 根據需要的資料提供提示
      const missing = []
      if (req.needs.includes('chinese_name') && !userProfile.chinese_name) missing.push('姓名')
      if (req.needs.includes('birth_date') && !userProfile.birth_date) missing.push('出生日期')
      if (req.needs.includes('birth_time') && !userProfile.birth_time) missing.push('出生時辰')
      if (req.needs.includes('birth_location') && !userProfile.birth_location) missing.push('出生地點')
      
      return { available: false, reason: `需要：${missing.join('、')}` }
    }
    
    return (
      <>
        <div className="content-header">
          <h1 className="content-title">六大命理系統</h1>
          <p className="content-subtitle">
            已解鎖 {unlockedSystemCount}/6 個系統
            {unlockedSystemCount < 6 && (
              <span 
                style={{marginLeft: 'var(--spacing-md)', color: 'var(--color-primary)', cursor: 'pointer'}}
                onClick={() => setCurrentView('chart')}
              >
                → 補充資料以解鎖更多
              </span>
            )}
          </p>
        </div>
        <div className="content-body">
          <div className="dashboard-grid">
            {[
              { id: 'tarot', icon: '🎴', name: '塔羅牌', desc: '牌陣占卜與指引' },
              { id: 'name', icon: '📝', name: '姓名學', desc: '五格剖象法分析' },
              { id: 'numerology', icon: '🔢', name: '靈數學', desc: '生命靈數與天賦分析' },
              { id: 'ziwei', icon: '⭐', name: '紫微斗數', desc: 'LLM-First 排盤與格局分析' },
              { id: 'bazi', icon: '🏛️', name: '八字命理', desc: '四柱排盤與十神分析' },
              { id: 'astrology', icon: '🌟', name: '西洋占星術', desc: '本命盤與合盤分析' }
            ].map(system => {
              const status = getSystemStatus(system.id)
              const isLocked = !status.available
              
              return (
                <div 
                  key={system.id}
                  className={`card ${isLocked ? 'card-locked' : ''}`}
                  style={{
                    cursor: isLocked ? 'not-allowed' : 'pointer',
                    opacity: isLocked ? 0.6 : 1,
                    position: 'relative'
                  }}
                  onClick={() => {
                    if (isLocked) {
                      showToast(status.reason, 'warning')
                      return
                    }
                    // 塔羅不需要命盤
                    if (system.id === 'tarot') {
                      setCurrentSystem(system.id)
                      setCurrentView('system-detail')
                      return
                    }
                    // 紫微和八字需要鎖定命盤
                    if ((system.id === 'ziwei' || system.id === 'bazi') && !chartLocked) {
                      showToast('紫微斗數和八字需要先建立並鎖定命盤', 'warning')
                      setCurrentView('chart')
                      return
                    }
                    setCurrentSystem(system.id)
                    setCurrentView('system-detail')
                  }}
                >
                  {isLocked && (
                    <div style={{
                      position: 'absolute',
                      top: 'var(--spacing-sm)',
                      right: 'var(--spacing-sm)',
                      background: 'var(--color-bg-tertiary)',
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      fontSize: '12px'
                    }}>
                      🔒 未解鎖
                    </div>
                  )}
                  <div style={{fontSize: '48px', marginBottom: 'var(--spacing-md)'}}>{system.icon}</div>
                  <div className="card-title">{system.name}</div>
                  <div className="card-body">{system.desc}</div>
                  {isLocked && (
                    <div style={{
                      marginTop: 'var(--spacing-sm)',
                      fontSize: '12px',
                      color: 'var(--color-text-muted)'
                    }}>
                      {status.reason}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </>
    )
  }

  // Consult View (AI 命理顧問)
  const renderConsultView = () => {
    // 計算對話序號
    const getSessionNumber = (sessionId) => {
      const idx = consultSessions.findIndex(s => s.session_id === sessionId)
      return idx >= 0 ? consultSessions.length - idx : null
    }
    const currentSessionNum = consultSessionId ? getSessionNumber(consultSessionId) : null

    return (
    <>
      <div className="content-header">
        <h1 className="content-title">💬 AI 命理顧問諮詢</h1>
        <p className="content-subtitle">跨系統整合、回覆附依據（有所本）</p>
      </div>
      <div className="content-body">
        <div className="card consult-card">
          <div className="card-header" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div>
              <div className="card-title">對話</div>
              <div style={{fontSize: '12px', color: 'var(--color-text-muted)'}}>
                {currentSessionNum ? `對話 #${currentSessionNum}` : '新對話'}
              </div>
            </div>
            <div style={{display: 'flex', gap: 'var(--spacing-sm)'}}>
              <div style={{position: 'relative'}}>
                <button 
                  className="btn btn-ghost" 
                  onClick={() => setShowSessionList(!showSessionList)}
                  disabled={consultSending}
                >
                  📋 歷史 ({consultSessions.length})
                </button>
                {showSessionList && (
                  <div className="session-dropdown">
                    {consultSessions.length === 0 ? (
                      <div style={{padding: 'var(--spacing-md)', color: 'var(--color-text-muted)', fontSize: '13px'}}>
                        尚無對話歷史
                      </div>
                    ) : (
                      consultSessions.map((s, idx) => (
                        <div 
                          key={s.session_id}
                          className={`session-item ${s.session_id === consultSessionId ? 'active' : ''}`}
                          onClick={() => switchConsultSession(s.session_id)}
                        >
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
                            <div style={{flex: 1, minWidth: 0}}>
                              <div className="session-title" style={{
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}>
                                #{consultSessions.length - idx} {s.title || '未命名對話'}
                              </div>
                              <div className="session-time">{new Date(s.updated_at).toLocaleDateString('zh-TW')}</div>
                            </div>
                            <button
                              className="btn-icon-delete"
                              onClick={(e) => deleteConsultSession(s.session_id, e)}
                              title="刪除對話"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
              <button className="btn btn-secondary" onClick={startNewConsult} disabled={consultSending}>
                新對話
              </button>
            </div>
          </div>

          <div className="consult-messages">
            {consultMessages.map((m, idx) => {
              if (m.role === 'typing') {
                return (
                  <div key={m.id || idx} className="consult-message assistant">
                    <div className="consult-bubble">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )
              }

              const isUser = m.role === 'user'
              const citations = m.citations || []
              const expanded = !!consultExpanded[idx]
              return (
                <div key={idx} className={`consult-message ${isUser ? 'user' : 'assistant'}`}>
                  <div className="consult-bubble">
                    {isUser ? (
                      <div style={{whiteSpace: 'pre-wrap'}}>{m.content}</div>
                    ) : (
                      <div className="markdown-content">
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                      </div>
                    )}

                    {!isUser && (
                      <div className="consult-meta">
                        {Array.isArray(m.used_systems) && m.used_systems.length > 0 && (
                          <div>系統：{m.used_systems.map(getSystemNameZh).join('、')}</div>
                        )}
                        {typeof m.confidence === 'number' && (
                          <div>信心：{Math.round(m.confidence * 100)}%</div>
                        )}
                      </div>
                    )}

                    {!isUser && citations.length > 0 && (
                      <div style={{marginTop: 'var(--spacing-sm)'}}>
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => setConsultExpanded(prev => ({ ...prev, [idx]: !prev[idx] }))}
                        >
                          {expanded ? '收起依據' : `依據（${citations.length}）`}
                        </button>
                        {expanded && (
                          <div className="consult-citations">
                            {citations.map((c, i) => (
                              <div key={i} className="consult-citation">
                                <div className="consult-citation-title">
                                  [{getSystemNameZh(c.system)}] {c.title}
                                </div>
                                <div className="consult-citation-excerpt">{c.excerpt}</div>
                                {c.path_readable && (
                                  <div style={{fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '4px'}}>
                                    📍 {c.path_readable}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {!isUser && Array.isArray(m.next_steps) && m.next_steps.length > 0 && (
                      <div className="consult-next">
                        <div className="consult-next-title">下一步建議</div>
                        <div className="consult-next-items">
                          {m.next_steps.slice(0, 3).map((s, i) => (
                            <button
                              key={i}
                              className="chip"
                              onClick={() => setConsultInput(s)}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          <div className="consult-input">
            <textarea
              className="form-input"
              rows={3}
              value={consultInput}
              onChange={(e) => setConsultInput(e.target.value)}
              placeholder="輸入你想問的問題…（例如：我適合轉職嗎？這段關係該怎麼做？）"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  sendConsult()
                }
              }}
            />
            <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--spacing-sm)'}}>
              <button className="btn btn-primary" onClick={sendConsult} disabled={consultSending || !consultInput.trim()}>
                {consultSending ? '思考中…' : '送出'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )}

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
                <div className="card-body" style={{whiteSpace: 'pre-wrap'}}>
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

  // System Detail View (單一系統詳細分析) - 新設計：優先顯示預計算報告
  const renderSystemDetailView = () => {
    const getSystemInfo = (id) => {
      const systems = {
        ziwei: { icon: '⭐', name: '紫微斗數', fullName: '紫微斗數完整命盤分析' },
        bazi: { icon: '🏛️', name: '八字命理', fullName: '八字命理完整分析' },
        astrology: { icon: '🌟', name: '西洋占星術', fullName: '西洋占星本命盤分析' },
        numerology: { icon: '🔢', name: '靈數學', fullName: '靈數學生命藍圖分析' },
        name: { icon: '📝', name: '姓名學', fullName: '姓名學五格剖象分析' },
        tarot: { icon: '🎴', name: '塔羅牌', fullName: '塔羅牌占卜' }
      }
      return systems[id] || { icon: '❓', name: '未知系統', fullName: '未知系統' }
    }

    const systemInfo = getSystemInfo(currentSystem)
    
    // 優先從預計算報告取得資料
    const precomputedReport = precomputedReports[currentSystem]
    const hasPrecomputed = precomputedReport && precomputedReport.report
    
    // 取得報告內容
    const getReportContent = () => {
      if (hasPrecomputed) {
        return precomputedReport.report.analysis || precomputedReport.report.interpretation || null
      }
      if (systemData) {
        return systemData.analysis || systemData.interpretation || null
      }
      return null
    }
    
    const reportContent = getReportContent()

    return (
      <>
        <div className="content-header">
          <button 
            className="btn btn-ghost" 
            onClick={() => setCurrentView('systems')}
            style={{marginBottom: 'var(--spacing-md)'}}
          >
            ← 返回系統列表
          </button>
          <h1 className="content-title">{systemInfo.icon} {systemInfo.fullName}</h1>
          <p className="content-subtitle">
            {hasPrecomputed ? (
              <span style={{color: 'var(--color-success)'}}>
                ✓ 報告已生成於 {new Date(precomputedReport.created_at).toLocaleDateString('zh-TW')}
              </span>
            ) : '詳細分析報告'}
          </p>
        </div>
        <div className="content-body">
          {/* 塔羅特殊處理 */}
          {currentSystem === 'tarot' && !tarotReading && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">🎴 塔羅牌占卜</div>
                <div className="card-subtitle">
                  {tarotAdvancedMode ? '進階模式 - 自選牌陣' : '引導模式 - 根據問題智能推薦'}
                </div>
              </div>
              <div className="card-body">
                {/* 模式切換 */}
                <div style={{
                  display: 'flex', 
                  justifyContent: 'flex-end', 
                  marginBottom: 'var(--spacing-md)',
                  paddingBottom: 'var(--spacing-md)',
                  borderBottom: '1px solid var(--color-border)'
                }}>
                  <label style={{display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', cursor: 'pointer'}}>
                    <span style={{fontSize: '0.875rem', color: 'var(--color-text-secondary)'}}>
                      {tarotAdvancedMode ? '🔧 進階模式' : '✨ 引導模式'}
                    </span>
                    <button
                      className={`btn btn-ghost`}
                      onClick={() => setTarotAdvancedMode(!tarotAdvancedMode)}
                      style={{fontSize: '0.75rem', padding: '4px 8px'}}
                    >
                      切換
                    </button>
                  </label>
                </div>

                {/* 引導模式：選擇問題類型 */}
                {!tarotAdvancedMode && (
                  <div style={{marginBottom: 'var(--spacing-lg)'}}>
                    <label style={{display: 'block', marginBottom: 'var(--spacing-sm)', fontWeight: 600}}>
                      您想問什麼類型的問題？
                    </label>
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-sm)'}}>
                      {[
                        { value: 'daily', label: '🌅 今日運勢', desc: '快速指引', spread: 'single', context: 'general' },
                        { value: 'trend', label: '📈 發展趨勢', desc: '過去→現在→未來', spread: 'three_card', context: 'general' },
                        { value: 'love', label: '💕 感情問題', desc: '關於愛情、關係', spread: 'three_card', context: 'love' },
                        { value: 'relationship', label: '👫 兩人關係', desc: '分析你與對方', spread: 'relationship', context: 'love' },
                        { value: 'career', label: '💼 工作事業', desc: '職場、發展', spread: 'three_card', context: 'career' },
                        { value: 'decision', label: '🤔 二選一抉擇', desc: 'A還是B？', spread: 'decision', context: 'general' },
                        { value: 'deep', label: '🔮 深度剖析', desc: '複雜問題全面分析', spread: 'celtic_cross', context: 'general' }
                      ].map(option => (
                        <button
                          key={option.value}
                          className={`btn ${tarotForm.context === option.context && tarotForm.spread_type === option.spread ? 'btn-primary' : 'btn-outline'}`}
                          onClick={() => setTarotForm(prev => ({ 
                            ...prev, 
                            spread_type: option.spread, 
                            context: option.context 
                          }))}
                          style={{
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'flex-start',
                            padding: 'var(--spacing-md)',
                            height: 'auto',
                            textAlign: 'left'
                          }}
                        >
                          <span style={{fontSize: '1rem', marginBottom: '4px'}}>{option.label}</span>
                          <span style={{fontSize: '0.75rem', opacity: 0.7}}>{option.desc}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* 進階模式：牌陣選擇 */}
                {tarotAdvancedMode && (
                  <>
                    <div style={{marginBottom: 'var(--spacing-lg)'}}>
                      <label style={{display: 'block', marginBottom: 'var(--spacing-sm)', fontWeight: 600}}>
                        選擇牌陣
                      </label>
                      <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)'}}>
                        {[
                          { value: 'single', label: '單牌', desc: '簡單問題', cards: 1 },
                          { value: 'three_card', label: '三牌陣', desc: '最常用', cards: 3, recommended: true },
                          { value: 'celtic_cross', label: '凱爾特十字', desc: '深度複雜問題', cards: 10 },
                          { value: 'relationship', label: '關係牌陣', desc: '兩人互動', cards: 6 },
                          { value: 'decision', label: '抉擇牌陣', desc: 'A vs B', cards: 7 }
                        ].map(spread => (
                          <button
                            key={spread.value}
                            className={`btn ${tarotForm.spread_type === spread.value ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => setTarotForm(prev => ({ ...prev, spread_type: spread.value }))}
                            style={{flex: '1 1 auto', minWidth: '120px', position: 'relative'}}
                          >
                            {spread.recommended && (
                              <span style={{
                                position: 'absolute', top: '-8px', right: '-8px',
                                background: 'var(--color-success)', color: 'white',
                                fontSize: '0.6rem', padding: '2px 6px', borderRadius: '10px'
                              }}>推薦</span>
                            )}
                            {spread.label}
                            <span style={{display: 'block', fontSize: '0.75rem', opacity: 0.8}}>
                              {spread.cards}張 · {spread.desc}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                    
                    {/* 問題領域 */}
                    <div style={{marginBottom: 'var(--spacing-lg)'}}>
                      <label style={{display: 'block', marginBottom: 'var(--spacing-sm)', fontWeight: 600}}>
                        問題領域
                      </label>
                      <div style={{display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-sm)'}}>
                        {[
                          { value: 'general', label: '綜合' },
                          { value: 'love', label: '❤️ 感情' },
                          { value: 'career', label: '💼 事業' },
                          { value: 'finance', label: '💰 財運' },
                          { value: 'health', label: '🏥 健康' }
                        ].map(ctx => (
                          <button
                            key={ctx.value}
                            className={`btn ${tarotForm.context === ctx.value ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => setTarotForm(prev => ({ ...prev, context: ctx.value }))}
                          >
                            {ctx.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}
                
                {/* 問題輸入 */}
                <div style={{marginBottom: 'var(--spacing-lg)'}}>
                  <label style={{display: 'block', marginBottom: 'var(--spacing-sm)', fontWeight: 600}}>
                    您的問題（選填，但建議填寫以獲得更精準解讀）
                  </label>
                  <textarea
                    className="input"
                    placeholder="請靜心默念您的問題，或在此輸入...&#10;例如：我和他的關係會怎麼發展？這份工作適合我嗎？"
                    value={tarotForm.question}
                    onChange={(e) => setTarotForm(prev => ({ ...prev, question: e.target.value }))}
                    style={{width: '100%', minHeight: '80px', resize: 'vertical'}}
                  />
                </div>
                
                <button 
                  className="btn btn-primary"
                  onClick={handleTarotReading}
                  disabled={tarotLoading}
                  style={{width: '100%', padding: 'var(--spacing-md)'}}
                >
                  {tarotLoading ? (
                    <>
                      <span className="spinner" style={{width: '16px', height: '16px', marginRight: '8px'}}></span>
                      占卜中，請稍候...
                    </>
                  ) : '🔮 開始占卜'}
                </button>
              </div>
            </div>
          )}
          
          {/* 塔羅占卜結果 */}
          {currentSystem === 'tarot' && tarotReading && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">🎴 {tarotReading.spread_name}</div>
                <div className="card-subtitle">
                  {tarotReading.question || '一般占卜'} • {
                    {general: '綜合', love: '感情', career: '事業', finance: '財運', health: '健康'}[tarotReading.context]
                  }
                </div>
              </div>
              <div className="card-body">
                {/* 抽到的牌 - 帶圖片 */}
                <div style={{
                  marginBottom: 'var(--spacing-xl)',
                  padding: 'var(--spacing-lg)',
                  background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
                  borderRadius: 'var(--radius-lg)',
                  border: '1px solid rgba(255,215,0,0.3)'
                }}>
                  <div style={{
                    fontWeight: 600, 
                    marginBottom: 'var(--spacing-lg)', 
                    color: '#ffd700',
                    textAlign: 'center',
                    fontSize: '1.2rem'
                  }}>
                    🃏 您抽到的牌
                  </div>
                  <div style={{
                    display: 'flex', 
                    flexWrap: 'wrap', 
                    justifyContent: 'center',
                    gap: 'var(--spacing-lg)'
                  }}>
                    {tarotReading.cards?.map((card, idx) => {
                      const cardImage = getTarotCardImage(card.name_en || card.name)
                      console.log('Card:', card.name_en, '-> Image:', cardImage)
                      return (
                        <div key={idx} style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          maxWidth: '140px'
                        }}>
                          {/* 位置標籤 */}
                          <div style={{
                            fontSize: '0.75rem', 
                            color: 'rgba(255,255,255,0.7)', 
                            marginBottom: 'var(--spacing-xs)',
                            textAlign: 'center'
                          }}>
                            {card.position}
                          </div>
                          
                          {/* 牌卡圖片 */}
                          <div style={{
                            position: 'relative',
                            width: '120px',
                            height: '200px',
                            borderRadius: '8px',
                            overflow: 'hidden',
                            boxShadow: card.is_reversed 
                              ? '0 0 20px rgba(255,100,100,0.5)' 
                              : '0 0 20px rgba(255,215,0,0.3)',
                            border: card.is_reversed 
                              ? '2px solid #ff6b6b' 
                              : '2px solid rgba(255,215,0,0.5)',
                            transform: card.is_reversed ? 'rotate(180deg)' : 'none',
                            transition: 'transform 0.3s ease'
                          }}>
                            {cardImage ? (
                              <img 
                                src={cardImage} 
                                alt={card.name_zh || card.name}
                                style={{
                                  width: '100%',
                                  height: '100%',
                                  objectFit: 'cover'
                                }}
                                onError={(e) => {
                                  e.target.style.display = 'none'
                                  e.target.nextSibling.style.display = 'flex'
                                }}
                              />
                            ) : null}
                            <div style={{
                              display: cardImage ? 'none' : 'flex',
                              width: '100%',
                              height: '100%',
                              background: 'linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%)',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexDirection: 'column',
                              padding: '10px'
                            }}>
                              <span style={{fontSize: '2rem', marginBottom: '8px'}}>🎴</span>
                              <span style={{
                                color: '#ffd700', 
                                fontSize: '0.75rem', 
                                textAlign: 'center',
                                transform: card.is_reversed ? 'rotate(180deg)' : 'none'
                              }}>
                                {card.name_zh || card.name}
                              </span>
                            </div>
                          </div>
                          
                          {/* 牌名 */}
                          <div style={{
                            marginTop: 'var(--spacing-sm)',
                            fontWeight: 600,
                            fontSize: '0.9rem',
                            color: '#fff',
                            textAlign: 'center'
                          }}>
                            {card.name_zh || card.name}
                          </div>
                          
                          {/* 逆位標記 */}
                          {card.is_reversed && (
                            <div style={{
                              fontSize: '0.7rem', 
                              color: '#ff6b6b', 
                              marginTop: '2px',
                              background: 'rgba(255,107,107,0.2)',
                              padding: '2px 8px',
                              borderRadius: '10px'
                            }}>
                              ⟲ 逆位
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
                
                {/* AI 解讀 */}
                <div style={{
                  padding: 'var(--spacing-lg)',
                  lineHeight: 1.8,
                  whiteSpace: 'pre-wrap',
                  background: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: 'var(--spacing-lg)'
                }}>
                  <div style={{
                    fontWeight: 600, 
                    marginBottom: 'var(--spacing-md)', 
                    color: 'var(--color-primary)',
                    fontSize: '1.1rem'
                  }}>
                    📖 牌義解讀
                  </div>
                  {tarotReading.interpretation}
                </div>
                
                {/* 重新占卜按鈕 */}
                <div style={{marginTop: 'var(--spacing-lg)', textAlign: 'center'}}>
                  <button 
                    className="btn btn-outline"
                    onClick={resetTarotReading}
                  >
                    🔄 重新占卜
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* 有報告時顯示 */}
          {reportContent && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">📊 完整分析報告</div>
                {hasPrecomputed && (
                  <div className="card-subtitle">
                    此報告根據您的個人資料預先生成，可隨時查閱
                  </div>
                )}
              </div>
              <div className="card-body">
                {/* 紫微斗數可視化命盤 */}
                {currentSystem === 'ziwei' && chartSummary && (
                  <ZiweiChart structure={chartSummary} />
                )}
                
                {/* 報告內容 */}
                <div style={{
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.8',
                  fontSize: '15px'
                }}>
                  {currentSystem === 'ziwei' 
                    ? sanitizeReportContent(
                        reportContent
                          .replace(/```json[\s\S]*?```/g, '')
                          .replace(/{[\s\S]*"chart_structure"[\s\S]*?}/g, '')
                      )
                    : sanitizeReportContent(reportContent)}
                </div>
              </div>
              <div className="card-footer">
                <button 
                  className="btn btn-ghost"
                  onClick={() => {
                    // 複製到剪貼簿
                    const filteredContent = currentSystem === 'ziwei'
                      ? sanitizeReportContent(
                          reportContent
                            .replace(/```json[\s\S]*?```/g, '')
                            .replace(/{[\s\S]*"chart_structure"[\s\S]*?}/g, '')
                        )
                      : sanitizeReportContent(reportContent)
                    navigator.clipboard.writeText(filteredContent)
                    showToast('報告已複製到剪貼簿', 'success')
                  }}
                >
                  📋 複製報告
                </button>
              </div>
            </div>
          )}
          
          {/* 載入中 */}
          {systemLoading && !reportContent && (
            <div className="card" style={{minHeight: '400px', display: 'grid', placeItems: 'center'}}>
              <div style={{textAlign: 'center'}}>
                <div className="spinner" style={{margin: '0 auto var(--spacing-lg)'}}></div>
                <div>正在分析...</div>
              </div>
            </div>
          )}
          
          {/* 無報告 */}
          {!systemLoading && !reportContent && currentSystem !== 'tarot' && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">尚無分析報告</div>
              </div>
              <div className="card-body">
                <p>此系統的報告尚未生成。</p>
                <p style={{marginTop: 'var(--spacing-md)'}}>
                  請先<span 
                    style={{color: 'var(--color-primary)', cursor: 'pointer', textDecoration: 'underline'}}
                    onClick={() => setCurrentView('chart')}
                  >補充個人資料</span>以生成報告。
                </p>
              </div>
            </div>
          )}
        </div>
      </>
    )
  }

  const sanitizeReportContent = (content) => {
    if (!content) return ''
    return content
      .replace(/\*\*/g, '')
      .replace(/^#{1,6}\s*/gm, '')
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
  // Sidebar Navigation - 新設計：顯示解鎖進度
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
            <div className="nav-icon">📋</div>
            <div>個人檔案</div>
            {unlockedSystemCount < 6 && <div className="nav-badge">{unlockedSystemCount}/6</div>}
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
          <div className="nav-label">命理系統（{unlockedSystemCount}/6 已解鎖）</div>
          <div 
            className={`nav-item ${currentView === 'systems' ? 'active' : ''}`}
            onClick={() => setCurrentView('systems')}
          >
            <div className="nav-icon">📚</div>
            <div>六大系統</div>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-label">進階功能</div>
          <div 
            className={`nav-item strategic ${currentView === 'strategic' ? 'active' : ''}`}
            onClick={() => setCurrentView('strategic')}
          >
            <div className="nav-icon">🎯</div>
            <div>戰略側寫</div>
            <div className="nav-badge">NEW</div>
          </div>

          <div 
            className={`nav-item ${currentView === 'consult' ? 'active' : ''}`}
            onClick={() => setCurrentView('consult')}
          >
            <div className="nav-icon">💬</div>
            <div>AI 諮詢</div>
          </div>
        </div>

        <div className="nav-section">
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
            {currentView === 'consult' && renderConsultView()}
            {currentView === 'strategic' && renderStrategicView()}
            {currentView === 'settings' && renderSettingsView()}
          </div>
        </div>
      )}

      {renderAuthModal()}
      {renderToast()}
    </div>
  )
}

export default App
