import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { devtools } from 'zustand/middleware'

// Enhanced Types with better validation
interface YouTubeTokens {
  access_token: string
  refresh_token: string
  expires_at: number
  token_type?: string
  scope?: string
}

interface YouTubeChannel {
  id: string
  title: string
  description?: string
  thumbnails?: {
    default?: { url: string }
    medium?: { url: string }
    high?: { url: string }
  }
  customUrl?: string
  publishedAt?: string
  subscriberCount?: number
  videoCount?: number
  viewCount?: number
}

interface VideoUploadData {
  videoFile: File
  title: string
  description: string
  tags?: string[]
  privacy_status?: 'private' | 'public' | 'unlisted'
  categoryId?: string
  defaultLanguage?: string
  thumbnail?: File
}

interface VideoFileUploadData extends VideoUploadData {
  // Inherits all properties from VideoUploadData
}

interface YouTubeVideo {
  id: string
  title: string
  description?: string
  publishedAt: string
  thumbnails?: {
    default?: { url: string }
    medium?: { url: string }
    high?: { url: string }
  }
  statistics?: {
    viewCount?: string
    likeCount?: string
    commentCount?: string
  }
  status?: {
    privacyStatus: string
    uploadStatus: string
  }
}

interface YouTubeError {
  code: string
  message: string
  details?: any
}

type ConnectionStatus = 'idle' | 'connecting' | 'connected' | 'error' | 'disconnected'

interface YouTubeState {
  // State
  isConnected: boolean
  connectionStatus: ConnectionStatus
  tokens: YouTubeTokens | null
  error: YouTubeError | null
  channel: YouTubeChannel | null
  isLoading: boolean
  lastError: string | null
  
  // Actions
  connect: () => Promise<void>
  disconnect: () => void
  refreshToken: () => Promise<void>
  handleCallback: (code: string) => Promise<void>
  uploadVideoFile: (videoData: VideoFileUploadData, userId: string) => Promise<any>
  getUserVideos: (maxResults?: number) => Promise<YouTubeVideo[]>
  getRecentActivity: (hoursBack?: number) => Promise<any>
  getVideoComments: (videoId: string, maxResults?: number, hoursBack?: number) => Promise<any>
  getROIAnalytics: (daysBack?: number, includeRevenue?: boolean) => Promise<any>
  getChannelInfo: () => Promise<void>
  clearError: () => void
  setLoading: (loading: boolean) => void
}

const STORAGE_KEY = 'youtube_tokens'

// Helper function to create consistent error objects
const createError = (message: string, code: string = 'UNKNOWN_ERROR', details?: any): YouTubeError => ({
  code,
  message,
  details
})

// Helper function to safely refresh token with better error handling
const safeRefreshToken = async (get: () => YouTubeState): Promise<void> => {
  const { tokens } = get()
  if (!tokens || Date.now() < tokens.expires_at) {
    return // No refresh needed
  }

  try {
    await get().refreshToken()
  } catch (refreshError) {
    console.error('Token refresh failed:', refreshError)
    
    // If refresh failed due to expired/invalid tokens, provide clear guidance
    if (refreshError instanceof Error && 
        (refreshError.message.includes('expired') || 
         refreshError.message.includes('invalid') ||
         refreshError.message.includes('reconnect'))) {
      throw new Error('Your YouTube session has expired. Please reconnect your YouTube account.')
    }
    
    // For other refresh errors, provide general guidance
    throw new Error('Failed to refresh YouTube authentication. Please try reconnecting your account.')
  }
}

