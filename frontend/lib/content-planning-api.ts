/**
 * Content Planning API Client
 * Provides interface to backend content planning services
 */

// Types
export interface DashboardData {
  success: boolean
  summary: {
    scheduled_posts: number
    gap_opportunities: number
    competitive_edge: string
    threat_alerts: number
  }
  competitive_intelligence: {
    new_opportunities: string[]
    trending_hashtags: string[]
  }
  content_gaps: Array<{
    type: string
    suggestion: string
    priority: string
    expected_impact: string
    implementation_effort: string
  }>
  recent_activity: Array<{
    action: string
    content: string
    time: string
    status: string
  }>
  performance_metrics: {
    content_performance: Record<string, any>
    hashtag_effectiveness: Record<string, any>
  }
  error?: string
}

export interface SupportedOptions {
  industries: string[]
  platforms: string[]
  content_types: string[]
  tones: string[]
}

export interface ContentGenerationRequest {
  clerk_id: string
  platform: string
  content_type: string
  tone?: string
  target_audience: string
  custom_requirements?: string
  generate_variations?: boolean
  industry?: string  // Add industry field
}

export interface ContentGenerationResponse {
  success: boolean
  content?: Record<string, any>
  variations?: Record<string, any>[]
  error?: string
}

export interface SaveContentSuggestionRequest {
  user_id: string
  suggested_content: string
  platform: string
  industry: string
  content_type: string
  tone: string
  target_audience: string
  hashtags?: string[]
  custom_requirements?: string
}

export interface SaveContentSuggestionResponse {
  success: boolean
  message: string
  suggestion_id?: string
  error?: string
}

export interface GetContentSuggestionsResponse {
  success: boolean
  suggestions: Array<{
    id: string
    suggested_content: string
    suggested_hashtags: string[]
    platform: string
    clerk_id: string
    content_type: string
    tone: string
    target_audience: string
    created_at: string
    predicted_engagement: Record<string, any>
    competitor_analysis: Record<string, any>
  }>
  error?: string
}

export interface CompetitorAnalysisRequest {
  clerk_id: string
  competitor_ids?: string[]
  analysis_type?: string
  time_period?: string
}

export interface CompetitorAnalysisResponse {
  success: boolean
  analysis?: Record<string, any>
  insights?: Record<string, any>
  recommendations?: string[]
  error?: string
}

export interface HashtagResearchRequest {
  clerk_id: string
  content_type: string
  platform: string
  target_audience: string
  custom_keywords?: string[]
}

export interface ContentStrategyRequest {
  clerk_id: string
  platforms: string[]
  content_goals: string[]
  target_audience: string
}

export interface ContentCalendarRequest {
  clerk_id: string
  platforms: string[]
  duration_days?: number
  posts_per_day?: number
}

// API Base URL - adjust based on your backend configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://bos-solution.onrender.com/api/v1'

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`API call to ${endpoint} failed:`, error)
    throw error
  }
}

