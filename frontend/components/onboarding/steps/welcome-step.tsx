"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, Target, BarChart3, Zap } from "lucide-react"

interface WelcomeStepProps {
  onNext: () => void
}

export function WelcomeStep({ onNext }: WelcomeStepProps) {
  return (
    <Card>
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Welcome to Bos Solution!</CardTitle>
        <CardDescription>
          Let's personalize your experience and set up your AI-powered marketing workspace in just a few steps.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start gap-3 p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20">
            <Sparkles className="h-6 w-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-semibold">AI Content Generation</h3>
              <p className="text-sm text-muted-foreground">Create compelling posts and campaigns automatically</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-950/20">
            <Target className="h-6 w-6 text-green-600 mt-1" />
            <div>
              <h3 className="font-semibold">Smart Targeting</h3>
              <p className="text-sm text-muted-foreground">Reach the right audience with AI-powered insights</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 rounded-lg bg-purple-50 dark:bg-purple-950/20">
            <BarChart3 className="h-6 w-6 text-purple-600 mt-1" />
            <div>
              <h3 className="font-semibold">Advanced Analytics</h3>
              <p className="text-sm text-muted-foreground">Track performance and optimize campaigns in real-time</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-4 rounded-lg bg-orange-50 dark:bg-orange-950/20">
            <Zap className="h-6 w-6 text-orange-600 mt-1" />
            <div>
              <h3 className="font-semibold">Automation</h3>
              <p className="text-sm text-muted-foreground">Schedule and optimize your marketing on autopilot</p>
            </div>
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-6">This setup will take about 3-5 minutes to complete.</p>
          <Button onClick={onNext} size="lg" className="px-8">
            Get Started
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