export const useYouTubeStore = create<YouTubeState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        isConnected: false,
        connectionStatus: 'idle',
        tokens: null,
        error: null,
        channel: null,
        isLoading: false,
        lastError: null,

        // Helper actions
        clearError: () => set({ error: null, lastError: null }),
        setLoading: (loading: boolean) => set({ isLoading: loading }),

        connect: async () => {
          set({ connectionStatus: 'connecting', error: null, isLoading: true })
          
          try {
            console.log('Starting YouTube OAuth connection...')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/auth/url`)
            
            if (!response.ok) {
              throw new Error(`HTTP ${response.status}: ${response.statusText}`)
            }
            
            const data = await response.json()
            
            console.log('Received auth URL:', data.auth_url ? 'URL received' : 'No URL')
            
            if (data.auth_url) {
              console.log('Redirecting to YouTube OAuth page...')
              // Redirect to YouTube OAuth page instead of opening popup
              window.location.href = data.auth_url
            } else {
              throw new Error('Failed to get auth URL from server')
            }
          } catch (error) {
            console.error('YouTube connect error:', error)
            const errorObj = createError(
              error instanceof Error ? error.message : 'Connection failed',
              'CONNECTION_ERROR',
              error
            )
            set({
              connectionStatus: 'error',
              error: errorObj,
              lastError: errorObj.message,
              isLoading: false
            })
          }
        },

        disconnect: () => {
          set({
            isConnected: false,
            connectionStatus: 'disconnected',
            tokens: null,
            error: null,
            channel: null,
            isLoading: false,
            lastError: null
          })
        },

        refreshToken: async () => {
          const { tokens } = get()
          if (!tokens?.refresh_token) {
            const errorObj = createError('No refresh token available', 'NO_REFRESH_TOKEN')
            set({ error: errorObj, lastError: errorObj.message })
            throw new Error(errorObj.message)
          }

          set({ isLoading: true })

          try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/refresh-token`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                refresh_token: tokens.refresh_token
              })
            })

            // Handle different types of errors
            if (!response.ok) {
              let errorMessage = `HTTP ${response.status}: Failed to refresh token`
              let errorCode = 'TOKEN_REFRESH_ERROR'
              
              try {
                const errorData = await response.json()
                if (errorData.detail || errorData.message) {
                  errorMessage = errorData.detail || errorData.message
                }
                
                // Check if this is an auth error that requires re-authentication
                if (response.status === 401 || response.status === 403 || 
                    errorMessage.toLowerCase().includes('invalid') || 
                    errorMessage.toLowerCase().includes('expired')) {
                  errorCode = 'REFRESH_TOKEN_EXPIRED'
                  errorMessage = 'Your YouTube session has expired. Please reconnect your account.'
                  
                  // Clear the invalid tokens
                  set({
                    isConnected: false,
                    connectionStatus: 'idle',
                    tokens: null,
                    error: null,
                    channel: null,
                    isLoading: false
                  })
                }
              } catch (parseError) {
                console.error('Failed to parse error response:', parseError)
              }
              
              const errorObj = createError(errorMessage, errorCode, { status: response.status })
              set({ 
                error: errorObj, 
                lastError: errorObj.message,
                isLoading: false 
              })
              throw new Error(errorMessage)
            }

            const data = await response.json()
            
            // Validate the response data
            if (!data.access_token) {
              throw new Error('Invalid response: missing access token')
            }
            
            const expires_at = Date.now() + ((data.expires_in || 3600) * 1000)
            
            set({
              tokens: {
                access_token: data.access_token,
                refresh_token: data.refresh_token || tokens.refresh_token,
                expires_at,
                token_type: data.token_type,
                scope: data.scope
              },
              isLoading: false,
              error: null,
              lastError: null,
              connectionStatus: 'connected'
            })
          } catch (error) {
            console.error('Token refresh error:', error)
            
            const errorObj = createError(
              error instanceof Error ? error.message : 'Token refresh failed',
              'TOKEN_REFRESH_ERROR',
              error
            )
            set({ 
              error: errorObj, 
              lastError: errorObj.message,
              isLoading: false 
            })
            throw error
          }
        },      handleCallback: async (code: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/auth/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
          })

          if (!response.ok) {
            const errorData = await response.text()
            throw new Error(`Failed to exchange code for tokens: ${errorData}`)
          }

          const data = await response.json()
          const expires_at = Date.now() + (data.expires_in * 1000)
          
          set({
            isConnected: true,
            connectionStatus: 'connected',
            tokens: {
              access_token: data.access_token,
              refresh_token: data.refresh_token,
              expires_at,
              token_type: data.token_type,
              scope: data.scope
            },
            error: null,
            lastError: null,
            isLoading: false
          })

          // Fetch channel info after successful authentication
          await get().getChannelInfo()
        } catch (error) {
          const errorObj = createError(
            error instanceof Error ? error.message : 'Authentication failed',
            'AUTH_CALLBACK_ERROR',
            error
          )
          set({
            connectionStatus: 'error',
            error: errorObj,
            lastError: errorObj.message,
            isLoading: false
          })
        }
      },

      getChannelInfo: async () => {
        const { tokens } = get()
        if (!tokens) {
          const errorObj = createError('Not authenticated with YouTube', 'NOT_AUTHENTICATED')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Safely refresh token if needed
        await safeRefreshToken(get)

        set({ isLoading: true })

        try {
          // Get current tokens after potential refresh
          const currentTokens = get().tokens
          if (!currentTokens?.access_token) {
            throw new Error('No valid access token available')
          }

          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/youtube/channel?access_token=${currentTokens.access_token}`
          )

          if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
              throw new Error('YouTube authentication failed. Please reconnect your account.')
            }
            throw new Error(`HTTP ${response.status}: Failed to fetch channel info`)
          }

          const channelData = await response.json()
          
          // Validate and transform channel data
          const channel: YouTubeChannel = {
            id: channelData.id,
            title: channelData.snippet?.title || 'Unknown Channel',
            description: channelData.snippet?.description,
            thumbnails: channelData.snippet?.thumbnails,
            customUrl: channelData.snippet?.customUrl,
            publishedAt: channelData.snippet?.publishedAt,
            subscriberCount: parseInt(channelData.statistics?.subscriberCount || '0'),
            videoCount: parseInt(channelData.statistics?.videoCount || '0'),
            viewCount: parseInt(channelData.statistics?.viewCount || '0')
          }
          
          set({ 
            channel, 
            isLoading: false, 
            error: null, 
            lastError: null 
          })
        } catch (error) {
          console.error('Fetch channel info error:', error)
          const errorObj = createError(
            error instanceof Error ? error.message : 'Failed to fetch channel info',
            'CHANNEL_FETCH_ERROR',
            error
          )
          set({ 
            error: errorObj, 
            lastError: errorObj.message, 
            isLoading: false 
          })
          throw error
        }
      },

      uploadVideoFile: async (videoData: VideoFileUploadData, userId: string) => {
        const { tokens } = get()
        if (!tokens) {
          const errorObj = createError('Not authenticated with YouTube', 'NOT_AUTHENTICATED')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Validate video data
        if (!videoData.videoFile || !videoData.title.trim()) {
          const errorObj = createError('Video file and title are required', 'INVALID_INPUT')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Check if token needs refresh and handle refresh failures
        if (Date.now() >= tokens.expires_at) {
          try {
            await get().refreshToken()
          } catch (refreshError) {
            console.error('Failed to refresh token before upload:', refreshError)
            
            // If refresh failed due to expired/invalid tokens, provide clear guidance
            if (refreshError instanceof Error && 
                (refreshError.message.includes('expired') || 
                 refreshError.message.includes('invalid') ||
                 refreshError.message.includes('reconnect'))) {
              throw new Error('Your YouTube session has expired. Please reconnect your YouTube account and try again.')
            }
            
            // For other refresh errors, provide general guidance
            throw new Error('Failed to refresh YouTube authentication. Please try reconnecting your account.')
          }
        }

        set({ isLoading: true })

        try {
          // Get the refreshed tokens
          const currentTokens = get().tokens
          if (!currentTokens?.access_token) {
            throw new Error('No valid access token available after refresh')
          }

          // Create FormData for file upload
          const formData = new FormData()
          formData.append('video_file', videoData.videoFile)
          formData.append('access_token', currentTokens.access_token)
          formData.append('title', videoData.title.trim())
          formData.append('description', videoData.description.trim() || '')
          formData.append('privacy_status', videoData.privacy_status || 'private')
          
          if (videoData.tags && videoData.tags.length > 0) {
            formData.append('tags', JSON.stringify(videoData.tags.filter(tag => tag.trim())))
          }
          
          if (videoData.categoryId) {
            formData.append('category_id', videoData.categoryId)
          }
          
          if (videoData.defaultLanguage) {
            formData.append('default_language', videoData.defaultLanguage)
          }
          
          if (videoData.thumbnail) {
            formData.append('thumbnail', videoData.thumbnail)
          }

          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/upload-file`, {
            method: 'POST',
            headers: {
              'X-User-ID': userId,
            },
            body: formData, // Don't set Content-Type header for FormData
          })

          if (!response.ok) {
            const errorData = await response.text()
            
            // Handle specific error cases
            if (response.status === 401 || response.status === 403) {
              throw new Error('YouTube authentication failed. Please reconnect your account.')
            } else if (response.status === 413) {
              throw new Error('Video file is too large. Please try a smaller file.')
            } else if (response.status === 400) {
              throw new Error(`Upload failed: ${errorData || 'Invalid request'}`)
            }
            
            throw new Error(`Failed to upload video: ${errorData || `HTTP ${response.status}`}`)
          }

          const result = await response.json()
          set({ isLoading: false, error: null, lastError: null })
          return result
        } catch (error) {
          console.error('Video file upload error:', error)
          const errorObj = createError(
            error instanceof Error ? error.message : 'Failed to upload video',
            'VIDEO_UPLOAD_ERROR',
            error
          )
          set({ 
            error: errorObj, 
            lastError: errorObj.message, 
            isLoading: false 
          })
          throw error
        }
      },

      getUserVideos: async (maxResults = 10): Promise<YouTubeVideo[]> => {
        const { tokens } = get()
        if (!tokens) {
          const errorObj = createError('Not authenticated with YouTube', 'NOT_AUTHENTICATED')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Check if token needs refresh
        if (Date.now() >= tokens.expires_at) {
          await get().refreshToken()
        }

        set({ isLoading: true })

        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/youtube/videos?access_token=${get().tokens?.access_token}&max_results=${maxResults}`
          )

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: Failed to fetch videos`)
          }

          const data = await response.json()
          
          // Transform and validate video data
          const videos: YouTubeVideo[] = (data.items || []).map((item: any) => ({
            id: item.id,
            title: item.snippet?.title || 'Untitled Video',
            description: item.snippet?.description,
            publishedAt: item.snippet?.publishedAt,
            thumbnails: item.snippet?.thumbnails,
            statistics: item.statistics,
            status: item.status
          }))

          set({ isLoading: false, error: null, lastError: null })
          return videos
        } catch (error) {
          console.error('Fetch videos error:', error)
          const errorObj = createError(
            error instanceof Error ? error.message : 'Failed to fetch videos',
            'VIDEOS_FETCH_ERROR',
            error
          )
          set({ 
            error: errorObj, 
            lastError: errorObj.message, 
            isLoading: false 
          })
          throw error
        }
      },

      getRecentActivity: async (hoursBack = 1) => {
        const { tokens } = get()
        if (!tokens) {
          throw new Error('Not authenticated with YouTube')
        }

        // Check if token needs refresh
        if (Date.now() >= tokens.expires_at) {
          await get().refreshToken()
        }

        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/youtube/recent-activity?access_token=${get().tokens?.access_token}&hours_back=${hoursBack}`
          )

          if (!response.ok) {
            throw new Error('Failed to fetch recent activity')
          }

          return await response.json()
        } catch (error) {
          console.error('Fetch recent activity error:', error)
          throw error
        }
      },

      getVideoComments: async (videoId: string, maxResults = 20, hoursBack?: number) => {
        const { tokens } = get()
        if (!tokens) {
          const errorObj = createError('Not authenticated with YouTube', 'NOT_AUTHENTICATED')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Safely refresh token if needed
        await safeRefreshToken(get)

        try {
          // Get current tokens after potential refresh
          const currentTokens = get().tokens
          if (!currentTokens?.access_token) {
            throw new Error('No valid access token available')
          }

          let url = `${process.env.NEXT_PUBLIC_API_URL}/youtube/videos/${videoId}/comments?access_token=${currentTokens.access_token}&max_results=${maxResults}`
          
          if (hoursBack) {
            url += `&hours_back=${hoursBack}`
          }

          const response = await fetch(url)

          if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
              throw new Error('YouTube authentication failed. Please reconnect your account.')
            }
            throw new Error(`HTTP ${response.status}: Failed to fetch video comments`)
          }

          return await response.json()
        } catch (error) {
          console.error('Fetch video comments error:', error)
          const errorObj = createError(
            error instanceof Error ? error.message : 'Failed to fetch video comments',
            'COMMENTS_FETCH_ERROR',
            error
          )
          set({ 
            error: errorObj, 
            lastError: errorObj.message 
          })
          throw error
        }
      },

      getROIAnalytics: async (daysBack = 30, includeRevenue = true) => {
        const { tokens } = get()
        if (!tokens) {
          const errorObj = createError('Not authenticated with YouTube', 'NOT_AUTHENTICATED')
          set({ error: errorObj, lastError: errorObj.message })
          throw new Error(errorObj.message)
        }

        // Safely refresh token if needed
        await safeRefreshToken(get)

        try {
          // Get current tokens after potential refresh
          const currentTokens = get().tokens
          if (!currentTokens?.access_token) {
            throw new Error('No valid access token available')
          }

          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://bos-solution.onrender.com/api/v1'
          let url = `${apiUrl}/youtube/analytics/roi-dashboard?access_token=${currentTokens.access_token}&days_back=${daysBack}&include_estimated_revenue=${includeRevenue}`

          console.log('🔍 YouTube ROI Analytics Request:', {
            url: url.replace(currentTokens.access_token || '', '[ACCESS_TOKEN]'),
            daysBack,
            includeRevenue,
            apiUrl
          })

          const response = await fetch(url, {
            signal: AbortSignal.timeout(30000) // 30 second timeout
          })

          console.log('🔍 YouTube ROI Analytics Response:', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok
          })

          if (!response.ok) {
            // Check for authentication errors first
            if (response.status === 401 || response.status === 403) {
              throw new Error('YouTube authentication failed. Please reconnect your account.')
            }
            
            // Try to get error details from response
            let errorMessage = `Failed to fetch ROI analytics: ${response.status} ${response.statusText}`
            
            try {
              // First try to parse as JSON
              const errorData = await response.json()
              console.log('🔍 Error response JSON:', errorData)
              if (errorData?.detail) {
                errorMessage = errorData.detail
              } else if (errorData?.message) {
                errorMessage = errorData.message
              }
            } catch (parseError) {
              console.log('🔍 JSON parse failed, trying text:', parseError)
              // If JSON parsing fails, try to get text
              try {
                const errorText = await response.text()
                console.log('🔍 Error response text:', errorText)
                if (errorText && errorText.trim()) {
                  // Check if it's an HTML error page
                  if (errorText.includes('<html') || errorText.includes('<!DOCTYPE')) {
                    errorMessage = `Server error: ${response.status} ${response.statusText}. Please try again later.`
                  } else {
                    errorMessage = `Server error: ${errorText}`
                  }
                }
              } catch (textError) {
                console.log('🔍 Text parse failed:', textError)
                // If all else fails, use the status
                errorMessage = `Server error: ${response.status} ${response.statusText}. Please try again later.`
              }
            }
            
            throw new Error(errorMessage)
          }

          const result = await response.json()
          console.log('🔍 YouTube ROI Analytics Success:', result)
          return result
        } catch (error) {
          console.error('🔍 Fetch ROI analytics error:', error)
          
          const errorObj = createError(
            error instanceof Error ? error.message : 'Failed to fetch ROI analytics',
            'ROI_FETCH_ERROR',
            error
          )
          
          // Provide more specific error messages
          if (error instanceof Error) {
            if (error.name === 'AbortError') {
              errorObj.message = 'Request timed out. Please check your internet connection and try again.'
            } else if (error.message.includes('Failed to fetch')) {
              errorObj.message = 'Unable to connect to the server. Please check if the backend is running and try again.'
            }
          }
          
          set({ 
            error: errorObj, 
            lastError: errorObj.message 
          })
          throw error
        }
      },
      }),
      {
        name: STORAGE_KEY,
        partialize: (state: YouTubeState) => ({ 
          tokens: state.tokens, 
          isConnected: state.isConnected,
          channel: state.channel 
        })
      }
    ),
    {
      name: 'youtube-store'
    }
  )
)
