"use client"

import { useState } from "react"
import { Calendar } from "@/components/ui/calendar"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Facebook, Instagram, Twitter, Linkedin, Clock, Eye } from "lucide-react"

interface ContentCalendarProps {
  selectedDate: Date
  onDateSelect: (date: Date) => void
}

const scheduledPosts = [
  {
    id: 1,
    title: "Summer Sale Announcement",
    platform: "instagram",
    time: "10:00 AM",
    status: "scheduled",
    engagement: "High",
  },
  {
    id: 2,
    title: "Product Feature Highlight",
    platform: "facebook",
    time: "2:00 PM",
    status: "scheduled",
    engagement: "Medium",
  },
  {
    id: 3,
    title: "Industry Insights Article",
    platform: "linkedin",
    time: "4:00 PM",
    status: "draft",
    engagement: "High",
  },
]

const platformIcons = {
  facebook: Facebook,
  instagram: Instagram,
  twitter: Twitter,
  linkedin: Linkedin,
}

const platformColors = {
  facebook: "bg-blue-600",
  instagram: "bg-pink-600",
  twitter: "bg-black",
  linkedin: "bg-blue-700",
}

export function ContentCalendar({ selectedDate, onDateSelect }: ContentCalendarProps) {
  const [view, setView] = useState<"calendar" | "list">("calendar")

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  return (
    <div className="space-y-4">
      <Tabs value={view} onValueChange={(value) => setView(value as "calendar" | "list")}>
        <TabsList>
          <TabsTrigger value="calendar">Calendar View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && onDateSelect(date)}
                className="rounded-md border"
              />
            </div>
            <div>
              <h3 className="font-semibold mb-3">{formatDate(selectedDate)}</h3>
              <div className="space-y-2">
                {scheduledPosts.map((post) => {
                  const Icon = platformIcons[post.platform as keyof typeof platformIcons]
                  const colorClass = platformColors[post.platform as keyof typeof platformColors]
                  return (
                    <Card key={post.id} className="p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`p-1.5 rounded ${colorClass}`}>
                            <Icon className="h-3 w-3 text-white" />
                          </div>
                          <div>
                            <p className="text-sm font-medium">{post.title}</p>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              {post.time}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={post.status === "scheduled" ? "default" : "secondary"} className="text-xs">
                            {post.status}
                          </Badge>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  )
                })}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="list" className="space-y-2">
          {scheduledPosts.map((post) => {
            const Icon = platformIcons[post.platform as keyof typeof platformIcons]
            const colorClass = platformColors[post.platform as keyof typeof platformColors]
            return (
              <Card key={post.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-lg ${colorClass}`}>
                      <Icon className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <h4 className="font-medium">{post.title}</h4>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {post.time}
                        </span>
                        <span>Expected: {post.engagement} engagement</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={post.status === "scheduled" ? "default" : "secondary"}>{post.status}</Badge>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
        </TabsContent>
      </Tabs>
    </div>
  )
}
