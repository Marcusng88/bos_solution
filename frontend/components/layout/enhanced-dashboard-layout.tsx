"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/optimization/theme-toggle"
import { UserButton } from "@clerk/nextjs"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { ErrorBoundary } from "@/components/ui/error-boundary"
import { LoadingState, LoadingOverlay } from "@/components/ui/enhanced-loading"
import { cn } from "@/lib/utils"
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
  Bell,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"

interface EnhancedDashboardLayoutProps {
  children: React.ReactNode
  title?: string
  description?: string
  showBreadcrumbs?: boolean
  actions?: React.ReactNode
  sidebar?: {
    collapsible?: boolean
    defaultCollapsed?: boolean
    width?: 'narrow' | 'normal' | 'wide'
  }
  className?: string
}

interface NavigationItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: number
  disabled?: boolean
  external?: boolean
  description?: string
}

const navigation: NavigationItem[] = [
  { 
    name: "Dashboard", 
    href: "/dashboard", 
    icon: Home, 
    description: "Overview and insights" 
  },
  { 
    name: "Competitor Intelligence", 
    href: "/dashboard/competitors", 
    icon: Search, 
    description: "Monitor competitors" 
  },
  { 
    name: "Content Planning", 
    href: "/dashboard/content", 
    icon: Calendar, 
    description: "Plan your content strategy" 
  },
  { 
    name: "Publishing", 
    href: "/dashboard/publishing", 
    icon: Send, 
    description: "Publish and schedule content" 
  },
  { 
    name: "Campaign & Optimization", 
    href: "/dashboard/optimization", 
    icon: Lightbulb, 
    description: "Optimize your campaigns" 
  },
  { 
    name: "ROI Dashboard", 
    href: "/dashboard/roi", 
    icon: DollarSign, 
    description: "Track return on investment" 
  },
  { 
    name: "Continuous Monitoring", 
    href: "/dashboard/monitoring", 
    icon: Eye, 
    description: "Real-time monitoring" 
  },
  { 
    name: "Settings", 
    href: "/dashboard/settings", 
    icon: Settings, 
    description: "Account and preferences" 
  },
]

// Custom hook for dashboard state management
function useDashboardState() {
  const { user, isLoaded } = useUser()
  const router = useRouter()
  const pathname = usePathname()
  
  const [sidebarOpen, setSidebarOpen] = React.useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
  const [onboardingComplete, setOnboardingComplete] = React.useState<boolean | null>(null)
  const [isCheckingOnboarding, setIsCheckingOnboarding] = React.useState(true)
  const [notifications, setNotifications] = React.useState<number>(0)

  // Onboarding check logic (enhanced from original)
  React.useEffect(() => {
    if (!isLoaded || !user) return

    const checkOnboardingStatus = async () => {
      try {
        console.log('🔍 Dashboard: Checking onboarding status...')
        setIsCheckingOnboarding(true)
        
        // Check multiple sources for onboarding completion
        const sources = {
          clerkMetadata: (user?.publicMetadata as any)?.onboardingComplete === true || 
                        (user?.unsafeMetadata as any)?.onboardingComplete === true,
          localStorage: typeof window !== 'undefined' ? 
                       localStorage.getItem("onboardingComplete") === "true" : false,
          userProfile: user?.firstName && user?.lastName && user?.emailAddresses?.length > 0
        }

        console.log('🔍 Onboarding sources check:', sources)

        // Consider onboarding complete if any reliable source says so
        const isComplete = Boolean(sources.clerkMetadata || sources.localStorage || sources.userProfile)

        console.log('🔍 Final onboarding status:', isComplete)
        setOnboardingComplete(isComplete)
        
        // Sync to localStorage if not already there
        if (isComplete && typeof window !== 'undefined') {
          localStorage.setItem("onboardingComplete", "true")
        }
      } catch (error) {
        console.error('🔍 Error checking onboarding status:', error)
        // If there's an error, assume onboarding is complete to prevent blocking
        setOnboardingComplete(true)
      } finally {
        setIsCheckingOnboarding(false)
      }
    }

    checkOnboardingStatus()
  }, [isLoaded, user])

  // Redirect to onboarding if needed
  React.useEffect(() => {
    if (!isLoaded || onboardingComplete === null || isCheckingOnboarding) return
    
    if (!onboardingComplete && pathname !== "/onboarding") {
      router.replace("/onboarding")
    }
  }, [isLoaded, onboardingComplete, isCheckingOnboarding, router, pathname])

  // Close sidebar on route change (mobile)
  React.useEffect(() => {
    setSidebarOpen(false)
  }, [pathname])

  // Load notifications (placeholder)
  React.useEffect(() => {
    // TODO: Load actual notifications
    setNotifications(3)
  }, [])

  return {
    user,
    isLoaded,
    pathname,
    sidebarOpen,
    setSidebarOpen,
    sidebarCollapsed,
    setSidebarCollapsed,
    onboardingComplete,
    isCheckingOnboarding,
    notifications
  }
}

