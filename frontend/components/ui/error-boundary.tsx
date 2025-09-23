"use client"

import React from 'react'
import { AlertCircle, RefreshCw, Home, Bug, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { cn } from '@/lib/utils'

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
  errorId: string
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<ErrorFallbackProps>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
  resetOnPropsChange?: boolean
  resetKeys?: Array<string | number>
  className?: string
}

interface ErrorFallbackProps {
  error: Error
  errorInfo: React.ErrorInfo | null
  resetError: () => void
  errorId: string
}

interface ErrorDisplayProps {
  title?: string
  description?: string
  error?: Error
  onRetry?: () => void
  onGoHome?: () => void
  showDetails?: boolean
  className?: string
}

// Default error fallback component
function DefaultErrorFallback({ 
  error, 
  errorInfo, 
  resetError, 
  errorId 
}: ErrorFallbackProps) {
  const [copied, setCopied] = React.useState(false)
  const [showDetails, setShowDetails] = React.useState(false)

  const errorDetails = {
    errorId,
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
    componentStack: errorInfo?.componentStack
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy error details:', err)
    }
  }

  const goHome = () => {
    window.location.href = '/dashboard'
  }

  return (
    <div className="min-h-[400px] flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertCircle className="h-6 w-6 text-red-500" />
            <CardTitle className="text-red-600">Something went wrong</CardTitle>
          </div>
          <CardDescription>
            An unexpected error occurred. We've been notified and are working to fix it.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <Bug className="h-4 w-4" />
            <AlertDescription>
              Error ID: <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 rounded">{errorId}</code>
            </AlertDescription>
          </Alert>

          <div className="flex space-x-2">
            <Button onClick={resetError} className="flex-1">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
            <Button variant="outline" onClick={goHome} className="flex-1">
              <Home className="h-4 w-4 mr-2" />
              Go Home
            </Button>
          </div>

          <div className="space-y-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="w-full text-xs"
            >
              {showDetails ? 'Hide' : 'Show'} Error Details
            </Button>

            {showDetails && (
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                    Error Details
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={copyToClipboard}
                    className="h-6 px-2 text-xs"
                  >
                    {copied ? (
                      <Check className="h-3 w-3" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <pre className="text-xs text-gray-700 dark:text-gray-300 overflow-auto max-h-32">
                  {error.message}
                </pre>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Error Boundary class component
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null

  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    }
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: Math.random().toString(36).substring(2, 9)
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      errorInfo
    })

    // Call onError prop if provided
    this.props.onError?.(error, errorInfo)

    // Log to error tracking service
    this.logErrorToService(error, errorInfo)
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys, resetOnPropsChange } = this.props
    const { hasError } = this.state

    if (hasError && prevProps.children !== this.props.children) {
      if (resetOnPropsChange) {
        this.resetError()
      }
    }

    if (hasError && resetKeys) {
      const prevResetKeys = prevProps.resetKeys || []
      if (resetKeys.some((key, idx) => key !== prevResetKeys[idx])) {
        this.resetError()
      }
    }
  }

  resetError = () => {
    if (this.resetTimeoutId) {
      window.clearTimeout(this.resetTimeoutId)
    }

    this.resetTimeoutId = window.setTimeout(() => {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: ''
      })
    }, 100)
  }

  logErrorToService = (error: Error, errorInfo: React.ErrorInfo) => {
    // Here you would typically send error to your error tracking service
    // For now, we'll just log to console
    console.error('Error logged:', {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    })
  }

  render() {
    const { hasError, error, errorInfo, errorId } = this.state
    const { children, fallback: Fallback, className } = this.props

    if (hasError && error) {
      const FallbackComponent = Fallback || DefaultErrorFallback
      return (
        <div className={cn('error-boundary', className)}>
          <FallbackComponent
            error={error}
            errorInfo={errorInfo}
            resetError={this.resetError}
            errorId={errorId}
          />
        </div>
      )
    }

    return children
  }
}

// Simple error display component for use in other components
export function ErrorDisplay({
  title = 'Something went wrong',
  description = 'An error occurred while loading this content.',
  error,
  onRetry,
  onGoHome,
  showDetails = false,
  className
}: ErrorDisplayProps) {
  const [detailsVisible, setDetailsVisible] = React.useState(showDetails)

  return (
    <div className={cn('flex flex-col items-center justify-center p-6 text-center space-y-4', className)}>
      <AlertCircle className="h-12 w-12 text-red-500" />
      
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 max-w-md">
          {description}
        </p>
      </div>

      {error && (
        <div className="w-full max-w-md">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDetailsVisible(!detailsVisible)}
            className="text-xs mb-2"
          >
            {detailsVisible ? 'Hide' : 'Show'} Error Details
          </Button>
          
          {detailsVisible && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <pre className="text-xs text-red-700 dark:text-red-300 overflow-auto max-h-32 text-left">
                {error.message}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="flex space-x-2">
        {onRetry && (
          <Button onClick={onRetry}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        )}
        {onGoHome && (
          <Button variant="outline" onClick={onGoHome}>
            <Home className="h-4 w-4 mr-2" />
            Go Home
          </Button>
        )}
      </div>
    </div>
  )
}

// Hook for error handling in functional components
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null)

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  const handleError = React.useCallback((error: Error | string) => {
    const errorObj = error instanceof Error ? error : new Error(error)
    setError(errorObj)
    console.error('Error handled:', errorObj)
  }, [])

  const withErrorHandling = React.useCallback(async <T,>(
    asyncFn: () => Promise<T>
  ): Promise<T | null> => {
    try {
      return await asyncFn()
    } catch (error) {
      handleError(error instanceof Error ? error : new Error(String(error)))
      return null
    }
  }, [handleError])

  return {
    error,
    resetError,
    handleError,
    withErrorHandling
  }
}

export default ErrorBoundary