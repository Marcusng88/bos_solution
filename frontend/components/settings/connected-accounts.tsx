"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Facebook, Instagram, Twitter, Linkedin, Youtube, Mail, Settings, RefreshCw, Clock } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useUser } from "@clerk/nextjs"
import GradientText from "@/components/effects/GradientText"
import ShinyText from "@/components/effects/ShinyText"

interface ConnectedAccount {
  platform: string
  username: string
  displayName: string
  isConnected: boolean
  lastSync?: string
  permissions: string[]
}

export function ConnectedAccounts() {
  const { toast } = useToast()
  const { user } = useUser()
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showIgGuide, setShowIgGuide] = useState(false)
  const [igGuideReason, setIgGuideReason] = useState<string>("")

  // Get real user data and check actual connections from database
  useEffect(() => {
    if (!user) return

    const checkRealConnections = async () => {
      try {
        // First fetch connected accounts from database
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
        const response = await fetch(`${apiBase}/social-media/connected-accounts`, {
          headers: {
            'X-User-ID': user.id,
          },
        })

        const dbAccounts = response.ok ? (await response.json()).accounts || [] : []
        console.log('Connected accounts from database:', dbAccounts)

        // Create account list with database status
        const realAccounts: ConnectedAccount[] = [
          {
            platform: "facebook",
            username: "",
            displayName: "Facebook",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "instagram", 
            username: "",
            displayName: "Instagram",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "twitter",
            username: "",
            displayName: "Twitter",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "linkedin",
            username: "",
            displayName: "LinkedIn",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "youtube",
            username: "",
            displayName: "YouTube",
            isConnected: false,
            lastSync: "",
            permissions: []
          }
        ]

        // Update accounts with database information
        realAccounts.forEach(account => {
          const dbAccount = dbAccounts.find((db: any) => db.platform === account.platform)
          if (dbAccount) {
            account.isConnected = true
            account.username = dbAccount.username || dbAccount.account_name || ""
            account.displayName = dbAccount.account_name || account.displayName
            account.lastSync = dbAccount.updated_at || dbAccount.created_at || ""
            account.permissions = Object.keys(dbAccount.permissions || {})
          }
        })

        setAccounts(realAccounts)
      } catch (error) {
        console.error('Error fetching connected accounts:', error)
        
        // Fallback to basic account list
        const fallbackAccounts: ConnectedAccount[] = [
          {
            platform: "facebook",
            username: "",
            displayName: "Facebook",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "instagram",
            username: "",
            displayName: "Instagram", 
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "twitter",
            username: "",
            displayName: "Twitter",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "linkedin",
            username: "",
            displayName: "LinkedIn",
            isConnected: false,
            lastSync: "",
            permissions: []
          },
          {
            platform: "youtube",
            username: "",
            displayName: "YouTube",
            isConnected: false,
            lastSync: "",
            permissions: []
          }
        ]
        setAccounts(fallbackAccounts)
      }
    }

    checkRealConnections()
  }, [user])

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "facebook":
        return Facebook
      case "instagram":
        return Instagram
      case "twitter":
        return Twitter
      case "linkedin":
        return Linkedin
      case "youtube":
        return Youtube
      default:
        return Mail
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case "facebook":
        return "bg-blue-600"
      case "instagram":
        return "bg-pink-600"
      case "twitter":
        return "bg-black"
      case "linkedin":
        return "bg-blue-700"
      case "youtube":
        return "bg-red-600"
      default:
        return "bg-gray-600"
    }
  }

  const getPlatformName = (platform: string) => {
    switch (platform) {
      case "facebook":
        return "Facebook"
      case "instagram":
        return "Instagram"
      case "twitter":
        return "Twitter/X"
      case "linkedin":
        return "LinkedIn"
      case "youtube":
        return "YouTube"
      default:
        return platform
    }
  }

  const handleRefresh = async (platform: string) => {
    setIsLoading(true)
    try {
      // Simulate API call for all platforms
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast({
        title: "Refreshed",
        description: `${getPlatformName(platform)} connection refreshed successfully.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to refresh ${getPlatformName(platform)} connection.`,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async (platform: string) => {
    try {
      // Simulate API call for all platforms
      await new Promise(resolve => setTimeout(resolve, 500))
      setAccounts(prev => prev.map(acc => 
        acc.platform === platform 
          ? { ...acc, isConnected: false, username: "", displayName: "", permissions: [] }
          : acc
      ))
      toast({
        title: "Disconnected",
        description: `${getPlatformName(platform)} has been disconnected.`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to disconnect ${getPlatformName(platform)}.`,
        variant: "destructive",
      })
    }
  }

  const handleConnect = async (platform: string) => {
    // Show "Coming Soon" message for all platforms
    toast({
      title: "Coming Soon! 🚀",
      description: `${getPlatformName(platform)} integration is currently under development. Stay tuned for updates!`,
    })
  }

  return (
    <div className="space-y-6 relative">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute inset-0">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
          <div className="absolute top-0 -right-4 w-72 h-72 bg-cyan-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-teal-500/6 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between relative z-10">
        <div>
          <h1 className="text-3xl font-bold">
            <GradientText colors={['#3b82f6', '#1d4ed8', '#6366f1']}>
              Settings
            </GradientText>
          </h1>
          <p className="text-muted-foreground">
            <ShinyText text="Manage your account and connected services" />
          </p>
        </div>
        <Button variant="outline" size="sm" className="backdrop-blur-sm bg-white/70 dark:bg-gray-900/70 border-white/20">
          <Settings className="mr-2 h-4 w-4" />
          Account Settings
        </Button>
      </div>

      {/* User Info */}
      <Card className="relative backdrop-blur-sm bg-white/70 dark:bg-gray-900/70 border border-white/20 shadow-xl animate-slideUp">
        <CardHeader>
          <CardTitle>
            <GradientText colors={['#059669', '#10b981']}>
              Account Information
            </GradientText>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress}</p>
            <p><strong>Name:</strong> {user?.fullName || `${user?.firstName} ${user?.lastName}`}</p>
            <p><strong>User ID:</strong> {user?.id}</p>
          </div>
        </CardContent>
      </Card>

      {/* Connected Accounts Section */}
      <Card className="relative backdrop-blur-sm bg-white/70 dark:bg-gray-900/70 border border-white/20 shadow-xl animate-slideUp animation-delay-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg shadow-lg">
              <Settings className="h-4 w-4 text-white" />
            </div>
            <GradientText colors={['#059669', '#10b981', '#34d399']}>
              Connected Accounts
            </GradientText>
          </CardTitle>
          <CardDescription>
            Manage your social media and platform connections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* YouTube Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-300"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "YouTube integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">YouTube</h4>
                    <p className="text-sm text-muted-foreground">Connect your channel</p>
                  </div>
                </div>
              </div>

              {/* Instagram Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-400"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "Instagram integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">Instagram</h4>
                    <p className="text-sm text-muted-foreground">Connect your profile</p>
                  </div>
                </div>
              </div>

              {/* TikTok Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-500"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "TikTok integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-gray-800 to-black rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">TikTok</h4>
                    <p className="text-sm text-muted-foreground">Connect your account</p>
                  </div>
                </div>
              </div>

              {/* LinkedIn Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-600"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "LinkedIn integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">LinkedIn</h4>
                    <p className="text-sm text-muted-foreground">Connect your profile</p>
                  </div>
                </div>
              </div>

              {/* Twitter/X Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-700"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "Twitter/X integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-gray-800 to-black rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">Twitter/X</h4>
                    <p className="text-sm text-muted-foreground">Connect your account</p>
                  </div>
                </div>
              </div>

              {/* Facebook Connection */}
              <div 
                className="border rounded-lg p-4 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-all duration-300 cursor-pointer backdrop-blur-sm bg-white/50 dark:bg-gray-900/50 border-white/20 shadow-lg hover:shadow-xl transform hover:scale-105 animate-slideUp animation-delay-800"
                onClick={() => {
                  toast({
                    title: "Coming Soon! 🚀",
                    description: "Facebook integration is currently under development. Stay tuned for updates!",
                  })
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg flex items-center justify-center shadow-lg">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium">Facebook</h4>
                    <p className="text-sm text-muted-foreground">Connect your page</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center pt-4">
              <p className="text-sm text-muted-foreground">
                <ShinyText text="Click on any platform to connect your account" />
              </p>
            </div>
          </div>
        </CardContent>
      </Card>


      {/* Connection Summary */}
      <Card className="relative backdrop-blur-sm bg-white/70 dark:bg-gray-900/70 border border-white/20 shadow-xl animate-slideUp animation-delay-900">
        <CardHeader>
          <CardTitle>
            <GradientText colors={['#f59e0b', '#d97706', '#92400e']}>
              Connection Summary
            </GradientText>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gradient-to-r from-blue-50/70 to-blue-100/70 dark:from-blue-950/30 dark:to-blue-900/30 rounded-lg backdrop-blur-sm border border-blue-200/30">
              <div className="text-2xl font-bold text-blue-600">{accounts.filter(acc => acc.isConnected).length}</div>
              <div className="text-sm text-blue-600">Connected Accounts</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-r from-green-50/70 to-green-100/70 dark:from-green-950/30 dark:to-green-900/30 rounded-lg backdrop-blur-sm border border-green-200/30">
              <div className="text-2xl font-bold text-green-600">{accounts.length}</div>
              <div className="text-sm text-green-600">Total Platforms</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-r from-orange-50/70 to-orange-100/70 dark:from-orange-950/30 dark:to-orange-900/30 rounded-lg backdrop-blur-sm border border-orange-200/30">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round((accounts.filter(acc => acc.isConnected).length / accounts.length) * 100)}%
              </div>
              <div className="text-sm text-orange-600">Connection Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Guidance Modal for Instagram linking */}
      <Dialog open={showIgGuide} onOpenChange={setShowIgGuide}>
        <DialogContent className="backdrop-blur-sm bg-white/90 dark:bg-gray-900/90 border border-white/20">
          <DialogHeader>
            <DialogTitle>Connect Instagram Business Account</DialogTitle>
            <DialogDescription>
              {igGuideReason || "We couldn't find a linked Instagram Business account for your Facebook Page."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3 text-sm">
            <p className="font-medium">To connect Instagram:</p>
            <ol className="list-decimal ml-5 space-y-2">
              <li>Open Instagram app → Settings → Account → Switch to Professional → Business.</li>
              <li>In your Facebook Page settings, link your Instagram account to this Page.</li>
              <li>Return here and press Connect on Instagram.</li>
            </ol>
            <p className="text-muted-foreground">Also ensure permissions: instagram_basic, pages_show_list, pages_read_engagement.</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowIgGuide(false)}>Close</Button>
            <Button onClick={() => { setShowIgGuide(false); handleConnect('instagram') }} className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white border-none">Re-check now</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
