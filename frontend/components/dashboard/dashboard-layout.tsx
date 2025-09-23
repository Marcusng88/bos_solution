/**
 * Enhanced Dashboard Layout with Flexible Sidebar
 * 
 * Features:
 * - Auto-expanding sidebar on hover near left edge (4px trigger zone)
 * - Collapsible sidebar that shows only icons when collapsed
 * - Pin/unpin functionality for manual control
 * - Smooth animations and transitions
 * - Auto-hide after 300ms delay when mouse leaves sidebar area
 * - Responsive design for mobile and desktop
 */

"use client"

import type React from "react"
import { useState, useRef, useCallback } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { UserButton } from "@clerk/nextjs"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { LoadingScreen } from "@/components/ui/loading-screen"
import { EnhancedSidebarAnimations } from "./enhanced-sidebar-animations"
import {
  Brain,
  Calendar,
  Send,
  BarChart3,
  Lightbulb,
  DollarSign,
  Menu,
  X,
  Search,
  Eye,
  Settings,
  Home,
  Pin,
  PinOff,
} from "lucide-react"

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: "Welcome", href: "/welcome", icon: Home },
  { name: "Competitor Intelligence", href: "/dashboard/competitors", icon: Search },
  { name: "Content Planning", href: "/dashboard", icon: Calendar },
  { name: "Publishing", href: "/dashboard/publishing", icon: Send },
  { name: "Campaign & Optimization", href: "/dashboard/optimization", icon: Lightbulb },
  { name: "ROI Dashboard", href: "/dashboard/roi", icon: DollarSign },
  { name: "Continuous Monitoring", href: "/dashboard/monitoring", icon: Eye },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, isLoaded } = useUser()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarExpanded, setSidebarExpanded] = useState(false)
  const [sidebarPinned, setSidebarPinned] = useState(false)
  const [onboardingComplete, setOnboardingComplete] = useState<boolean | null>(null)
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(true)
  const pathname = usePathname()
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const sidebarRef = useRef<HTMLDivElement>(null)

  // Handle sidebar hover interactions
  const handleSidebarMouseEnter = useCallback(() => {
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current)
      hoverTimeoutRef.current = null
    }
    if (!sidebarPinned) {
      setSidebarExpanded(true)
    }
  }, [sidebarPinned])

  const handleSidebarMouseLeave = useCallback(() => {
    if (!sidebarPinned && hoverTimeoutRef.current === null) {
      hoverTimeoutRef.current = setTimeout(() => {
        setSidebarExpanded(false)
        hoverTimeoutRef.current = null
      }, 300) // 300ms delay before hiding
    }
  }, [sidebarPinned])

  const handleHoverZoneEnter = useCallback(() => {
    if (!sidebarPinned) {
      setSidebarExpanded(true)
    }
  }, [sidebarPinned])

  const toggleSidebarPin = useCallback(() => {
    setSidebarPinned(!sidebarPinned)
    if (!sidebarPinned) {
      setSidebarExpanded(true)
    }
  }, [sidebarPinned])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (!isLoaded || !user) return

    const checkOnboardingStatus = async () => {
      try {
        console.log('🔍 Dashboard: Checking onboarding status...');
        setIsCheckingOnboarding(true)
        
        // Check multiple sources for onboarding completion
        const sources = {
          // 1. Clerk metadata (existing)
          clerkMetadata: (user?.publicMetadata as any)?.onboardingComplete === true || 
                        (user?.unsafeMetadata as any)?.onboardingComplete === true,
          
          // 2. Local storage (more persistent)
          localStorage: typeof window !== "undefined" && localStorage.getItem("onboardingComplete") === "true",
          
          // 3. Session storage (temporary override)
          sessionStorage: typeof window !== "undefined" && sessionStorage.getItem("skipOnboardingGuard") === "true"
        }

        console.log('🔍 Dashboard: Onboarding sources:', sources);

        // If any source indicates completion, consider it complete
        const isComplete = Object.values(sources).some(Boolean)
        
        if (isComplete) {
          console.log('✅ Dashboard: Onboarding complete from local sources');
          setOnboardingComplete(true)
          return
        }

        // 4. Check database status (most reliable)
        try {
          console.log('🔍 Dashboard: Checking database onboarding status...');
          const apiClient = new (await import('@/lib/api-client')).ApiClient()
          const dbStatus = await apiClient.getUserOnboardingStatus(user.id)
          console.log('✅ Dashboard: Database status response:', dbStatus);
          
          if (dbStatus?.onboarding_complete) {
            console.log('✅ Dashboard: Onboarding complete from database');
            setOnboardingComplete(true)
            // Update local storage for future checks
            if (typeof window !== "undefined") {
              localStorage.setItem("onboardingComplete", "true")
            }
            return
          }
        } catch (dbError) {
          console.warn('⚠️ Dashboard: Failed to check database onboarding status:', dbError)
          // Continue with other checks
        }

        // If we get here, onboarding is not complete
        console.log('❌ Dashboard: Onboarding not complete');
        setOnboardingComplete(false)
        
      } catch (error) {
        console.error('❌ Dashboard: Error checking onboarding status:', error)
        setOnboardingComplete(false)
      } finally {
        setIsCheckingOnboarding(false)
      }
    }

    checkOnboardingStatus()
  }, [isLoaded, user])

  useEffect(() => {
    if (!isLoaded || onboardingComplete === null || isCheckingOnboarding) return
    
    // Only redirect if we're not already on the onboarding page and onboarding is not complete
    if (!onboardingComplete && pathname !== "/onboarding") {
      router.replace("/onboarding")
    }
  }, [isLoaded, onboardingComplete, isCheckingOnboarding, router, pathname])

  // If we're already on the onboarding page, don't show loading or redirect
  if (pathname === "/onboarding") {
    return null
  }

  if (!isLoaded || isCheckingOnboarding) {
    return (
      <LoadingScreen 
        message={!isLoaded ? 'Loading...' : 'Checking your setup...'}
        submessage={!isLoaded ? 'Please wait while we load your dashboard' : 'Verifying your account settings'}
      />
    )
  }

  // If onboarding is not complete, don't render the dashboard
  if (!onboardingComplete) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? "block" : "hidden"}`}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-72 flex-col">
          <div className="glass-card border-r border-white/10 shadow-floating">
            <div className="flex h-16 items-center justify-between px-6">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-primary rounded-xl blur-sm opacity-75"></div>
                  <div className="relative p-2.5 bg-gradient-primary rounded-xl shadow-lg">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                </div>
                <div className="flex flex-col">
                  <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">
                    BOSSolution
                  </span>
                  <span className="text-xs text-slate-400 font-medium">AI Marketing Hub</span>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)} className="hover-lift">
                <X className="h-5 w-5" />
              </Button>
            </div>
            <nav className="flex-1 space-y-2 px-4 py-6">
              {navigation.map((item, index) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-300 animate-slide-in-right ${
                      isActive
                        ? "bg-gradient-primary text-white shadow-soft hover-glow"
                        : "text-slate-300 hover:bg-white/10 hover:text-white hover:shadow-soft hover-lift"
                    }`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon className={`mr-3 h-5 w-5 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : ''}`} />
                    <span className="font-medium">{item.name}</span>
                    {isActive && (
                      <div className="ml-auto w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    )}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </div>

      {/* Desktop sidebar with enhanced animations */}
      <div className="hidden lg:block">
        {/* Enhanced Sidebar Animations */}
        <EnhancedSidebarAnimations 
          isExpanded={sidebarExpanded}
          isPinned={sidebarPinned}
          navigationItems={navigation}
        />
        
        {/* Hover zone for sidebar activation */}
        <div 
          className="fixed inset-y-0 left-0 w-4 z-30"
          onMouseEnter={handleHoverZoneEnter}
        />
        
        {/* Collapsible sidebar */}
        <div 
          ref={sidebarRef}
          data-sidebar-main
          className={`fixed inset-y-0 left-0 z-40 flex flex-col transition-all duration-300 ease-in-out ${
            sidebarExpanded || sidebarPinned ? 'w-72' : 'w-16'
          }`}
          onMouseEnter={handleSidebarMouseEnter}
          onMouseLeave={handleSidebarMouseLeave}
        >
          <div className="flex flex-col flex-grow glass-nav border-r border-white/10 shadow-elevated relative overflow-hidden">
            {/* Header section */}
            <div className={`flex items-center h-20 px-4 border-b border-white/10 transition-all duration-300 ${
              sidebarExpanded || sidebarPinned ? 'justify-between' : 'justify-center'
            }`}>
              {(sidebarExpanded || sidebarPinned) ? (
                <div className="flex items-center gap-3" data-sidebar-logo>
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-primary rounded-xl blur-sm opacity-75 animate-pulse-glow"></div>
                    <div className="relative p-2.5 bg-gradient-primary rounded-xl shadow-lg hover-lift">
                      <Brain className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xl font-bold bg-gradient-to-r from-white to-slate-200 bg-clip-text text-transparent">
                      BOSSolution
                    </span>
                    <span className="text-xs text-slate-400 font-medium">AI Marketing Hub</span>
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-primary rounded-xl blur-sm opacity-75 animate-pulse-glow"></div>
                  <div className="relative p-2.5 bg-gradient-primary rounded-xl shadow-lg hover-lift">
                    <Brain className="h-6 w-6 text-white" />
                  </div>
                </div>
              )}
              
              {/* Pin/Unpin button */}
              {(sidebarExpanded || sidebarPinned) && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleSidebarPin}
                  className={`h-8 w-8 hover-lift ${sidebarPinned ? 'text-blue-400' : 'text-slate-400'}`}
                  title={sidebarPinned ? 'Unpin sidebar' : 'Pin sidebar'}
                >
                  {sidebarPinned ? <Pin className="h-4 w-4" /> : <PinOff className="h-4 w-4" />}
                </Button>
              )}
            </div>
            
            {/* Navigation */}
            <nav className={`flex-1 space-y-2 px-2 py-6 transition-all duration-300 ${
              sidebarExpanded || sidebarPinned ? 'px-4' : 'px-2'
            }`}>
              {navigation.map((item, index) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    data-nav-item
                    className={`group flex items-center text-sm font-medium rounded-xl transition-all duration-300 hover-lift animate-slide-in-right ${
                      sidebarExpanded || sidebarPinned ? 'px-4 py-3.5' : 'px-3 py-3 justify-center'
                    } ${
                      isActive
                        ? "bg-gradient-primary text-white shadow-soft hover-glow"
                        : "text-slate-300 hover:bg-white/10 hover:text-white hover:shadow-soft"
                    }`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                    title={!(sidebarExpanded || sidebarPinned) ? item.name : undefined}
                  >
                    <Icon 
                      data-nav-icon
                      className={`transition-all duration-300 group-hover:scale-110 ${
                        sidebarExpanded || sidebarPinned ? 'mr-3 h-5 w-5' : 'h-5 w-5'
                      } ${isActive ? 'text-white' : ''}`} 
                    />
                    {(sidebarExpanded || sidebarPinned) && (
                      <>
                        <span className="font-medium" data-nav-text>{item.name}</span>
                        {isActive && (
                          <div className="ml-auto flex items-center gap-2">
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                          </div>
                        )}
                      </>
                    )}
                  </Link>
                )
              })}
            </nav>
            
            {/* Sidebar footer with user info */}
            {(sidebarExpanded || sidebarPinned) && (
              <div className="p-4 border-t border-white/10" data-user-section>
                <div className="glass-card p-4 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-white">
                        {user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0]?.toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">
                        {user?.firstName || 'User'}
                      </p>
                      <p className="text-xs text-slate-400 truncate">
                        Premium Plan
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className={`transition-all duration-300 ease-in-out ${
        sidebarExpanded || sidebarPinned ? 'lg:pl-72' : 'lg:pl-16'
      }`}>
      {/* Enhanced top bar */}
      <div className="sticky top-0 z-40 glass-nav backdrop-blur-xl border-b border-white/10 shadow-soft">
        <div className="flex h-16 items-center gap-x-4 px-4 sm:gap-x-6 sm:px-6">
          <Button 
            variant="ghost" 
            size="icon" 
            className="lg:hidden hover-lift glass-card" 
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex flex-1 gap-x-4 self-stretch sm:gap-x-6">
            {/* Breadcrumb or page title */}
            <div className="flex items-center">
              <h2 className="text-base sm:text-lg font-semibold text-white truncate">
                {navigation.find(item => item.href === pathname)?.name || 'Dashboard'}
              </h2>
            </div>
            
            <div className="flex flex-1" />
            
            <div className="flex items-center gap-x-2 sm:gap-x-4">
              {/* Search button */}
              <Button variant="ghost" size="icon" className="hover-lift glass-card hidden sm:flex">
                <Search className="h-4 w-4" />
              </Button>
              
              {/* User button with enhanced styling */}
              <div className="glass-card rounded-lg p-1">
                <UserButton 
                  appearance={{
                    elements: {
                      userButtonAvatarBox: "h-8 w-8 shadow-soft",
                      userButtonPopoverCard: "glass-card shadow-floating border border-white/10",
                      userButtonPopoverActionButton: "hover:bg-white/10 transition-all duration-200",
                    }
                  }}
                  afterSignOutUrl="/login"
                />
              </div>
            </div>
          </div>
        </div>
      </div>        {/* Page content with enhanced spacing and animations */}
        <main className="py-6 sm:py-8 animate-fade-in-scale">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="animate-slide-in-up">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
