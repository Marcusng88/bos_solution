/**
 * Enhanced React hook for content planning functionality
 * Provides advanced state management, caching, and error handling
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useUser } from '@clerk/nextjs'
import { 
  contentPlanningAPI, 
  type DashboardData, 
  type SupportedOptions,
  type ContentGenerationRequest,
  type ContentGenerationResponse 
} from '@/lib/content-planning-api'

export interface UseEnhancedContentPlanningOptions {
  autoLoad?: boolean
  cacheTimeout?: number // Cache timeout in milliseconds
  retryAttempts?: number
  debounceMs?: number
  enableOfflineMode?: boolean
}

interface CacheEntry<T> {
  data: T
  timestamp: number
  expiresAt: number
}

interface LoadingState {
  dashboardData: boolean
  supportedOptions: boolean
  contentGeneration: boolean
  competitorAnalysis: boolean
  hashtagResearch: boolean
  strategyGeneration: boolean
  calendarGeneration: boolean
  contentGaps: boolean
}

interface RetryState {
  count: number
  lastAttempt: number
}

export function useEnhancedContentPlanning(options: UseEnhancedContentPlanningOptions = {}) {
  const { 
    autoLoad = true, 
    cacheTimeout = 5 * 60 * 1000, // 5 minutes
    retryAttempts = 3,
    debounceMs = 300,
    enableOfflineMode = false
  } = options
  
  const { user } = useUser()

  // State management
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [supportedOptions, setSupportedOptions] = useState<SupportedOptions | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState('technology')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loadingStates, setLoadingStates] = useState<LoadingState>({
    dashboardData: false,
    supportedOptions: false,
    contentGeneration: false,
    competitorAnalysis: false,
    hashtagResearch: false,
    strategyGeneration: false,
    calendarGeneration: false,
    contentGaps: false
  })

  // Refs for caching and debouncing
  const cacheRef = useRef<Map<string, CacheEntry<any>>>(new Map())
  const retryStateRef = useRef<Map<string, RetryState>>(new Map())
  const timeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map())
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map())

  // Network status
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true)

  // Network status listeners
  useEffect(() => {
    if (typeof window === 'undefined') return

    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Cache utilities
  const getCachedData = useCallback(<T,>(key: string): T | null => {
    const cached = cacheRef.current.get(key)
    if (!cached) return null
    
    if (Date.now() > cached.expiresAt) {
      cacheRef.current.delete(key)
      return null
    }
    
    return cached.data
  }, [])

  const setCachedData = useCallback(<T,>(key: string, data: T) => {
    const timestamp = Date.now()
    cacheRef.current.set(key, {
      data,
      timestamp,
      expiresAt: timestamp + cacheTimeout
    })
  }, [cacheTimeout])

  // Error handling utilities
  const setError = useCallback((operation: string, error: string | null) => {
    setErrors(prev => {
      if (error === null) {
        const { [operation]: _, ...rest } = prev
        return rest
      }
      return { ...prev, [operation]: error }
    })
  }, [])

  const clearError = useCallback((operation: string) => {
    setError(operation, null)
  }, [setError])

  const clearAllErrors = useCallback(() => {
    setErrors({})
  }, [])

  // Loading state utilities
  const setLoadingState = useCallback((operation: keyof LoadingState, loading: boolean) => {
    setLoadingStates(prev => ({ ...prev, [operation]: loading }))
  }, [])

  // Retry utilities
  const shouldRetry = useCallback((operation: string, error: any): boolean => {
    const retryState = retryStateRef.current.get(operation) || { count: 0, lastAttempt: 0 }
    
    // Don't retry if we've exceeded max attempts
    if (retryState.count >= retryAttempts) return false
    
    // Don't retry client errors (4xx) except for 429 (rate limit)
    if (error?.status >= 400 && error?.status < 500 && error?.status !== 429) return false
    
    // Don't retry if offline and offline mode is disabled
    if (!isOnline && !enableOfflineMode) return false
    
    return true
  }, [retryAttempts, isOnline, enableOfflineMode])

  const updateRetryState = useCallback((operation: string) => {
    const current = retryStateRef.current.get(operation) || { count: 0, lastAttempt: 0 }
    retryStateRef.current.set(operation, {
      count: current.count + 1,
      lastAttempt: Date.now()
    })
  }, [])

  const resetRetryState = useCallback((operation: string) => {
    retryStateRef.current.delete(operation)
  }, [])

  // Abort controller utilities
  const createAbortController = useCallback((operation: string) => {
    // Cancel existing operation
    const existing = abortControllersRef.current.get(operation)
    if (existing) {
      existing.abort()
    }

    const controller = new AbortController()
    abortControllersRef.current.set(operation, controller)
    return controller
  }, [])

  const cleanupAbortController = useCallback((operation: string) => {
    abortControllersRef.current.delete(operation)
  }, [])

  // Enhanced API call wrapper with retry logic
  const enhancedApiCall = useCallback(async <T,>(
    operation: string,
    apiCall: (signal?: AbortSignal) => Promise<T>,
    useCache = true
  ): Promise<T> => {
    // Check cache first
    if (useCache) {
      const cached = getCachedData<T>(operation)
      if (cached) return cached
    }

    // Check if offline and offline mode is disabled
    if (!isOnline && !enableOfflineMode) {
      throw new Error('No internet connection available')
    }

    setLoadingState(operation as keyof LoadingState, true)
    clearError(operation)

    let lastError: any
    const maxRetries = retryAttempts + 1 // Initial attempt + retries

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const controller = createAbortController(operation)
        const result = await apiCall(controller.signal)
        
        // Success - cache the result and reset retry state
        if (useCache) {
          setCachedData(operation, result)
        }
        resetRetryState(operation)
        cleanupAbortController(operation)
        setLoadingState(operation as keyof LoadingState, false)
        
        return result
      } catch (error: any) {
        lastError = error
        cleanupAbortController(operation)

        // If this was an abort, don't retry
        if (error.name === 'AbortError') {
          break
        }

        // Check if we should retry
        if (attempt < maxRetries && shouldRetry(operation, error)) {
          updateRetryState(operation)
          
          // Exponential backoff with jitter
          const baseDelay = Math.min(1000 * Math.pow(2, attempt - 1), 10000)
          const jitter = Math.random() * 1000
          const delay = baseDelay + jitter
          
          console.warn(`API call failed (attempt ${attempt}/${maxRetries}), retrying in ${delay}ms:`, error)
          await new Promise(resolve => setTimeout(resolve, delay))
        } else {
          break
        }
      }
    }

    // All retries failed
    const errorMessage = lastError?.message || `Failed to ${operation} after ${retryAttempts} retries`
    setError(operation, errorMessage)
    setLoadingState(operation as keyof LoadingState, false)
    
    throw new Error(errorMessage)
  }, [
    getCachedData, 
    setCachedData, 
    setLoadingState, 
    clearError, 
    setError, 
    shouldRetry, 
    updateRetryState, 
    resetRetryState, 
    createAbortController, 
    cleanupAbortController,
    retryAttempts,
    isOnline,
    enableOfflineMode
  ])

  // Enhanced API methods
  const loadSupportedOptions = useCallback(async () => {
    return enhancedApiCall(
      'supportedOptions',
      async (signal) => {
        const options = await contentPlanningAPI.getSupportedOptions()
        setSupportedOptions(options)
        return options
      }
    )
  }, [enhancedApiCall])

  const loadDashboardData = useCallback(async (industryParam?: string) => {
    const industry = industryParam || selectedIndustry
    const cacheKey = `dashboardData_${industry}`
    
    return enhancedApiCall(
      cacheKey,
      async (signal) => {
        const data = await contentPlanningAPI.getDashboardData(industry)
        setDashboardData(data)
        return data
      }
    )
  }, [enhancedApiCall, selectedIndustry])

  // Debounced dashboard data loading
  const debouncedLoadDashboardData = useCallback((industry: string) => {
    const timeoutKey = `dashboardData_${industry}`
    
    // Clear existing timeout
    const existingTimeout = timeoutsRef.current.get(timeoutKey)
    if (existingTimeout) {
      clearTimeout(existingTimeout)
    }

    // Set new timeout
    const timeout = setTimeout(() => {
      loadDashboardData(industry)
      timeoutsRef.current.delete(timeoutKey)
    }, debounceMs)
    
    timeoutsRef.current.set(timeoutKey, timeout)
  }, [loadDashboardData, debounceMs])

  const generateContent = useCallback(async (request: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
    return enhancedApiCall(
      'contentGeneration',
      async (signal) => {
        return await contentPlanningAPI.generateContent(request)
      },
      false // Don't cache content generation
    )
  }, [enhancedApiCall])

  const saveContentSuggestion = useCallback(async (suggestionData: any) => {
    return enhancedApiCall(
      'saveContentSuggestion',
      async (signal) => {
        return await contentPlanningAPI.saveContentSuggestion(suggestionData)
      },
      false
    )
  }, [enhancedApiCall])

  const getContentSuggestions = useCallback(async (userId: string, limit: number = 3) => {
    const cacheKey = `contentSuggestions_${userId}_${limit}`
    
    return enhancedApiCall(
      cacheKey,
      async (signal) => {
        return await contentPlanningAPI.getContentSuggestions(userId, limit)
      }
    )
  }, [enhancedApiCall])

  const updateContentSuggestion = useCallback(async (suggestionId: string, request: any) => {
    return enhancedApiCall(
      'updateContentSuggestion',
      async (signal) => {
        return await contentPlanningAPI.updateContentSuggestion(suggestionId, request)
      },
      false
    )
  }, [enhancedApiCall])

  const analyzeCompetitors = useCallback(async (analysisType: string = 'trend_analysis') => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    return enhancedApiCall(
      'competitorAnalysis',
      async (signal) => {
        return await contentPlanningAPI.analyzeCompetitors({
          clerk_id: user.id,
          analysis_type: analysisType
        })
      },
      false
    )
  }, [enhancedApiCall, user?.id])

  const researchHashtags = useCallback(async (platform: string, contentType: string = 'promotional') => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    const cacheKey = `hashtags_${platform}_${contentType}`
    
    return enhancedApiCall(
      cacheKey,
      async (signal) => {
        return await contentPlanningAPI.researchHashtags({
          clerk_id: user.id,
          content_type: contentType,
          platform,
          target_audience: 'professionals'
        })
      }
    )
  }, [enhancedApiCall, user?.id])

  const generateStrategy = useCallback(async (platforms: string[], goals: string[] = ['engagement', 'reach']) => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    return enhancedApiCall(
      'strategyGeneration',
      async (signal) => {
        return await contentPlanningAPI.generateStrategy({
          clerk_id: user.id,
          platforms,
          content_goals: goals,
          target_audience: 'professionals'
        })
      },
      false
    )
  }, [enhancedApiCall, user?.id])

  const generateCalendar = useCallback(async (
    platforms: string[], 
    durationDays: number = 30, 
    postsPerDay: number = 2
  ) => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    return enhancedApiCall(
      'calendarGeneration',
      async (signal) => {
        return await contentPlanningAPI.generateCalendar({
          clerk_id: user.id,
          platforms,
          duration_days: durationDays,
          posts_per_day: postsPerDay
        })
      },
      false
    )
  }, [enhancedApiCall, user?.id])

  const identifyContentGaps = useCallback(async (userContentSummary: string = 'Standard promotional and educational content') => {
    const cacheKey = `contentGaps_${selectedIndustry}_${userContentSummary.slice(0, 50)}`
    
    return enhancedApiCall(
      cacheKey,
      async (signal) => {
        return await contentPlanningAPI.identifyGaps(selectedIndustry, userContentSummary)
      }
    )
  }, [enhancedApiCall, selectedIndustry])

  // Enhanced industry change with debouncing
  const changeIndustry = useCallback(async (newIndustry: string) => {
    setSelectedIndustry(newIndustry)
    debouncedLoadDashboardData(newIndustry)
  }, [debouncedLoadDashboardData])

  // Refresh data with cache invalidation
  const refreshData = useCallback(async (invalidateCache = false) => {
    if (invalidateCache) {
      cacheRef.current.clear()
    }
    
    await Promise.all([
      loadDashboardData(),
      loadSupportedOptions()
    ])
  }, [loadDashboardData, loadSupportedOptions])

  // Cancel all ongoing operations
  const cancelAllOperations = useCallback(() => {
    abortControllersRef.current.forEach(controller => {
      controller.abort()
    })
    abortControllersRef.current.clear()
    
    timeoutsRef.current.forEach(timeout => {
      clearTimeout(timeout)
    })
    timeoutsRef.current.clear()
  }, [])

  // Auto-load on mount
  useEffect(() => {
    if (autoLoad) {
      refreshData()
    }
  }, [autoLoad, refreshData])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancelAllOperations()
    }
  }, [cancelAllOperations])

  // Computed state
  const isLoading = Object.values(loadingStates).some(Boolean)
  const hasErrors = Object.keys(errors).length > 0
  const isReady = !isLoading && !hasErrors && !!dashboardData && !!supportedOptions

  return {
    // State
    dashboardData,
    supportedOptions,
    selectedIndustry,
    errors,
    loadingStates,
    isOnline,

    // Actions
    loadDashboardData,
    loadSupportedOptions,
    generateContent,
    saveContentSuggestion,
    getContentSuggestions,
    updateContentSuggestion,
    analyzeCompetitors,
    researchHashtags,
    generateStrategy,
    generateCalendar,
    identifyContentGaps,
    changeIndustry,
    refreshData,
    cancelAllOperations,

    // Error handling
    clearError,
    clearAllErrors,

    // Computed state
    isLoading,
    hasErrors,
    isReady,

    // Cache utilities
    getCachedData,
    setCachedData,

    // Network status
    isConnected: isOnline
  }
}

export default useEnhancedContentPlanning