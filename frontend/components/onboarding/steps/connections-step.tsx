"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, ArrowRight, Facebook, Instagram, Twitter, Linkedin, Youtube, Mail, Loader2, Check, Plus, Save } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { initiateOAuth, getAvailablePlatforms, getPlatformConfig } from "@/lib/oauth"
import { formatPlatformName, getPlatformIcon, getPlatformColor } from "@/lib/utils"
import { YouTubeConnection } from "../youtube-connection"
import type { OnboardingData } from "../onboarding-wizard"
import { useState, useEffect } from "react"
import React from "react"

// Facebook SDK TypeScript declarations
declare global {
  interface Window {
    FB: {
      getLoginStatus: (callback: (response: any) => void) => void
      init: (params: any) => void
      login: (callback: (response: any) => void, params?: any) => void
      logout: (callback: (response: any) => void) => void
    }
  }
}

interface ConnectionsStepProps {
  data: OnboardingData
  updateData: (updates: Partial<OnboardingData>) => void
  onNext: () => void
  onPrev: () => void
  isFromSettings?: boolean
  onSave?: () => void
  currentStep?: number
}

const platforms = [
  { id: "facebook", name: "Facebook", icon: Facebook, color: "bg-blue-600" },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-600" },
]

export function ConnectionsStep({ data, updateData, onNext, onPrev, isFromSettings = false, onSave, currentStep }: ConnectionsStepProps) {
  const { toast } = useToast()
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null)
  const [facebookLoginStatus, setFacebookLoginStatus] = useState<string>('unknown')
  
  // Get available platforms from OAuth config
  const availablePlatforms = getAvailablePlatforms()

  // Facebook login status checking
  useEffect(() => {
    // Check if Facebook SDK is loaded
    if (typeof window !== 'undefined' && window.FB) {
      checkFacebookLoginStatus()
    }
  }, [])

  const checkFacebookLoginStatus = () => {
    if (typeof window !== 'undefined' && window.FB) {
      window.FB.getLoginStatus(function(response: any) {
        statusChangeCallback(response)
      })
    }
  }

  const statusChangeCallback = (response: any) => {
    console.log('Facebook login status:', response.status)
    setFacebookLoginStatus(response.status)
    
    if (response.status === 'connected') {
      // User is logged in and connected to your app
      console.log('User is logged in:', response.authResponse.userID)
      toast({
        title: "Facebook Connected",
        description: "You're already logged into Facebook!",
      })
    } else if (response.status === 'not_authorized') {
      // User is logged into Facebook but not your app
      console.log('User needs to authorize your app')
    } else {
      // User is not logged into Facebook
      console.log('User is not logged into Facebook')
    }
  }

  const checkLoginState = () => {
    if (typeof window !== 'undefined' && window.FB) {
      window.FB.getLoginStatus(function(response: any) {
        statusChangeCallback(response)
      })
    }
  }

  const connectPlatform = async (platformId: string) => {
    try {
      setConnectingPlatform(platformId)
      
      // Check if platform is already connected
      const currentConnections = data.connectedAccounts || []
      const isConnected = currentConnections.some(conn => conn.platform === platformId)
      
      if (isConnected) {
        // Disconnect platform
        const updatedConnections = currentConnections.filter(conn => conn.platform !== platformId)
        updateData({ connectedAccounts: updatedConnections })
        
        toast({
          title: "Disconnected",
          description: `${formatPlatformName(platformId)} has been disconnected.`,
        })
        return
      }

      // Initiate OAuth flow
      initiateOAuth(platformId)
      
    } catch (error) {
      console.error(`Failed to connect ${platformId}:`, error)
      toast({
        title: "Connection Failed",
        description: `Failed to connect ${formatPlatformName(platformId)}. Please try again.`,
        variant: "destructive",
      })
    } finally {
      setConnectingPlatform(null)
    }
  }

  const getConnectionStatus = (platformId: string) => {
    const currentConnections = data.connectedAccounts || []
    return currentConnections.find(conn => conn.platform === platformId)
  }

  const isConnected = (platformId: string) => {
    return !!getConnectionStatus(platformId)
  }

  const getConnectedCount = () => {
    return (data.connectedAccounts || []).length
  }

  const handleYouTubeConnectionChange = (connected: boolean) => {
    const currentConnections = data.connectedAccounts || []
    if (connected && !currentConnections.some(conn => typeof conn === 'string' ? conn === 'youtube' : conn.platform === 'youtube')) {
      updateData({ connectedAccounts: [...currentConnections, { platform: 'youtube', username: '', displayName: 'YouTube', isConnected: true, permissions: [], connectedAt: new Date() }] })
    } else if (!connected && currentConnections.some(conn => typeof conn === 'string' ? conn === 'youtube' : conn.platform === 'youtube')) {
      updateData({ connectedAccounts: currentConnections.filter((conn) => typeof conn === 'string' ? conn !== 'youtube' : conn.platform !== 'youtube') })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connect your accounts</CardTitle>
        <CardDescription>
          {isFromSettings 
            ? "Update your connected social media and advertising accounts. Changes will be saved when you click 'Save Changes'."
            : "Connect your social media and advertising accounts to enable AI-powered content creation and campaign management. You can skip this step and connect accounts later."
          }
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* YouTube Connection - Featured */}
        <div>
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-600" />
            YouTube Integration
          </h3>
          <YouTubeConnection 
            onConnectionChange={handleYouTubeConnectionChange} 
            returnContext={isFromSettings ? 'settings' : 'onboarding'}
            currentStep={currentStep}
          />
        </div>

        {/* Other Platforms */}
        <div>
          <h3 className="font-medium mb-3">Other Platforms</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {platforms.map((platform) => {
              const Icon = platform.icon
              const connection = getConnectionStatus(platform.id)
              const connected = isConnected(platform.id)
              const isConnecting = connectingPlatform === platform.id
              
              return (
                <div
                  key={platform.id}
                  className={`flex items-center justify-between p-4 border rounded-lg transition-all duration-200 ${
                    connected 
                      ? 'border-green-300 bg-green-50 dark:border-green-700 dark:bg-green-950/20' 
                      : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${platform.color}`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-medium">{platform.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {connected ? "Connected" : "Not Connected"}
                        </p>
                      </div>
                    </div>
                    
                    {platform.id === 'facebook' ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          if (typeof window !== 'undefined' && window.FB) {
                            window.FB.login(function(response: any) {
                              checkLoginState()
                            }, {
                              scope: 'pages_read_engagement,pages_show_list,pages_manage_metadata,pages_read_user_content,instagram_basic,instagram_content_publish'
                            })
                          }
                        }}
                        className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 ml-auto"
                      >
                        Connect
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => connectPlatform(platform.id)}
                        disabled={isConnecting}
                      >
                        {isConnecting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Connecting...
                          </>
                        ) : connected ? (
                          "Disconnect"
                        ) : (
                          "Connect"
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {getConnectedCount() > 0 && (
          <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
            <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">
              Great! You've connected {getConnectedCount()} account{getConnectedCount() !== 1 ? 's' : ''}:
            </h4>
            <div className="flex flex-wrap gap-2">
              {(data.connectedAccounts || []).map((connection, index) => {
                const platform = typeof connection === 'string' 
                  ? platforms.find((p) => p.id === connection)
                  : platforms.find((p) => p.id === connection.platform)
                const platformName = typeof connection === 'string' 
                  ? (connection === "youtube" ? "YouTube" : connection)
                  : formatPlatformName(connection.platform)
                return (
                  <Badge key={typeof connection === 'string' ? connection : connection.platform || index} variant="secondary">
                    {platform?.icon && React.createElement(platform.icon, { className: "h-3 w-3 mr-1" })} {platformName}
                    {typeof connection === 'object' && connection.username && ` (@${connection.username})`}
                  </Badge>
                )
              })}
            </div>
          </div>
        )}

        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
          <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
            What happens when you connect?
          </h4>
          <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
            <li>• We'll securely authenticate with each platform</li>
            <li>• You'll grant permission to access your data</li>
            <li>• We'll start monitoring your performance metrics</li>
            <li>• You can revoke access at any time</li>
          </ul>
        </div>

        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          {isFromSettings && onSave ? (
            <Button onClick={onSave}>
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </Button>
          ) : (
            <Button onClick={onNext}>
              {getConnectedCount() > 0 ? "Continue" : "Skip for now"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
