"use client"

import React from 'react'
import { cn } from '@/lib/utils'
import { Loader2, Brain, Zap, BarChart3 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'default' | 'brand' | 'pulse' | 'dots' | 'brain'
  className?: string
}

interface LoadingStateProps {
  title?: string
  description?: string
  showProgress?: boolean
  progress?: number
  className?: string
  children?: React.ReactNode
}

interface LoadingOverlayProps {
  isLoading: boolean
  children: React.ReactNode
  loadingContent?: React.ReactNode
  className?: string
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12'
}

export function LoadingSpinner({ 
  size = 'md', 
  variant = 'default', 
  className 
}: LoadingSpinnerProps) {
  if (variant === 'brand') {
    return (
      <div className={cn('flex items-center justify-center', className)}>
        <div className="relative">
          <Brain className={cn(sizeClasses[size], 'text-blue-600 animate-pulse')} />
          <div className="absolute inset-0">
            <Zap className={cn(sizeClasses[size], 'text-yellow-500 animate-ping')} />
          </div>
        </div>
      </div>
    )
  }

  if (variant === 'pulse') {
    return (
      <div className={cn('flex space-x-1', className)}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={cn(
              'rounded-full bg-blue-600 animate-pulse',
              size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'
            )}
            style={{
              animationDelay: `${i * 150}ms`,
              animationDuration: '1s'
            }}
          />
        ))}
      </div>
    )
  }

  if (variant === 'dots') {
    return (
      <div className={cn('flex space-x-1', className)}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={cn(
              'rounded-full bg-blue-600 animate-bounce',
              size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'
            )}
            style={{
              animationDelay: `${i * 100}ms`
            }}
          />
        ))}
      </div>
    )
  }

  if (variant === 'brain') {
    return (
      <div className={cn('relative', className)}>
        <BarChart3 className={cn(sizeClasses[size], 'text-blue-600 animate-spin')} />
        <div className="absolute inset-0 opacity-50">
          <Brain className={cn(sizeClasses[size], 'text-purple-600 animate-pulse')} />
        </div>
      </div>
    )
  }

  return (
    <Loader2 className={cn(sizeClasses[size], 'animate-spin text-blue-600', className)} />
  )
}

export function LoadingState({ 
  title = 'Loading...', 
  description, 
  showProgress = false, 
  progress = 0,
  className,
  children 
}: LoadingStateProps) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center p-8 text-center space-y-4',
      className
    )}>
      <LoadingSpinner size="lg" variant="brain" />
      
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {title}
        </h3>
        {description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 max-w-md">
            {description}
          </p>
        )}
      </div>

      {showProgress && (
        <div className="w-full max-w-xs">
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
        </div>
      )}

      {children}
    </div>
  )
}

export function LoadingOverlay({ 
  isLoading, 
  children, 
  loadingContent,
  className 
}: LoadingOverlayProps) {
  if (!isLoading) {
    return <>{children}</>
  }

  return (
    <div className={cn('relative', className)}>
      <div className="opacity-50 pointer-events-none">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        {loadingContent || <LoadingSpinner size="lg" variant="brain" />}
      </div>
    </div>
  )
}

// Hook for managing loading states
export function useLoadingState(initialState = false) {
  const [isLoading, setIsLoading] = React.useState(initialState)
  const [progress, setProgress] = React.useState(0)
  const [error, setError] = React.useState<string | null>(null)

  const startLoading = React.useCallback(() => {
    setIsLoading(true)
    setProgress(0)
    setError(null)
  }, [])

  const stopLoading = React.useCallback(() => {
    setIsLoading(false)
    setProgress(100)
  }, [])

  const updateProgress = React.useCallback((newProgress: number) => {
    setProgress(Math.min(100, Math.max(0, newProgress)))
  }, [])

  const setLoadingError = React.useCallback((errorMessage: string) => {
    setError(errorMessage)
    setIsLoading(false)
  }, [])

  const withLoading = React.useCallback(async <T,>(
    asyncFn: () => Promise<T>,
    progressCallback?: (progress: number) => void
  ): Promise<T> => {
    try {
      startLoading()
      
      if (progressCallback) {
        progressCallback(25)
        updateProgress(25)
      }
      
      const result = await asyncFn()
      
      if (progressCallback) {
        progressCallback(100)
        updateProgress(100)
      }
      
      stopLoading()
      return result
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred'
      setLoadingError(errorMessage)
      throw error
    }
  }, [startLoading, stopLoading, updateProgress, setLoadingError])

  return {
    isLoading,
    progress,
    error,
    startLoading,
    stopLoading,
    updateProgress,
    setLoadingError,
    withLoading
  }
}

export default {
  Spinner: LoadingSpinner,
  State: LoadingState,
  Overlay: LoadingOverlay,
  useLoadingState
}