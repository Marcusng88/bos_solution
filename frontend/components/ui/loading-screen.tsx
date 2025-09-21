"use client"

import React from "react"
import { Brain } from "lucide-react"

interface LoadingScreenProps {
  message?: string
  submessage?: string
  showLogo?: boolean
}

export function LoadingScreen({ 
  message = "Loading...", 
  submessage,
  showLogo = true 
}: LoadingScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <div className="text-center space-y-6 animate-fade-in-scale">
        {showLogo && (
          <div className="flex justify-center animate-float-gentle">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-primary rounded-2xl blur-lg opacity-75 animate-pulse-glow"></div>
              <div className="relative p-6 bg-gradient-primary rounded-2xl shadow-floating">
                <Brain className="h-12 w-12 text-white" />
              </div>
            </div>
          </div>
        )}
        
        <div className="space-y-3">
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary/30 border-t-primary"></div>
          </div>
          
          <div className="space-y-2">
            <p className="text-xl font-semibold text-slate-900 dark:text-white animate-slide-in-up">
              {message}
            </p>
            {submessage && (
              <p className="text-sm text-slate-600 dark:text-slate-400 animate-slide-in-up stagger-1">
                {submessage}
              </p>
            )}
          </div>
        </div>
        
        {/* Loading dots animation */}
        <div className="flex justify-center space-x-2 animate-slide-in-up stagger-2">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 bg-primary rounded-full animate-bounce"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export function LoadingSpinner({ size = "md", className = "" }: { size?: "sm" | "md" | "lg", className?: string }) {
  const sizeClasses = {
    sm: "h-4 w-4 border-2",
    md: "h-6 w-6 border-2", 
    lg: "h-8 w-8 border-3"
  }
  
  return (
    <div className={`animate-spin rounded-full border-primary/30 border-t-primary ${sizeClasses[size]} ${className}`} />
  )
}

export function LoadingCard() {
  return (
    <div className="glass-card p-6 animate-pulse">
      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
          <div className="space-y-2 flex-1">
            <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
            <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2"></div>
          </div>
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-5/6"></div>
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4"></div>
        </div>
      </div>
    </div>
  )
}