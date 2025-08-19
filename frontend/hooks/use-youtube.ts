import { create } from 'zustand'

interface YouTubeTokens {
  access_token: string
  refresh_token: string
  expires_in: number
  expires_at: number
}

interface YouTubeChannel {
  id: string
  title: string
  description: string
  thumbnail: string
  subscriber_count: string
  video_count: string
  view_count: string
}

interface VideoUploadData {
  title: string
  description: string
  tags?: string[]
  privacy_status?: string
}

interface VideoFileUploadData extends VideoUploadData {
  videoFile: File
}

interface YouTubeState {
  isConnected: boolean
  connectionStatus: string
  tokens: YouTubeTokens | null
  channel: YouTubeChannel | null
  connect: () => Promise<void>
  disconnect: () => void
  handleCallback: (code: string) => Promise<any>
  refreshToken: () => Promise<YouTubeTokens>
  uploadVideo: (videoData: VideoUploadData) => Promise<any>
  uploadVideoFile: (videoData: VideoFileUploadData) => Promise<any>
  getUserVideos: (maxResults?: number) => Promise<any>
}

const STORAGE_KEY = 'youtube_tokens'

export const useYouTubeStore = create<YouTubeState>((set, get) => ({
  isConnected: false,
  connectionStatus: 'disconnected',
  tokens: null,
  channel: null,

  connect: async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/auth/url`)
      const data = await response.json()
      
      if (data.auth_url) {
        window.location.href = data.auth_url
      }
    } catch (error) {
      console.error('Failed to get YouTube auth URL:', error)
      throw error
    }
  },

  disconnect: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({
      isConnected: false,
      connectionStatus: 'disconnected',
      tokens: null,
      channel: null
    })
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
        throw new Error('Failed to authenticate with YouTube')
      }

      const data = await response.json()
      
      const tokens: YouTubeTokens = {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in,
        expires_at: Date.now() + (data.expires_in * 1000)
      }

      const channel = data.channel_info

      // Store tokens and channel info securely (in production, consider more secure storage)
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ tokens, channel }))

      set({
        isConnected: true,
        connectionStatus: 'connected',
        tokens,
        channel
      })

      // Also save the connection to the social_media_accounts table
      try {
        const user = (window as any)?.Clerk?.user
        console.log('Attempting to save YouTube connection to database...', {
          hasUser: !!user,
          userId: user?.id,
          hasAccessToken: !!tokens.access_token,
          apiUrl: process.env.NEXT_PUBLIC_API_URL
        })
        
        if (user?.id && tokens.access_token) {
          console.log('Making request to backend YouTube connect endpoint...')
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/social-media/connect/youtube`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-User-ID': user.id,
            },
            body: JSON.stringify({ access_token: tokens.access_token }),
          })
          
          console.log('YouTube backend response status:', response.status)
          
          if (response.ok) {
            const result = await response.json()
            console.log('✅ YouTube connection saved to database successfully!', result)
          } else {
            const errorText = await response.text()
            console.error('❌ Failed to save YouTube connection to database:', errorText)
            console.error('Response status:', response.status)
          }
        } else {
          console.warn('Missing required data for database save:', {
            userId: user?.id,
            hasAccessToken: !!tokens.access_token
          })
        }
      } catch (error) {
        console.error('❌ Error saving YouTube connection to database:', error)
      }

      return data
    } catch (error) {
      console.error('YouTube callback error:', error)
      throw error
    }
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
        body: JSON.stringify({ refresh_token: tokens.refresh_token }),
      })

      if (!response.ok) {
        throw new Error('Failed to refresh token')
      }

      const data = await response.json()
      
      const newTokens: YouTubeTokens = {
        ...tokens,
        access_token: data.access_token,
        expires_in: data.expires_in,
        expires_at: Date.now() + (data.expires_in * 1000)
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(newTokens))
      
      set({ tokens: newTokens })
      
      return newTokens
    } catch (error) {
      console.error('Token refresh error:', error)
      // If refresh fails, disconnect user
      get().disconnect()
      throw error
    }
  },

  uploadVideo: async (videoData: VideoUploadData) => {
    const { tokens } = get()
    if (!tokens) {
      throw new Error('Not authenticated with YouTube')
    }

    // Check if token needs refresh
    if (Date.now() >= tokens.expires_at) {
      await get().refreshToken()
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/youtube/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: get().tokens?.access_token,
          ...videoData
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to upload video')
      }

      return await response.json()
    } catch (error) {
      console.error('Video upload error:', error)
      throw error
    }
  },

  uploadVideoFile: async (videoData: VideoFileUploadData) => {
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
  }
}))

// Initialize store from localStorage
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    try {
      const data = JSON.parse(stored)
      // Check if token is still valid (with some buffer time)
      if (data.tokens && data.tokens.expires_at && Date.now() < data.tokens.expires_at - 300000) { // 5 min buffer
        useYouTubeStore.setState({
          isConnected: true,
          connectionStatus: 'connected',
          tokens: data.tokens,
          channel: data.channel || null // Restore channel info if available
        })
      } else {
        // Token expired, remove it
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch (error) {
      console.error('Failed to parse stored YouTube tokens:', error)
      localStorage.removeItem(STORAGE_KEY)
    }
  }
}
