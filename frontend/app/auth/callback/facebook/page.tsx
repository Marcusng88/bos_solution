"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, CheckCircle, XCircle, Facebook } from "lucide-react"
import { handleOAuthCallback } from "@/lib/oauth"
import { useToast } from "@/hooks/use-toast"

export default function FacebookCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState<string>('')

  useEffect(() => {
    handleFacebookCallback()
  }, [])

  const handleFacebookCallback = async () => {
    try {
      // Get the full URL including query parameters
      const fullUrl = window.location.href
      
      // Handle OAuth callback
      const result = handleOAuthCallback('facebook', fullUrl)
      
      if (!result) {
        setStatus('error')
        setErrorMessage('Invalid OAuth response')
        return
      }

      const { code, state } = result

      // TODO: Send authorization code to backend for token exchange
      // For now, simulate successful connection
      console.log('Facebook OAuth successful:', { code, state })
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setStatus('success')
      
      // Show success toast
      toast({
        title: "Facebook Connected!",
        description: "Your Facebook page has been successfully connected.",
      })
      
      // Redirect to dashboard after delay
      setTimeout(() => {
        router.push('/dashboard')
      }, 1500)
      
    } catch (error) {
      console.error('Facebook OAuth error:', error)
      setStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error occurred')
    }
  }

  const handleRetry = () => {
    setStatus('loading')
    setErrorMessage('')
    handleFacebookCallback()
  }

  const handleGoToDashboard = () => {
    router.push('/dashboard')
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-100 dark:bg-blue-900/20 rounded-full flex items-center justify-center mb-4">
              <Facebook className="h-8 w-8 text-blue-600" />
            </div>
            <CardTitle>Connecting Facebook</CardTitle>
            <CardDescription>
              Please wait while we connect your Facebook page...
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
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
              Facebook Connected!
            </CardTitle>
            <CardDescription>
              Your Facebook page has been successfully connected to BOS Solution.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <p className="text-sm text-green-700 dark:text-green-300">
                You can now:
              </p>
              <ul className="text-sm text-green-600 dark:text-green-400 mt-2 space-y-1">
                <li>• Monitor your Facebook page performance</li>
                <li>• Track post engagement and reach</li>
                <li>• Analyze audience demographics</li>
                <li>• Get insights on competitor pages</li>
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
              We couldn't connect your Facebook page. Please try again.
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

