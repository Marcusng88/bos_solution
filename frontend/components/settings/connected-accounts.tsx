"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
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
          console.log('FB.login response:', response);
          if (response.status === 'connected') {
            // Send token to backend to persist connection
            const apiBase = process.env.NEXT_PUBLIC_API_URL
            const userId = user?.id
            const accessToken = response.authResponse?.accessToken
            console.log('Extracted data:', { apiBase, userId, accessTokenPresent: !!accessToken });
            
            if (!apiBase || !userId || !accessToken) {
              console.error('Missing required data:', { apiBase: !!apiBase, userId: !!userId, accessToken: !!accessToken });
              toast({
                title: "Missing config",
                description: "Unable to persist connection. Please try again.",
                variant: "destructive",
              })
              return
            }
            
            console.log('Sending request to backend...');
            fetch(`${apiBase}/social-media/connect/facebook`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId,
              },
              body: JSON.stringify({ access_token: accessToken }),
            }).then(async (r) => {
              if (!r.ok) {
                const err = await r.json().catch(() => ({}))
                throw new Error(err?.detail || 'Failed to save connection')
              }
              const result = await r.json().catch(() => ({}))

              // Refresh accounts from database to get the real connection status
              const response = await fetch(`${apiBase}/social-media/connected-accounts`, {
                headers: {
                  'X-User-ID': userId,
                },
              })
              
              if (response.ok) {
                const dbAccounts = (await response.json()).accounts || []
                setAccounts(prev => prev.map(account => {
                  const dbAccount = dbAccounts.find((db: any) => db.platform === account.platform)
                  if (dbAccount) {
                    return {
                      ...account,
                      isConnected: true,
                      username: dbAccount.username || dbAccount.account_name || "",
                      displayName: dbAccount.account_name || account.displayName,
                      lastSync: 'Just now',
                      permissions: Object.keys(dbAccount.permissions || {})
                    }
                  }
                  return account
                }))
              }
              
              const fbConnected = !!result?.facebook?.connected
              const igConnected = !!result?.instagram?.connected

              if (fbConnected && igConnected) {
                toast({
                  title: "Connected!",
                  description: "Facebook and Instagram connected successfully!",
                })
              } else if (fbConnected && !igConnected) {
                toast({
                  title: "Facebook connected",
                  description: "Instagram is not connected. We'll guide you to link your Instagram Business account to your Page.",
                })
                setIgGuideReason(result?.instagram?.reason || "No Instagram business account linked")
                setShowIgGuide(true)
              } else {
                toast({
                  title: "Connection updated",
                  description: "Connection status refreshed.",
                })
              }
            }).catch(() => {
              toast({
                title: "Persist failed",
                description: "Connected on Facebook, but saving failed.",
                variant: "destructive",
              })
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
    } else if (platform === 'instagram') {
      // Trigger Instagram connection via backend (uses env/default token or provided token)
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL
        const userId = user?.id
        if (!apiBase || !userId) {
          toast({
            title: "Missing config",
            description: "Unable to start Instagram connect.",
            variant: "destructive",
          })
          return
        }

        const r = await fetch(`${apiBase}/social-media/connect/instagram`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-ID': userId,
          },
          body: JSON.stringify({})
        })

        if (!r.ok) {
          const err = await r.json().catch(() => ({}))
          throw new Error(err?.detail || 'Failed to connect Instagram')
        }

        const result = await r.json().catch(() => ({}))

        // Refresh and reflect
        const resp = await fetch(`${apiBase}/social-media/connected-accounts`, {
          headers: {
            'X-User-ID': userId,
          },
        })
        if (resp.ok) {
          const dbAccounts = (await resp.json()).accounts || []
          setAccounts(prev => prev.map(account => {
            const dbAccount = dbAccounts.find((db: any) => db.platform === account.platform)
            if (dbAccount) {
              return {
                ...account,
                isConnected: true,
                username: dbAccount.username || dbAccount.account_name || "",
                displayName: dbAccount.account_name || account.displayName,
                lastSync: 'Just now',
                permissions: Object.keys(dbAccount.permissions || {})
              }
            }
            return account
          }))
        }

        const igConnected = !!result?.instagram?.connected
        const fbConnected = !!result?.facebook?.connected
        if (igConnected && fbConnected) {
          toast({ title: "Connected!", description: "Instagram and Facebook connected successfully!" })
        } else if (igConnected && !fbConnected) {
          toast({ title: "Instagram connected", description: "Facebook is not connected." })
        } else {
          toast({ title: "Connection updated", description: "Connection status refreshed." })
        }

      } catch (e) {
        toast({ title: "Error", description: "Instagram connect failed.", variant: "destructive" })
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
      {/* Guidance Modal for Instagram linking */}
      <Dialog open={showIgGuide} onOpenChange={setShowIgGuide}>
        <DialogContent>
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
            <Button onClick={() => { setShowIgGuide(false); handleConnect('instagram') }}>Re-check now</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
