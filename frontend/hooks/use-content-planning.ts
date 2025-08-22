/**
 * React hook for content planning functionality
 * Manages state and API interactions for content planning features
 * 
 * Note: autoLoad only loads basic dashboard data and supported options.
 * AI agent functions (generateContent, analyzeCompetitors, etc.) are only
 * invoked when explicitly called by the user.
 */

import { useState, useEffect, useCallback } from 'react'
import { 
  contentPlanningAPI, 
  type DashboardData, 
  type SupportedOptions,
  type ContentGenerationRequest,
  type ContentGenerationResponse 
} from '@/lib/content-planning-api'

export interface UseContentPlanningOptions {
  industry?: string
  autoLoad?: boolean // Only loads basic dashboard data, doesn't invoke AI agent
}

export function useContentPlanning(options: UseContentPlanningOptions = {}) {
  const { industry = 'technology', autoLoad = true } = options

  // State management
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [supportedOptions, setSupportedOptions] = useState<SupportedOptions | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState(industry)

  // Load supported options
  const loadSupportedOptions = useCallback(async () => {
    try {
      setLoading(true)
      const options = await contentPlanningAPI.getSupportedOptions()
      setSupportedOptions(options)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load supported options')
    } finally {
      setLoading(false)
    }
  }, [])

  // Load dashboard data
  const loadDashboardData = useCallback(async (industryParam?: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await contentPlanningAPI.getDashboardData(industryParam || selectedIndustry)
      setDashboardData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Generate content - Only invoked when user clicks "Create Content" button
  const generateContent = useCallback(async (request: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateContent(request)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate content'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // Save content suggestion to database
  const saveContentSuggestion = useCallback(async (suggestionData: {
    user_id: string
    suggested_content: string
    platform: string
    industry: string
    content_type: string
    tone: string
    target_audience: string
    hashtags?: string[]
    custom_requirements?: string
  }) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.saveContentSuggestion(suggestionData)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save content suggestion'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // Get content suggestions from database
  const getContentSuggestions = useCallback(async (userId: string, limit: number = 3) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.getContentSuggestions(userId, limit)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch content suggestions'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // Analyze competitors - Only invoked when explicitly requested by user
  const analyzeCompetitors = useCallback(async (analysisType: string = 'trend_analysis') => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.analyzeCompetitors({
        industry: selectedIndustry,
        analysis_type: analysisType
      })
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze competitors'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Research hashtags - Only invoked when explicitly requested by user
  const researchHashtags = useCallback(async (platform: string, contentType: string = 'promotional') => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.researchHashtags({
        industry: selectedIndustry,
        content_type: contentType,
        platform,
        target_audience: 'professionals'
      })
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to research hashtags'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Generate content strategy - Only invoked when explicitly requested by user
  const generateStrategy = useCallback(async (platforms: string[], goals: string[] = ['engagement', 'reach']) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateStrategy({
        industry: selectedIndustry,
        platforms,
        content_goals: goals,
        target_audience: 'professionals'
      })
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate strategy'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Generate content calendar - Only invoked when explicitly requested by user
  const generateCalendar = useCallback(async (
    platforms: string[], 
    durationDays: number = 30, 
    postsPerDay: number = 2
  ) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateCalendar({
        industry: selectedIndustry,
        platforms,
        duration_days: durationDays,
        posts_per_day: postsPerDay
      })
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate calendar'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Identify content gaps - Only invoked when explicitly requested by user
  const identifyContentGaps = useCallback(async (userContentSummary: string = 'Standard promotional and educational content') => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.identifyGaps(selectedIndustry, userContentSummary)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to identify content gaps'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [selectedIndustry])

  // Change industry and reload data
  const changeIndustry = useCallback(async (newIndustry: string) => {
    setSelectedIndustry(newIndustry)
    await loadDashboardData(newIndustry)
  }, [loadDashboardData])

  // Refresh all data
  const refreshData = useCallback(async () => {
    await Promise.all([
      loadDashboardData(),
      loadSupportedOptions()
    ])
  }, [loadDashboardData, loadSupportedOptions])

  // Auto-load basic dashboard data on mount (does NOT invoke AI agent)
  useEffect(() => {
    if (autoLoad) {
      refreshData()
    }
  }, [autoLoad, refreshData])

  return {
    // State
    dashboardData,
    supportedOptions,
    loading,
    error,
    selectedIndustry,

    // Actions
    loadDashboardData,
    loadSupportedOptions,
    generateContent,
    saveContentSuggestion,
    getContentSuggestions,
    analyzeCompetitors,
    researchHashtags,
    generateStrategy,
    generateCalendar,
    identifyContentGaps,
    changeIndustry,
    refreshData,

    // Utilities
    isLoading: loading,
    hasError: !!error,
    isReady: !loading && !error && !!dashboardData && !!supportedOptions
  }
}
