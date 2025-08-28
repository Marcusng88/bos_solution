import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Types
interface YouTubeTokens {
  access_token: string
  refresh_token: string
  expires_at: number
}

interface VideoUploadData {
  videoFile: File
  title: string
  description: string
  tags?: string[]
  privacy_status?: string
}

interface VideoFileUploadData {
  videoFile: File
  title: string
  description: string
  tags?: string[]
  privacy_status?: string
}

interface YouTubeState {
  isConnected: boolean
  connectionStatus: 'idle' | 'connecting' | 'connected' | 'error'
  tokens: YouTubeTokens | null
  error: string | null
  
  // Actions
  connect: () => Promise<void>
  disconnect: () => void
  refreshToken: () => Promise<void>
  handleCallback: (code: string) => Promise<void>
  uploadVideoFile: (videoData: VideoFileUploadData, userId: string) => Promise<any>
  getUserVideos: (maxResults?: number) => Promise<any>
  getRecentActivity: (hoursBack?: number) => Promise<any>
  getVideoComments: (videoId: string, maxResults?: number, hoursBack?: number) => Promise<any>
  getROIAnalytics: (daysBack?: number, includeRevenue?: boolean) => Promise<any>
}

const STORAGE_KEY = 'youtube_tokens'

export const useYouTubeStore = create<YouTubeState>()(
  persist(
    (set, get) => ({
      isConnected: false,
      connectionStatus: 'idle',
      tokens: null,
      error: null,

      connect: async () => {
        set({ connectionStatus: 'connecting', error: null })
        
        try {
          console.log('Starting YouTube OAuth connection...')
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/auth/url`)
          const data = await response.json()
          
          console.log('Received auth URL:', data.auth_url ? 'URL received' : 'No URL')
          
          if (data.auth_url) {
            console.log('Redirecting to YouTube OAuth page...')
            // Redirect to YouTube OAuth page instead of opening popup
            window.location.href = data.auth_url
          } else {
            throw new Error('Failed to get auth URL')
          }
        } catch (error) {
          console.error('YouTube connect error:', error)
          set({
            connectionStatus: 'error',
            error: error instanceof Error ? error.message : 'Connection failed'
          })
        }
      },

      disconnect: () => {
        set({
          isConnected: false,
          connectionStatus: 'idle',
          tokens: null,
          error: null
        })
      },

      refreshToken: async () => {
        const { tokens } = get()
        if (!tokens?.refresh_token) {
          throw new Error('No refresh token available')
        }

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

          if (!response.ok) {
            throw new Error('Failed to refresh token')
          }

          const data = await response.json()
          const expires_at = Date.now() + (data.expires_in * 1000)
          
          set({
            tokens: {
              access_token: data.access_token,
              refresh_token: data.refresh_token || tokens.refresh_token,
              expires_at
            }
          })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Token refresh failed' })
          throw error
        }
      },

      handleCallback: async (code: string) => {
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
              expires_at
            },
            error: null
          })
        } catch (error) {
          set({
            connectionStatus: 'error',
            error: error instanceof Error ? error.message : 'Authentication failed'
          })
        }
      },

      uploadVideoFile: async (videoData: VideoFileUploadData, userId: string) => {
        const { tokens } = get()
        if (!tokens) {
          throw new Error('Not authenticated with YouTube')
        }

        // Check if token needs refresh
        if (Date.now() >= tokens.expires_at) {
          await get().refreshToken()
        }

        try {
          // Create FormData for file upload
          const formData = new FormData()
          formData.append('video_file', videoData.videoFile)
          formData.append('access_token', get().tokens?.access_token || '')
          formData.append('title', videoData.title)
          formData.append('description', videoData.description)
          formData.append('privacy_status', videoData.privacy_status || 'private')
          
          if (videoData.tags && videoData.tags.length > 0) {
            formData.append('tags', JSON.stringify(videoData.tags))
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
            throw new Error(`Failed to upload video: ${errorData}`)
          }

          return await response.json()
        } catch (error) {
          console.error('Video file upload error:', error)
          throw error
        }
      },

      getUserVideos: async (maxResults = 10) => {
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
            `${process.env.NEXT_PUBLIC_API_URL}/youtube/videos?access_token=${get().tokens?.access_token}&max_results=${maxResults}`
          )

          if (!response.ok) {
            throw new Error('Failed to fetch videos')
          }

          return await response.json()
        } catch (error) {
          console.error('Fetch videos error:', error)
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
          throw new Error('Not authenticated with YouTube')
        }

        // Check if token needs refresh
        if (Date.now() >= tokens.expires_at) {
          await get().refreshToken()
        }

        try {
          let url = `${process.env.NEXT_PUBLIC_API_URL}/youtube/videos/${videoId}/comments?access_token=${get().tokens?.access_token}&max_results=${maxResults}`
          
          if (hoursBack) {
            url += `&hours_back=${hoursBack}`
          }

          const response = await fetch(url)

          if (!response.ok) {
            throw new Error('Failed to fetch video comments')
          }

          return await response.json()
        } catch (error) {
          console.error('Fetch video comments error:', error)
          throw error
        }
      },

      getROIAnalytics: async (daysBack = 30, includeRevenue = true) => {
        const { tokens } = get()
        if (!tokens) {
          throw new Error('Not authenticated with YouTube')
        }

        // Check if token needs refresh
        if (Date.now() >= tokens.expires_at) {
          await get().refreshToken()
        }

        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
          let url = `${apiUrl}/youtube/analytics/roi-dashboard?access_token=${get().tokens?.access_token}&days_back=${daysBack}&include_estimated_revenue=${includeRevenue}`

          console.log('🔍 YouTube ROI Analytics Request:', {
            url: url.replace(get().tokens?.access_token || '', '[ACCESS_TOKEN]'),
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
          
          // Provide more specific error messages
          if (error instanceof Error) {
            if (error.name === 'AbortError') {
              throw new Error('Request timed out. Please check your internet connection and try again.')
            } else if (error.message.includes('Failed to fetch')) {
              throw new Error('Unable to connect to the server. Please check if the backend is running and try again.')
            }
          }
          
          throw error
        }
      },
    }),
    {
      name: STORAGE_KEY,
      partialize: (state: YouTubeState) => ({ tokens: state.tokens, isConnected: state.isConnected })
    }
  )
)
