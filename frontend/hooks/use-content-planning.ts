/**
 * React hook for content planning functionality
 * Manages state and API interactions for content planning features
 * 
 * Note: autoLoad only loads basic dashboard data and supported options.
 * AI agent functions (generateContent, analyzeCompetitors, etc.) are only
 * invoked when explicitly called by the user.
 */

import { useState, useEffect, useCallback } from 'react'
import { useUser } from '@clerk/nextjs'
import { 
  contentPlanningAPI, 
  type DashboardData, 
  type SupportedOptions,
  type ContentGenerationRequest,
  type ContentGenerationResponse,
  type ImageGenerationRequest,
  type ImageGenerationResponse
} from '@/lib/content-planning-api'

export interface UseContentPlanningOptions {
  autoLoad?: boolean // Only loads basic dashboard data, doesn't invoke AI agent
}

export function useContentPlanning(options: UseContentPlanningOptions = {}) {
  const { autoLoad = true } = options
  const { user } = useUser()

  // State management
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [supportedOptions, setSupportedOptions] = useState<SupportedOptions | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState('technology') // Keep for dashboard data

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

  // Update content suggestion in database
  const updateContentSuggestion = useCallback(async (suggestionId: string, request: { suggested_content: string; user_modifications?: string }) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.updateContentSuggestion(suggestionId, request)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update content suggestion'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

  // Analyze competitors - Only invoked when explicitly requested by user
  const analyzeCompetitors = useCallback(async (analysisType: string = 'trend_analysis') => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.analyzeCompetitors({
        clerk_id: user.id,
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
  }, [user?.id])

  // Research hashtags - Only invoked when explicitly requested by user
  const researchHashtags = useCallback(async (platform: string, contentType: string = 'promotional') => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.researchHashtags({
        clerk_id: user.id,
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
  }, [user?.id])

  // Generate content strategy - Only invoked when explicitly requested by user
  const generateStrategy = useCallback(async (platforms: string[], goals: string[] = ['engagement', 'reach']) => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateStrategy({
        clerk_id: user.id,
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
  }, [user?.id])

  // Generate content calendar - Only invoked when explicitly requested by user
  const generateCalendar = useCallback(async (
    platforms: string[], 
    durationDays: number = 30, 
    postsPerDay: number = 2
  ) => {
    if (!user?.id) {
      throw new Error('User not authenticated')
    }
    
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateCalendar({
        clerk_id: user.id,
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
  }, [user?.id])

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

  // Generate image based on text content - Only invoked when explicitly requested by user
  const generateImage = useCallback(async (request: {
    text_content: string
    platform?: string
    content_type?: string
    industry?: string
    custom_prompt?: string
  }) => {
    try {
      setLoading(true)
      setError(null)
      const response = await contentPlanningAPI.generateImage(request)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate image'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [])

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
    updateContentSuggestion,
    analyzeCompetitors,
    researchHashtags,
    generateStrategy,
    generateCalendar,
    identifyContentGaps,
    generateImage,
    changeIndustry,
    refreshData,

    // Utilities
    isLoading: loading,
    hasError: !!error,
    isReady: !loading && !error && !!dashboardData && !!supportedOptions
  }
}
