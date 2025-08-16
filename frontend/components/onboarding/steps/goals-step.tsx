"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, ArrowRight, Target, Users, DollarSign, TrendingUp, Heart, Megaphone } from "lucide-react"
import type { OnboardingData } from "../onboarding-wizard"

interface GoalsStepProps {
  data: OnboardingData
  updateData: (updates: Partial<OnboardingData>) => void
  onNext: () => void
  onPrev: () => void
  isFromSettings?: boolean
}

const marketingGoals = [
  { id: "brand-awareness", label: "Increase brand awareness", icon: Megaphone },
  { id: "lead-generation", label: "Generate more leads", icon: Target },
  { id: "customer-acquisition", label: "Acquire new customers", icon: Users },
  { id: "sales-growth", label: "Boost sales and revenue", icon: DollarSign },
  { id: "engagement", label: "Improve social media engagement", icon: Heart },
  { id: "website-traffic", label: "Drive more website traffic", icon: TrendingUp },
]

export function GoalsStep({ data, updateData, onNext, onPrev, isFromSettings = false }: GoalsStepProps) {
  const toggleGoal = (goalId: string) => {
    const currentGoals = data.goals || []
    const updatedGoals = currentGoals.includes(goalId)
      ? currentGoals.filter((id) => id !== goalId)
      : [...currentGoals, goalId]
    updateData({ goals: updatedGoals })
  }

  const canProceed = data.goals.length > 0 && data.budget

  return (
    <Card>
      <CardHeader>
        <CardTitle>What are your marketing goals?</CardTitle>
        <CardDescription>
          Select all that apply. This helps us prioritize AI recommendations for your campaigns.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3">
          <Label className="text-base font-medium">Primary marketing objectives</Label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {marketingGoals.map((goal) => {
              const Icon = goal.icon
              const isSelected = data.goals.includes(goal.id)
              return (
                <div
                  key={goal.id}
                  className={`flex items-center space-x-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                    isSelected
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-950/20"
                      : "border-gray-200 hover:border-gray-300 dark:border-gray-700"
                  }`}
                  onClick={() => toggleGoal(goal.id)}
                >
                  <Checkbox checked={isSelected} onChange={() => toggleGoal(goal.id)} />
                  <Icon className={`h-5 w-5 ${isSelected ? "text-blue-600" : "text-gray-500"}`} />
                  <Label className="cursor-pointer flex-1">{goal.label}</Label>
                </div>
              )
            })}
          </div>
        </div>

        <div className="space-y-3">
          <Label className="text-base font-medium">What's your monthly marketing budget?</Label>
          <Select value={data.budget} onValueChange={(value) => updateData({ budget: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select your budget range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="under-500">Under $500</SelectItem>
              <SelectItem value="500-1000">$500 - $1,000</SelectItem>
              <SelectItem value="1000-5000">$1,000 - $5,000</SelectItem>
              <SelectItem value="5000-10000">$5,000 - $10,000</SelectItem>
              <SelectItem value="10000-25000">$10,000 - $25,000</SelectItem>
              <SelectItem value="over-25000">Over $25,000</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={onPrev}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button onClick={onNext} disabled={!canProceed}>
            {isFromSettings ? "Next: Competitors" : "Next"}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
