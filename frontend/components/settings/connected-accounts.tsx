"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Facebook, Instagram, Twitter, Linkedin, Youtube, Mail, Settings, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useUser } from "@clerk/nextjs"

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

  // Get real user data and check actual connections
  useEffect(() => {
    if (!user) return

    const checkRealConnections = async () => {
      const realAccounts: ConnectedAccount[] = [
        {
          platform: "facebook",
          username: user.primaryEmailAddress?.emailAddress || "",
          displayName: user.fullName || user.firstName || "User",
          isConnected: false, // We'll check this with Facebook SDK
          lastSync: "",
          permissions: []
        },
        {
          platform: "twitter",
          username: "",
          displayName: "Twitter",
          isConnected: false,
          permissions: []
        },
        {
          platform: "linkedin",
          username: "",
          displayName: "LinkedIn",
          isConnected: false,
          permissions: []
        },
        {
          platform: "youtube",
          username: "",
          displayName: "YouTube",
          isConnected: false,
          permissions: []
        }
      ]

      // Check Facebook connection status using Facebook SDK
      if (typeof window !== 'undefined' && window.FB) {
        try {
          window.FB.getLoginStatus(function(response: any) {
            if (response.status === 'connected') {
              setAccounts(prev => prev.map(acc => 
                acc.platform === 'facebook' || acc.platform === 'instagram'
                  ? { ...acc, isConnected: true, lastSync: 'Just now' }
                  : acc
              ))
            }
          })
        } catch (error) {
          console.log('Facebook SDK not ready yet')
        }
      }

      setAccounts(realAccounts)
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
        return "FB/Ins"
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
      // Check real Facebook connection status
      if (platform === 'facebook' && typeof window !== 'undefined' && window.FB) {
        window.FB.getLoginStatus(function(response: any) {
          if (response.status === 'connected') {
            setAccounts(prev => prev.map(acc => 
              acc.platform === 'facebook' || acc.platform === 'instagram'
                ? { ...acc, isConnected: true, lastSync: 'Just now' }
                : acc
            ))
            toast({
              title: "Refreshed",
              description: `${getPlatformName(platform)} connection refreshed successfully.`,
            })
          } else {
            setAccounts(prev => prev.map(acc => 
              acc.platform === 'facebook' || acc.platform === 'instagram'
                ? { ...acc, isConnected: false, lastSync: '' }
                : acc
            ))
            toast({
              title: "Not Connected",
              description: `${getPlatformName(platform)} is not currently connected.`,
            })
          }
        })
      } else {
        // Simulate API call for other platforms
        await new Promise(resolve => setTimeout(resolve, 1000))
        toast({
          title: "Refreshed",
          description: `${getPlatformName(platform)} connection refreshed successfully.`,
        })
      }
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
      if (platform === 'facebook' && typeof window !== 'undefined' && window.FB) {
        // Actually disconnect from Facebook
        window.FB.logout(function(response: any) {
          setAccounts(prev => prev.map(acc => 
            acc.platform === 'facebook' || acc.platform === 'instagram'
              ? { ...acc, isConnected: false, username: "", displayName: "", permissions: [] }
              : acc
          ))
          toast({
            title: "Disconnected",
            description: `${getPlatformName(platform)} has been disconnected.`,
          })
        })
      } else {
        // Simulate API call for other platforms
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
      }
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to disconnect ${getPlatformName(platform)}.`,
        variant: "destructive",
      })
    }
  }

  const handleConnect = async (platform: string) => {
    if (platform === 'facebook') {
      // Trigger Facebook OAuth flow
      if (typeof window !== 'undefined' && window.FB) {
        window.FB.login(function(response: any) {
          if (response.status === 'connected') {
            // Successfully connected
            setAccounts(prev => prev.map(acc => 
              acc.platform === 'facebook' || acc.platform === 'instagram'
                ? { ...acc, isConnected: true, lastSync: 'Just now' }
                : acc
            ))
            toast({
              title: "Connected!",
              description: "Facebook & Instagram connected successfully!",
            })
          } else if (response.status === 'not_authorized') {
            toast({
              title: "Not Authorized",
              description: "Facebook login was cancelled or not authorized.",
              variant: "destructive",
            })
          } else {
            toast({
              title: "Login Failed",
              description: "Facebook login failed. Please try again.",
              variant: "destructive",
            })
          }
        }, {
          scope: 'pages_read_engagement,pages_show_list,instagram_basic'
        })
      } else {
        toast({
          title: "Facebook SDK Not Ready",
          description: "Please wait for Facebook SDK to load and try again.",
          variant: "destructive",
        })
      }
    } else {
      // For other platforms, show a message
      toast({
        title: "Coming Soon",
        description: `${getPlatformName(platform)} integration is not yet implemented.`,
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Manage your account and connected services</p>
        </div>
        <Button variant="outline" size="sm">
          <Settings className="mr-2 h-4 w-4" />
          Account Settings
        </Button>
      </div>

      {/* User Info */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress}</p>
            <p><strong>Name:</strong> {user?.fullName || `${user?.firstName} ${user?.lastName}`}</p>
            <p><strong>User ID:</strong> {user?.id}</p>
          </div>
        </CardContent>
      </Card>

      {/* Connected Accounts */}
      <Card>
        <CardHeader>
          <CardTitle>Connected Accounts</CardTitle>
          <CardDescription>
            Manage your social media and advertising platform connections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {accounts.map((account) => {
            const Icon = getPlatformIcon(account.platform)
            
            return (
              <div
                key={account.platform}
                className={`flex items-center justify-between p-4 border rounded-lg transition-all duration-200 ${
                  account.isConnected 
                    ? 'border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950/20' 
                    : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getPlatformColor(account.platform)}`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium">{getPlatformName(account.platform)}</h3>
                    <p className="text-sm text-muted-foreground">
                      {account.isConnected ? "Connected" : "Not connected"}
                    </p>
                    {account.isConnected && account.username && (
                      <p className="text-xs text-green-600 dark:text-green-400">
                        {account.username}
                      </p>
                    )}
                    {account.isConnected && account.lastSync && (
                      <p className="text-xs text-blue-600 dark:text-blue-400">
                        Last sync: {account.lastSync}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {account.isConnected && (
                    <>
                      <Badge variant="secondary">Connected</Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRefresh(account.platform)}
                        disabled={isLoading}
                      >
                        <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDisconnect(account.platform)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Disconnect
                      </Button>
                    </>
                  )}
                  {!account.isConnected && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleConnect(account.platform)}
                    >
                      Connect
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      {/* Connection Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Connection Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{accounts.filter(acc => acc.isConnected).length}</div>
              <div className="text-sm text-blue-600">Connected Accounts</div>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{accounts.length}</div>
              <div className="text-sm text-green-600">Total Platforms</div>
            </div>
            <div className="text-center p-4 bg-orange-50 dark:bg-orange-950/20 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round((accounts.filter(acc => acc.isConnected).length / accounts.length) * 100)}%
              </div>
              <div className="text-sm text-orange-600">Connection Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