// Breadcrumb component
function Breadcrumbs({ pathname }: { pathname: string }) {
  const pathSegments = pathname.split('/').filter(Boolean)
  
  if (pathSegments.length <= 1) return null

  const breadcrumbs = pathSegments.map((segment, index) => {
    const href = '/' + pathSegments.slice(0, index + 1).join('/')
    const name = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ')
    const isLast = index === pathSegments.length - 1
    
    return {
      name,
      href,
      isLast
    }
  })

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
      <Link href="/dashboard" className="hover:text-gray-900 dark:hover:text-gray-100">
        Home
      </Link>
      {breadcrumbs.map((crumb, index) => (
        <React.Fragment key={crumb.href}>
          <span>/</span>
          {crumb.isLast ? (
            <span className="text-gray-900 dark:text-gray-100 font-medium">
              {crumb.name}
            </span>
          ) : (
            <Link 
              href={crumb.href} 
              className="hover:text-gray-900 dark:hover:text-gray-100"
            >
              {crumb.name}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
}

// Navigation item component with enhanced accessibility
function NavigationItem({ 
  item, 
  isActive, 
  collapsed, 
  onClick 
}: { 
  item: NavigationItem
  isActive: boolean
  collapsed: boolean
  onClick?: () => void
}) {
  const Icon = item.icon
  
  return (
    <Link
      href={item.href}
      className={cn(
        "group flex items-center rounded-md text-sm font-medium transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
        collapsed ? "px-2 py-2 justify-center" : "px-2 py-2",
        isActive
          ? "bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white"
      )}
      onClick={onClick}
      title={collapsed ? item.name : undefined}
      aria-label={collapsed ? item.name : undefined}
      aria-current={isActive ? "page" : undefined}
    >
      <Icon className={cn("flex-shrink-0 h-5 w-5", !collapsed && "mr-3")} />
      {!collapsed && (
        <div className="flex-1 min-w-0">
          <span className="truncate">{item.name}</span>
          {item.description && (
            <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {item.description}
            </div>
          )}
        </div>
      )}
      {!collapsed && item.badge && item.badge > 0 && (
        <span className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
          {item.badge > 99 ? '99+' : item.badge}
        </span>
      )}
    </Link>
  )
}

// Sidebar component
function Sidebar({ 
  collapsed, 
  onToggleCollapse, 
  pathname,
  onClose 
}: {
  collapsed: boolean
  onToggleCollapse: () => void
  pathname: string
  onClose?: () => void
}) {
  return (
    <div className={cn(
      "flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-200",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold">BOSSolution</span>
          </div>
        )}
        
        {collapsed && (
          <div className="p-2 bg-blue-600 rounded-lg">
            <Brain className="h-6 w-6 text-white" />
          </div>
        )}

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            className="hidden lg:flex"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
          
          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="lg:hidden"
              aria-label="Close sidebar"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <NavigationItem
              key={item.href}
              item={item}
              isActive={isActive}
              collapsed={collapsed}
              onClick={onClose}
            />
          )
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <HelpCircle className="h-4 w-4" />
            <span>Need help?</span>
          </div>
        </div>
      )}
    </div>
  )
}

// Main layout component
export function EnhancedDashboardLayout({
  children,
  title,
  description,
  showBreadcrumbs = true,
  actions,
  sidebar = { collapsible: true, defaultCollapsed: false },
  className
}: EnhancedDashboardLayoutProps) {
  const {
    user,
    isLoaded,
    pathname,
    sidebarOpen,
    setSidebarOpen,
    sidebarCollapsed,
    setSidebarCollapsed,
    onboardingComplete,
    isCheckingOnboarding,
    notifications
  } = useDashboardState()

  // Initialize collapsed state
  React.useEffect(() => {
    if (sidebar.defaultCollapsed) {
      setSidebarCollapsed(true)
    }
  }, [sidebar.defaultCollapsed, setSidebarCollapsed])

  // Loading states
  if (!isLoaded || isCheckingOnboarding) {
    return (
      <LoadingState
        title={!isLoaded ? 'Loading...' : 'Checking your setup...'}
        description={!isLoaded ? 'Initializing your dashboard...' : 'Verifying your account status...'}
        showProgress={false}
      />
    )
  }

  // Onboarding redirect (don't render anything)
  if (pathname === "/onboarding" || !onboardingComplete) {
    return null
  }

  return (
    <ErrorBoundary>
      <div className={cn("min-h-screen bg-gray-50 dark:bg-gray-900", className)}>
        {/* Mobile sidebar backdrop */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Mobile sidebar */}
        <div className={cn(
          "fixed inset-y-0 left-0 z-50 lg:hidden transition-transform duration-300",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <Sidebar
            collapsed={false}
            onToggleCollapse={() => {}}
            pathname={pathname}
            onClose={() => setSidebarOpen(false)}
          />
        </div>

        {/* Desktop sidebar */}
        <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:z-40">
          <Sidebar
            collapsed={sidebar.collapsible ? sidebarCollapsed : false}
            onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
            pathname={pathname}
          />
        </div>

        {/* Main content */}
        <div className={cn(
          "lg:pl-64 transition-all duration-200",
          sidebar.collapsible && sidebarCollapsed && "lg:pl-16"
        )}>
          {/* Top bar */}
          <header className="sticky top-0 z-30 flex h-16 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm dark:border-gray-700 dark:bg-gray-800 sm:gap-x-6 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="lg:hidden" 
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu className="h-6 w-6" />
            </Button>

            {/* Title and description */}
            <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
              <div className="flex flex-1 flex-col justify-center">
                {title && (
                  <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100 truncate">
                    {title}
                  </h1>
                )}
                {description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {description}
                  </p>
                )}
              </div>
              
              {/* Actions */}
              {actions && (
                <div className="flex items-center gap-2">
                  {actions}
                </div>
              )}
            </div>

            {/* Right side items */}
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Notifications */}
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-600 text-white text-xs rounded-full flex items-center justify-center">
                    {notifications > 9 ? '9+' : notifications}
                  </span>
                )}
              </Button>

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
          </header>

          {/* Page content */}
          <main className="flex flex-1 flex-col">
            <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
              {/* Breadcrumbs */}
              {showBreadcrumbs && <Breadcrumbs pathname={pathname} />}
              
              {/* Content */}
              <LoadingOverlay isLoading={false}>
                <ErrorBoundary>
                  {children}
                </ErrorBoundary>
              </LoadingOverlay>
            </div>
          </main>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default EnhancedDashboardLayout