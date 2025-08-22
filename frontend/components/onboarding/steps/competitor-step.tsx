"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Plus, X, Search, Globe, Facebook, Instagram, Youtube } from "lucide-react"
import type { OnboardingData } from "../onboarding-wizard"

interface CompetitorStepProps {
  data: OnboardingData
  updateData: (updates: Partial<OnboardingData>) => void
  onNext: () => void
  onPrev: () => void
  isFromSettings?: boolean
}

const platformIcons = {
  facebook: Facebook,
  instagram: Instagram,
  youtube: Youtube,
}

const platformOptions = [
  { id: "facebook", name: "Facebook", icon: Facebook },
  { id: "instagram", name: "Instagram", icon: Instagram },
  { id: "youtube", name: "YouTube", icon: Youtube },
]

export function CompetitorStep({ data, updateData, onNext, onPrev, isFromSettings = false }: CompetitorStepProps) {
  const [newCompetitor, setNewCompetitor] = useState({
    name: "",
    website: "",
    description: "",
    platforms: [] as string[],
  })

  const addCompetitor = () => {
    if (newCompetitor.name && newCompetitor.website) {
      updateData({
        competitors: [...data.competitors, { ...newCompetitor }],
      })
      setNewCompetitor({ name: "", website: "", description: "", platforms: [] })
    }
  }

  const removeCompetitor = (index: number) => {
    const updatedCompetitors = data.competitors.filter((_, i) => i !== index)
    updateData({ competitors: updatedCompetitors })
  }

  const togglePlatform = (platform: string) => {
    const updatedPlatforms = newCompetitor.platforms.includes(platform)
      ? newCompetitor.platforms.filter((p) => p !== platform)
      : [...newCompetitor.platforms, platform]

    setNewCompetitor({ ...newCompetitor, platforms: updatedPlatforms })
  }

  const canProceed = data.competitors.length >= 1

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Competitor Intelligence
        </CardTitle>
        <CardDescription>
          Tell us about your main competitors so our AI can analyze their strategies and find opportunities for you.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Add New Competitor */}
        <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
          <h3 className="font-medium">Add Competitor</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="competitor-name">Company Name</Label>
              <Input
                id="competitor-name"
                placeholder="e.g., Nike, Apple, Starbucks"
                value={newCompetitor.name}
                onChange={(e) => setNewCompetitor({ ...newCompetitor, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="competitor-website">Website</Label>
              <Input
                id="competitor-website"
                placeholder="https://competitor.com"
                value={newCompetitor.website}
                onChange={(e) => setNewCompetitor({ ...newCompetitor, website: e.target.value })}
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="competitor-description">Description (Optional)</Label>
            <Input
              id="competitor-description"
              placeholder="Brief description of this competitor..."
              value={newCompetitor.description}
              onChange={(e) => setNewCompetitor({ ...newCompetitor, description: e.target.value })}
            />
          </div>

          <div>
            <Label>Platforms they're active on</Label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-2">
              {platformOptions.map((platform) => {
                const Icon = platform.icon
                return (
                  <div key={platform.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={platform.id}
                      checked={newCompetitor.platforms.includes(platform.id)}
                      onCheckedChange={() => togglePlatform(platform.id)}
                    />
                    <Label htmlFor={platform.id} className="flex items-center gap-2 cursor-pointer">
                      <Icon className="h-4 w-4" />
                      {platform.name}
                    </Label>
                  </div>
                )
              })}
            </div>
          </div>

          <Button onClick={addCompetitor} className="w-full" disabled={!newCompetitor.name || !newCompetitor.website}>
            <Plus className="h-4 w-4 mr-2" />
            Add Competitor
          </Button>
        </div>

        {/* Competitor List */}
        {data.competitors.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-medium">Your Competitors ({data.competitors.length})</h3>
            {data.competitors.map((competitor, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{competitor.name}</h4>
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">{competitor.website}</span>
                  </div>
                  {competitor.description && (
                    <p className="text-sm text-muted-foreground mb-2">{competitor.description}</p>
                  )}
                  <div className="flex gap-1 flex-wrap">
                    {competitor.platforms.map((platform) => {
                      const Icon = platformIcons[platform as keyof typeof platformIcons]
                      return (
                        <Badge key={platform} variant="secondary" className="text-xs">
                          {Icon && <Icon className="h-3 w-3 mr-1" />}
                          {platform}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeCompetitor(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}

        {/* AI Analysis Preview */}
        {data.competitors.length > 0 && (
          <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <Search className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-blue-900 dark:text-blue-100">AI Analysis Preview</span>
            </div>
            <p className="text-sm text-blue-700 dark:text-blue-300">
              Our AI will analyze {data.competitors.length} competitor{data.competitors.length > 1 ? "s" : ""} across{" "}
              {Array.from(new Set(data.competitors.flatMap((c) => c.platforms))).length} platform
              {Array.from(new Set(data.competitors.flatMap((c) => c.platforms))).length > 1 ? "s" : ""} to identify:
            </p>
            <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1">
              <li>• Content gaps and opportunities</li>
              <li>• Posting frequency and timing patterns</li>
              <li>• Engagement strategies that work</li>
              <li>• Trending topics in your industry</li>
            </ul>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={onPrev}>
            Previous
          </Button>
          {!isFromSettings && (
            <Button onClick={onNext} disabled={!canProceed}>
              {canProceed ? "Start AI Analysis" : "Add at least 1 competitor"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
