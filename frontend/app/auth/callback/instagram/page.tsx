"use client"

import { useEffect, useState, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, CheckCircle, XCircle, Instagram } from "lucide-react"
import { handleOAuthCallback } from "@/lib/oauth"
import { useToast } from "@/hooks/use-toast"

function InstagramCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    handleInstagramCallback()
  }, [])

  const handleInstagramCallback = async () => {
    try {
      // Get the full URL including query parameters
      const fullUrl = window.location.href
      
      // Handle OAuth callback
      const result = handleOAuthCallback('instagram', fullUrl)
      
      if (!result) {
        setStatus('error')
        setErrorMessage('Invalid OAuth response')
        return
      }

      const { code, state } = result

      // TODO: Send authorization code to backend for token exchange
      // For now, simulate successful connection
      console.log('Instagram OAuth successful:', { code, state })
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setStatus('success')
      
      // Show success toast
      toast({
        title: "Instagram Connected!",
        description: "Your Instagram account has been successfully connected.",
      })
      
      // Redirect to dashboard after delay
      setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
      
    } catch (error) {
      console.error('Instagram OAuth error:', error)
      setStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error occurred')
    }
  }

  const handleRetry = () => {
    setStatus('loading')
    setErrorMessage('')
    handleInstagramCallback()
  }

  const handleGoToDashboard = () => {
    router.push('/dashboard')
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-pink-100 dark:bg-pink-900/20 rounded-full flex items-center justify-center mb-4">
              <Instagram className="h-8 w-8 text-pink-600" />
            </div>
            <CardTitle>Connecting Instagram</CardTitle>
            <CardDescription>
              Please wait while we connect your Instagram account...
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-pink-600 mx-auto mb-4" />
            <p className="text-sm text-muted-foreground">
              This may take a few moments
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <CardTitle className="text-green-800 dark:text-green-200">
              Instagram Connected!
            </CardTitle>
            <CardDescription>
              Your Instagram account has been successfully connected to BOS Solution.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <p className="text-sm text-green-700 dark:text-green-300">
                You can now:
              </p>
              <ul className="text-sm text-green-600 dark:text-green-400 mt-2 space-y-1">
                <li>• Monitor your Instagram performance</li>
                <li>• Track engagement metrics</li>
                <li>• Analyze competitor activity</li>
                <li>• Get AI-powered insights</li>
              </ul>
            </div>
            <Button onClick={handleGoToDashboard} className="w-full">
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4">
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
            <CardTitle className="text-red-800 dark:text-red-200">
              Connection Failed
            </CardTitle>
            <CardDescription>
              We couldn't connect your Instagram account. Please try again.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="p-4 bg-red-50 dark:bg-red-950/20 rounded-lg">
              <p className="text-sm text-red-700 dark:text-red-300">
                Error: {errorMessage}
              </p>
            </div>
            <div className="space-y-2">
              <Button onClick={handleRetry} className="w-full">
                Try Again
              </Button>
              <Button onClick={handleGoToDashboard} variant="outline" className="w-full">
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return null
}

export default function InstagramCallbackPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto p-8 max-w-md">
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
              <p>Processing Instagram connection...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    }>
      <InstagramCallbackContent />
    </Suspense>
  )
}

