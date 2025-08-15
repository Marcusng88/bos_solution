"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, ArrowRight, Facebook, Instagram, Twitter, Linkedin, Youtube, Mail } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { YouTubeConnection } from "../youtube-connection"
import type { OnboardingData } from "../onboarding-wizard"

interface ConnectionsStepProps {
  data: OnboardingData
  updateData: (updates: Partial<OnboardingData>) => void
  onNext: () => void
  onPrev: () => void
}

const platforms = [
  { id: "facebook", name: "Facebook", icon: Facebook, color: "bg-blue-600" },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "bg-pink-600" },
  { id: "twitter", name: "Twitter/X", icon: Twitter, color: "bg-black" },
  { id: "linkedin", name: "LinkedIn", icon: Linkedin, color: "bg-blue-700" },
  { id: "google-ads", name: "Google Ads", icon: Mail, color: "bg-green-600" },
]

export function ConnectionsStep({ data, updateData, onNext, onPrev }: ConnectionsStepProps) {
  const { toast } = useToast()

  const connectPlatform = (platformId: string) => {
    const currentConnections = data.connectedAccounts || []
    if (currentConnections.includes(platformId)) {
      // Disconnect
      updateData({ connectedAccounts: currentConnections.filter((id) => id !== platformId) })
      toast({
        title: "Disconnected",
        description: `${platforms.find((p) => p.id === platformId)?.name} has been disconnected.`,
      })
    } else {
      // Connect
      updateData({ connectedAccounts: [...currentConnections, platformId] })
      toast({
        title: "Connected!",
        description: `${platforms.find((p) => p.id === platformId)?.name} has been connected successfully.`,
      })
    }
  }

  const handleYouTubeConnectionChange = (connected: boolean) => {
    const currentConnections = data.connectedAccounts || []
    if (connected && !currentConnections.includes("youtube")) {
      updateData({ connectedAccounts: [...currentConnections, "youtube"] })
    } else if (!connected && currentConnections.includes("youtube")) {
      updateData({ connectedAccounts: currentConnections.filter((id) => id !== "youtube") })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connect your accounts</CardTitle>
        <CardDescription>
          Connect your social media and advertising accounts to enable AI-powered content creation and campaign
          management. You can skip this step and connect accounts later.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* YouTube Connection - Featured */}
        <div>
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <Youtube className="h-5 w-5 text-red-600" />
            YouTube Integration
          </h3>
          <YouTubeConnection onConnectionChange={handleYouTubeConnectionChange} />
        </div>

        {/* Other Platforms */}
        <div>
          <h3 className="font-medium mb-3">Other Platforms</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {platforms.map((platform) => {
              const Icon = platform.icon
              const isConnected = data.connectedAccounts.includes(platform.id)
              return (
                <div
                  key={platform.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${platform.color}`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium">{platform.name}</h3>
                      <p className="text-sm text-muted-foreground">{isConnected ? "Connected" : "Coming soon"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isConnected && <Badge variant="secondary">Connected</Badge>}
                    <Button
                      variant="outline"
                      size="sm"
                      disabled
                      className="opacity-50"
                    >
                      Coming Soon
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {data.connectedAccounts.length > 0 && (
          <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
            <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">Great! You've connected:</h4>
            <div className="flex flex-wrap gap-2">
              {data.connectedAccounts.map((accountId) => {
                const platform = platforms.find((p) => p.id === accountId)
                const platformName = platform?.name || (accountId === "youtube" ? "YouTube" : accountId)
                return (
                  <Badge key={accountId} variant="secondary">
                    {platformName}
                  </Badge>
                )
              })}
            </div>
          </div>
        )}

        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button onClick={onNext}>
            {data.connectedAccounts.length > 0 ? "Continue" : "Skip for now"}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
