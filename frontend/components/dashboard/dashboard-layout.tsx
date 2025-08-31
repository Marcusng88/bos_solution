"use client"

import type React from "react"
import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/optimization/theme-toggle"
import { UserButton } from "@clerk/nextjs"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
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
} from "lucide-react"

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
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
  const [onboardingComplete, setOnboardingComplete] = useState<boolean | null>(null)
  const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(true)
  const pathname = usePathname()

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
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-muted-foreground">
            {!isLoaded ? 'Loading...' : 'Checking your setup...'}
          </p>
          {/* Debug button for development */}
          {process.env.NODE_ENV === 'development' && (
            <button
              onClick={() => {
                localStorage.setItem("onboardingComplete", "true")
                setOnboardingComplete(true)
              }}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
            </button>
          )}
        </div>
      </div>
    )
  }

  // If onboarding is not complete, don't render the dashboard
  if (!onboardingComplete) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? "block" : "hidden"}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white dark:bg-gray-800">
          <div className="flex h-16 items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold">BOSSolution</span>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
              <X className="h-6 w-6" />
            </Button>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? "bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="flex items-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold">BOSSolution</span>
            </div>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? "bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
                  }`}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm dark:border-gray-700 dark:bg-gray-800 sm:gap-x-6 sm:px-6 lg:px-8">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-6 w-6" />
          </Button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1" />
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <ThemeToggle />
              <UserButton 
                appearance={{
                  elements: {
                    userButtonAvatarBox: "h-8 w-8",
                    userButtonPopoverCard: "shadow-lg border border-gray-200 dark:border-gray-700",
                    userButtonPopoverActionButton: "hover:bg-gray-50 dark:hover:bg-gray-700",
                  }
                }}
                afterSignOutUrl="/login"
              />
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6 overflow-hidden relative">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 overflow-hidden relative">{children}</div>
        </main>
      </div>
    </div>
  )
}