// Content Planning API
export const contentPlanningAPI = {
  // Get dashboard data
  async getDashboardData(industry: string = 'technology'): Promise<DashboardData> {
    return apiCall<DashboardData>(`/content-planning/dashboard-data?industry=${encodeURIComponent(industry)}`)
  },

  // Get supported options
  async getSupportedOptions(): Promise<SupportedOptions> {
    return apiCall<SupportedOptions>('/content-planning/supported-options')
  },

  // Generate content
  async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    return apiCall<ContentGenerationResponse>('/content-planning/generate-content', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Analyze competitors
  async analyzeCompetitors(request: CompetitorAnalysisRequest): Promise<CompetitorAnalysisResponse> {
    return apiCall<CompetitorAnalysisResponse>('/content-planning/analyze-competitors', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Research hashtags
  async researchHashtags(request: HashtagResearchRequest): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>('/content-planning/research-hashtags', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Generate content strategy
  async generateStrategy(request: ContentStrategyRequest): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>('/content-planning/generate-strategy', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Generate content calendar
  async generateCalendar(request: ContentCalendarRequest): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>('/content-planning/generate-calendar', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Identify content gaps
  async identifyGaps(industry: string, userContentSummary: string): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>('/content-planning/identify-gaps', {
      method: 'POST',
      body: JSON.stringify({
        industry,
        user_content_summary: userContentSummary,
      }),
    })
  },

  // Get industry insights
  async getIndustryInsights(industry: string): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>(`/content-planning/industry-insights/${encodeURIComponent(industry)}`)
  },

  // Optimize posting schedule
  async optimizeSchedule(industry: string, platforms: string[]): Promise<Record<string, any>> {
    return apiCall<Record<string, any>>('/content-planning/optimize-schedule', {
      method: 'POST',
      body: JSON.stringify({
        industry,
        platforms,
      }),
    })
  },

  // Save content suggestion to database
  async saveContentSuggestion(request: SaveContentSuggestionRequest): Promise<SaveContentSuggestionResponse> {
    return apiCall<SaveContentSuggestionResponse>('/content-planning/save-content-suggestion', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  // Get content suggestions from database
  async getContentSuggestions(userId: string, limit: number = 3): Promise<GetContentSuggestionsResponse> {
    return apiCall<GetContentSuggestionsResponse>(`/content-planning/get-content-suggestions?user_id=${encodeURIComponent(userId)}&limit=${limit}`)
  },

  // Update content suggestion in database
  async updateContentSuggestion(suggestionId: string, request: { suggested_content: string; user_modifications?: string }): Promise<{ success: boolean; message: string; suggestion_id?: string; error?: string }> {
    return apiCall<{ success: boolean; message: string; suggestion_id?: string; error?: string }>(`/content-planning/update-content-suggestion/${suggestionId}`, {
      method: 'PUT',
      body: JSON.stringify(request),
    })
  },
}

// Mock data for development/testing when backend is not available
export const mockContentPlanningAPI = {
  async getDashboardData(industry: string = 'technology'): Promise<DashboardData> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    return {
      success: true,
      summary: {
        scheduled_posts: 24,
        gap_opportunities: 8,
        competitive_edge: '+23%',
        threat_alerts: 3,
      },
      competitive_intelligence: {
        new_opportunities: [
          'Video content creation',
          'Interactive polls and surveys',
          'Behind-the-scenes content',
        ],
        trending_hashtags: [
          '#TechInnovation',
          '#AI',
          '#DigitalTransformation',
          '#Innovation',
          '#TechTrends',
        ],
      },
      content_gaps: [
        {
          type: 'format_gap',
          suggestion: 'Educational video content',
          priority: 'High',
          expected_impact: 'High',
          implementation_effort: 'Medium'
        },
        {
          type: 'topic_gap',
          suggestion: 'Industry trend analysis',
          priority: 'High',
          expected_impact: 'Moderate to High',
          implementation_effort: 'Medium'
        },
        {
          type: 'topic_gap',
          suggestion: 'Customer success stories',
          priority: 'Medium',
          expected_impact: 'Moderate',
          implementation_effort: 'Low'
        },
        {
          type: 'format_gap',
          suggestion: 'Technical tutorials',
          priority: 'High',
          expected_impact: 'High',
          implementation_effort: 'Medium'
        },
        {
          type: 'topic_gap',
          suggestion: 'Thought leadership content',
          priority: 'Medium',
          expected_impact: 'High',
          implementation_effort: 'High'
        },
      ],
      recent_activity: [
        {
          action: 'Gap Identified',
          content: 'Video content opportunity vs competitors',
          time: '1 hour ago',
          status: 'opportunity',
        },
        {
          action: 'AI Generated',
          content: 'Weekly Newsletter Content',
          time: '2 hours ago',
          status: 'draft',
        },
        {
          action: 'Competitor Alert',
          content: 'New trending hashtag detected',
          time: '3 hours ago',
          status: 'alert',
        },
      ],
      performance_metrics: {
        content_performance: {
          engagement_rate: '4.2%',
          reach_growth: '+15%',
          click_through_rate: '2.8%',
        },
        hashtag_effectiveness: {
          top_performing: ['#TechInnovation', '#AI'],
          trending: ['#DigitalTransformation', '#Innovation'],
        },
      },
    }
  },

  async getSupportedOptions(): Promise<SupportedOptions> {
    await new Promise(resolve => setTimeout(resolve, 300))
    
    return {
      industries: [
        'technology',
        'fashion_beauty',
        'food_beverage',
        'finance_fintech',
        'healthcare_wellness',
        'automotive',
        'travel_hospitality',
        'fitness_sports',
        'education_elearning',
        'real_estate_construction',
      ],
      platforms: [
        'linkedin',
        'twitter',
        'instagram',
        'facebook',
        'tiktok',
        'youtube',
      ],
      content_types: [
        'product_announcement',
        'educational',
        'promotional',
        'behind_the_scenes',
        'user_generated',
        'trending_topic',
        'industry_news',
        'company_culture',
      ],
      tones: [
        'professional',
        'casual',
        'humorous',
        'inspirational',
        'urgent',
        'friendly',
        'authoritative',
        'playful',
        'educational',
        'promotional',
      ],
    }
  },

  async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return {
      success: true,
      content: {
        platform: request.platform,
        content_type: request.content_type,
        tone: request.tone || 'professional',
        content: `Generated ${request.content_type} content for ${request.platform}.`,
        hashtags: ['#Generated', '#Content', '#AI'],
        optimal_posting_time: 'Tuesday-Thursday, 9-11 AM',
      },
    }
  },

  async analyzeCompetitors(request: CompetitorAnalysisRequest): Promise<CompetitorAnalysisResponse> {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    return {
      success: true,
      analysis: {
        competitor_count: 5,
        analysis_type: request.analysis_type || 'comprehensive_analysis',
        time_period: request.time_period || 'last_30_days',
      },
      insights: {
        market_opportunities: ['Video content', 'Interactive content', 'Educational series'],
        content_gaps: [
          {
            type: 'topic_gap',
            suggestion: 'Technical tutorials',
            priority: 'High',
            expected_impact: 'High',
            implementation_effort: 'Medium'
          },
          {
            type: 'topic_gap',
            suggestion: 'Industry insights',
            priority: 'High',
            expected_impact: 'Moderate to High',
            implementation_effort: 'Low'
          },
          {
            type: 'topic_gap',
            suggestion: 'Customer stories',
            priority: 'Medium',
            expected_impact: 'Moderate',
            implementation_effort: 'Low'
          }
        ],
      },
      recommendations: [
        'Focus on video content creation',
        'Develop educational content series',
        'Increase interactive content frequency',
      ],
    }
  },

  async researchHashtags(request: HashtagResearchRequest): Promise<Record<string, any>> {
    await new Promise(resolve => setTimeout(resolve, 600))
    
    return {
      success: true,
      recommended_hashtags: {
        trending_hashtags: ['#Trending', '#Popular', '#Viral'],
        industry_specific: ['#Industry', '#Specific', '#Relevant'],
        platform_optimized: ['#Platform', '#Optimized', '#Best'],
      },
      hashtag_analysis: {
        engagement_potential: 'High',
        reach_estimate: '10K-50K',
        competition_level: 'Medium',
      },
    }
  },

  async generateStrategy(request: ContentStrategyRequest): Promise<Record<string, any>> {
    await new Promise(resolve => setTimeout(resolve, 1200))
    
    return {
      success: true,
      strategy: {
        overview: `Comprehensive content strategy for user`,
        platforms: request.platforms,
        goals: request.content_goals,
        target_audience: request.target_audience,
        content_mix: {
          educational: '40%',
          promotional: '30%',
          engaging: '20%',
          trending: '10%',
        },
      },
    }
  },

  async generateCalendar(request: ContentCalendarRequest): Promise<Record<string, any>> {
    await new Promise(resolve => setTimeout(resolve, 900))
    
    return {
      success: true,
      calendar: {
        duration_days: request.duration_days || 30,
        posts_per_day: request.posts_per_day || 2,
        total_posts: (request.duration_days || 30) * (request.posts_per_day || 2),
        platforms: request.platforms,
        content_distribution: {
          monday: ['Educational', 'Promotional'],
          tuesday: ['Trending', 'Engaging'],
          wednesday: ['Educational', 'Promotional'],
          thursday: ['Trending', 'Engaging'],
          friday: ['Educational', 'Promotional'],
          saturday: ['Engaging', 'Trending'],
          sunday: ['Educational', 'Engaging'],
        },
      },
    }
  },

  async identifyGaps(industry: string, userContentSummary: string): Promise<Record<string, any>> {
    await new Promise(resolve => setTimeout(resolve, 700))
    
    return {
      success: true,
      gaps_identified: {
        potential_topic_gaps: [
          'Industry trend analysis',
          'Technical tutorials',
          'Customer success stories',
          'Behind-the-scenes content',
          'Interactive content',
        ],
        content_format_gaps: ['Video content', 'Infographics', 'Podcasts'],
      },
      content_suggestions: [
        {
          type: 'topic_gap',
          suggestion: 'Create weekly industry trend reports',
          priority: 'High',
          expected_impact: 'Moderate to High',
          implementation_effort: 'Medium'
        },
        {
          type: 'topic_gap',
          suggestion: 'Develop technical tutorial series',
          priority: 'High',
          expected_impact: 'High',
          implementation_effort: 'Medium'
        },
        {
          type: 'topic_gap',
          suggestion: 'Share customer success stories',
          priority: 'Medium',
          expected_impact: 'Moderate',
          implementation_effort: 'Low'
        },
        {
          type: 'format_gap',
          suggestion: 'Show behind-the-scenes processes',
          priority: 'Medium',
          expected_impact: 'High',
          implementation_effort: 'Medium'
        },
        {
          type: 'format_gap',
          suggestion: 'Create interactive polls and surveys',
          priority: 'Low',
          expected_impact: 'Moderate',
          implementation_effort: 'Low'
        },
      ],
    }
  },
}

// Export the appropriate API based on environment
export default process.env.NODE_ENV === 'development' && !process.env.NEXT_PUBLIC_API_URL
  ? mockContentPlanningAPI
  : contentPlanningAPI
