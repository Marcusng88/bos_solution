"use client"

import { useEffect, useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, CheckCircle, AlertCircle, Youtube } from "lucide-react"
import { useYouTubeStore } from "@/hooks/use-youtube"
import { useToast } from "@/hooks/use-toast"

function YouTubeCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const { handleCallback, getROIAnalytics } = useYouTubeStore()
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const code = searchParams.get('code')
    const error = searchParams.get('error')

    if (error) {
      setStatus('error')
      setMessage('Authorization was denied or cancelled.')
      return
    }

    if (!code) {
      setStatus('error')
      setMessage('No authorization code received.')
      return
    }

    handleYouTubeCallback(code)
  }, [searchParams])

  const handleYouTubeCallback = async (code: string) => {
    try {
      setStatus('loading')
      setMessage('Exchanging authorization code for access tokens...')
      
      await handleCallback(code)

      // After tokens are stored, fetch ROI analytics first
      setMessage('Fetching ROI analytics...')
      try {
        const roi = await getROIAnalytics()

        // Trigger JSON download
        const blob = new Blob([JSON.stringify(roi, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'youtube_roi_analytics.json'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      } catch (e) {
        console.error('ROI fetch error:', e)
      }

      setStatus('success')
      setMessage('Successfully connected to YouTube!')
      
      toast({
        title: "YouTube Connected!",
        description: "Your YouTube account has been successfully connected.",
      })

      // Get the return context from session storage
      const returnContext = sessionStorage.getItem('youtube_return_context') || 'onboarding'
      const returnStep = sessionStorage.getItem('youtube_return_step')
      
      // Clear the context from storage (but keep the step for now)
      sessionStorage.removeItem('youtube_return_context')

      // Redirect based on context after a short delay
      setTimeout(() => {
        if (returnContext === 'settings') {
          router.push('/dashboard/settings')
        } else if (returnContext === 'publishing') {
          router.push('/dashboard/publishing')
        } else {
          // For onboarding users, go to dashboard since preferences are already saved
          router.push('/dashboard')
        }
      }, 2000)
      
    } catch (error: any) {
      console.error('YouTube callback error:', error)
      setStatus('error')
      setMessage(error.message || 'Failed to connect to YouTube. Please try again.')
      
      toast({
        title: "Connection Failed",
        description: error.message || 'Failed to connect to YouTube.',
        variant: "destructive",
      })
    }
  }

  const handleReturnToOnboarding = () => {
    const returnContext = sessionStorage.getItem('youtube_return_context') || 'onboarding'
    sessionStorage.removeItem('youtube_return_context')
    
    if (returnContext === 'settings') {
      router.push('/dashboard/settings')
    } else if (returnContext === 'publishing') {
      router.push('/dashboard/publishing')
    } else {
      // For onboarding users, go to dashboard since preferences are already saved
      router.push('/dashboard')
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'loading':
        return <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-600" />
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-600" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'loading':
        return 'border-blue-200 bg-blue-50 dark:bg-blue-900/20'
      case 'success':
        return 'border-green-200 bg-green-50 dark:bg-green-900/20'
      case 'error':
        return 'border-red-200 bg-red-50 dark:bg-red-900/20'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <Card className={`w-full max-w-md ${getStatusColor()}`}>
        <CardHeader>
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="p-3 bg-white dark:bg-gray-800 rounded-full shadow-sm">
              <Youtube className="h-8 w-8 text-red-600" />
            </div>
            <div>
              <CardTitle className="text-xl">YouTube Connection</CardTitle>
              <CardDescription>
                {status === 'loading' && 'Connecting your YouTube account...'}
                {status === 'success' && 'Successfully connected!'}
                {status === 'error' && 'Connection failed'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center space-y-4">
            <div className="flex items-center justify-center">
              {getStatusIcon()}
            </div>
            
            <p className="text-center text-sm text-muted-foreground">
              {message}
            </p>

            {status === 'success' && (
              <div className="text-center space-y-2">
                <p className="text-sm text-green-700 dark:text-green-300">
                  You'll be redirected to dashboard shortly...
                </p>
                <Button 
                  onClick={handleReturnToOnboarding}
                  className="w-full"
                >
                  Continue to Dashboard
                </Button>
              </div>
            )}

            {status === 'error' && (
              <div className="w-full space-y-2">
                <Button 
                  onClick={handleReturnToOnboarding}
                  variant="outline"
                  className="w-full"
                >
                  Go to Dashboard
                </Button>
                <p className="text-xs text-center text-muted-foreground">
                  You can try connecting again from the dashboard
                </p>
              </div>
            )}

            {status === 'loading' && (
              <div className="w-full">
                <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function YouTubeCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <YouTubeCallbackContent />
    </Suspense>
  )
}
