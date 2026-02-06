import { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react'

/**
 * AetheriaContext - 統一狀態管理
 * 
 * 作為單一真相來源 (Single Source of Truth)，管理：
 * - 使用者資料 (profile, birthInfo)
 * - 命盤狀態 (chartLocked, chartSummary, chartData)
 * - 對話狀態 (messages, currentSession)
 * - 系統洞察 (systemAnalysis)
 */

const AetheriaContext = createContext(null)

export function AetheriaProvider({ children, apiBase, token }) {
  // ========== User State ==========
  const [profile, setProfile] = useState(null)
  const [birthInfo, setBirthInfo] = useState(null)

  // ========== Chart State ==========
  const [chartLocked, setChartLocked] = useState(false)
  const [chartSummary, setChartSummary] = useState(null)
  const [systemAnalysis, setSystemAnalysis] = useState({})
  const [overviewData, setOverviewData] = useState(null)

  // ========== Chat State ==========
  const [messages, setMessages] = useState([])
  const [currentSession, setCurrentSession] = useState(null)

  // ========== Computed State ==========
  const chartData = useMemo(() => {
    if (!chartSummary) return null
    return {
      ziwei: chartSummary.ziwei,
      bazi: chartSummary.bazi,
      astrology: chartSummary.astrology,
      numerology: chartSummary.numerology,
      name: chartSummary.name,
      birth_date: chartSummary.birth_date,
      birth_time: chartSummary.birth_time,
      birth_location: chartSummary.birth_location,
      available_systems: chartSummary.available_systems || []
    }
  }, [chartSummary])

  const isAuthenticated = useMemo(() => !!token && !!profile, [token, profile])

  // ========== API Helpers ==========
  const authHeaders = useMemo(() => {
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    return headers
  }, [token])

  const apiCall = useCallback(async (path, payload = null, method = 'POST') => {
    try {
      const options = {
        method: payload ? method : 'GET',
        headers: authHeaders
      }
      if (payload) {
        options.body = JSON.stringify(payload)
      }
      const response = await fetch(`${apiBase}${path}`, options)
      let data = null
      try {
        data = await response.json()
      } catch {
        data = null
      }
      if (!response.ok) {
        const msg = (data && (data.message || data.error)) || `API ${response.status}`
        const err = new Error(msg)
        err.status = response.status
        throw err
      }
      return data
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }, [apiBase, authHeaders])

  // ========== User Actions ==========
  const fetchProfile = useCallback(async () => {
    if (!token) return
    try {
      const data = await apiCall('/api/profile', null, 'GET')
      setProfile(data.profile)
      setBirthInfo(data.birth_info)
      return data
    } catch (error) {
      console.warn('載入使用者資料失敗:', error)
      throw error
    }
  }, [token, apiCall])

  const updateProfile = useCallback(async (updates) => {
    if (!profile?.user_id) throw new Error('No user ID')
    try {
      const data = await apiCall('/api/profile/update', {
        user_id: profile.user_id,
        ...updates
      })
      setProfile(prev => ({ ...prev, ...updates }))
      
      // Inject system event into chat
      const systemEvent = {
        id: `event-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        type: 'system_event',
        role: 'system',
        content: '個人資料已更新',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, systemEvent])
      
      return data
    } catch (error) {
      console.error('更新個人資料失敗:', error)
      throw error
    }
  }, [profile?.user_id, apiCall])

  // ========== Chart Actions ==========
  const checkChartLock = useCallback(async () => {
    if (!profile?.user_id) return
    try {
      const data = await apiCall(`/api/reports/get?user_id=${encodeURIComponent(profile.user_id)}`, null, 'GET')
      
      if (!data || !data.reports || Object.keys(data.reports).length === 0) {
        setChartLocked(false)
        setChartSummary(null)
        return
      }

      const reports = data?.reports || {}
      const available = data?.available_systems || Object.keys(reports)
      const reportsGenerated = {}
      for (const key of available) reportsGenerated[key] = true

      setChartLocked(true)
      setChartSummary({
        reports_generated: reportsGenerated,
        generation_errors: {},
        available_systems: available,
        birth_date: birthInfo?.birth_date || profile?.birth_date,
        birth_time: birthInfo?.birth_time || profile?.birth_time,
        birth_location: birthInfo?.birth_location || profile?.birth_location,
        ziwei: reports.ziwei?.report?.chart_structure || null,
        bazi: reports.bazi?.report?.bazi_chart || null,
        numerology: reports.numerology?.report?.profile || null,
        name: reports.name?.report?.five_grids || reports.name?.report || null,
        astrology: reports.astrology?.report?.natal_chart || null
      })
    } catch (error) {
      console.warn('檢查命盤鎖定狀態失敗:', error)
    }
  }, [profile?.user_id, profile?.birth_date, profile?.birth_time, profile?.birth_location, birthInfo, apiCall])

  const lockChart = useCallback(async (chartData) => {
    setChartLocked(true)
    setChartSummary(chartData)
    
    // Inject system event into chat
    const systemEvent = {
      id: `event-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'system_event',
      role: 'system',
      content: '命盤已生成並鎖定',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, systemEvent])
  }, [setMessages])

  const unlockChart = useCallback(() => {
    setChartLocked(false)
    setChartSummary(null)
    setSystemAnalysis({})
    setOverviewData(null)
    
    // Inject system event into chat
    const systemEvent = {
      id: `event-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'system_event',
      role: 'system',
      content: '命盤已解鎖',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, systemEvent])
  }, [])

  const updateSystemAnalysis = useCallback((system, data) => {
    setSystemAnalysis(prev => ({ ...prev, [system]: data }))
  }, [])

  // ========== Chat Actions ==========
  const sendMessage = useCallback(async (content, options = {}) => {
    if (!token) throw new Error('Not authenticated')

    const userMessage = {
      id: `user-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'text',
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])

    // If chart just locked, inject context
    if (options.chartJustLocked && chartSummary) {
      const contextEvent = {
        id: `event-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        type: 'system_event',
        role: 'system',
        content: '已將命盤資料注入對話上下文',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, contextEvent])
    }

    return userMessage
  }, [token, chartSummary])

  const clearMessages = useCallback(() => {
    setMessages([])
    setCurrentSession(null)
  }, [])

  // ========== Auto-fetch on mount ==========
  useEffect(() => {
    if (token && !profile) {
      fetchProfile().catch(() => {
        // Silent fail on initial load
      })
    }
  }, [token, profile, fetchProfile])

  useEffect(() => {
    if (profile && !chartLocked) {
      checkChartLock().catch(() => {
        // Silent fail on initial check
      })
    }
  }, [profile, chartLocked, checkChartLock])

  // ========== Context Value ==========
  const value = {
    // State
    profile,
    birthInfo,
    chartLocked,
    chartSummary,
    chartData,
    systemAnalysis,
    overviewData,
    messages,
    currentSession,
    isAuthenticated,

    // User Actions
    setProfile,
    setBirthInfo,
    fetchProfile,
    updateProfile,

    // Chart Actions
    setChartLocked,
    setChartSummary,
    checkChartLock,
    lockChart,
    unlockChart,
    updateSystemAnalysis,
    setOverviewData,

    // Chat Actions
    setMessages,
    setCurrentSession,
    sendMessage,
    clearMessages,

    // API Helper
    apiCall
  }

  return (
    <AetheriaContext.Provider value={value}>
      {children}
    </AetheriaContext.Provider>
  )
}

/**
 * useAetheriaContext - Hook to access Aetheria context
 */
// eslint-disable-next-line react-refresh/only-export-components
export function useAetheriaContext() {
  const context = useContext(AetheriaContext)
  if (!context) {
    throw new Error('useAetheriaContext must be used within AetheriaProvider')
  }
  return context
}
