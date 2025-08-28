"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, Target, Users, Calendar } from "lucide-react"

interface CompetitorGap {
  id: number
  title: string
  description: string
  opportunity: string
  confidence: number
  difficulty: 'Easy' | 'Medium' | 'Hard'
  impact: 'Low' | 'Medium' | 'High'
  timeframe: string
}

const mockGaps: CompetitorGap[] = [
  {
    id: 1,
    title: "Educational Video Content",
    description: "Competitors are not creating enough how-to and tutorial content",
    opportunity: "Create weekly educational videos to establish thought leadership",
    confidence: 89,
    difficulty: 'Medium',
    impact: 'High',
    timeframe: '2-4 weeks'
  },
  {
    id: 2,
    title: "Customer Success Stories",
    description: "Limited case studies and testimonials in competitor content",
    opportunity: "Develop detailed customer success story campaigns",
    confidence: 95,
    difficulty: 'Easy',
    impact: 'High',
    timeframe: '1-2 weeks'
  },
  {
    id: 3,
    title: "Interactive Content",
    description: "Competitors lack polls, quizzes, and interactive posts",
    opportunity: "Create engaging interactive content to boost engagement",
    confidence: 76,
    difficulty: 'Medium',
    impact: 'Medium',
    timeframe: '1-3 weeks'
  }
]

interface CompetitorGapSuggestionsProps {
  selectedDate?: Date
}

export function CompetitorGapSuggestions({ selectedDate }: CompetitorGapSuggestionsProps) {
  const [gaps] = useState<CompetitorGap[]>(mockGaps)

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High': return 'bg-purple-100 text-purple-800'
      case 'Medium': return 'bg-blue-100 text-blue-800'
      case 'Low': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Card className="w-full max-w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Target className="h-4 w-4 text-orange-600" />
          Competitor Gap Opportunities
        </CardTitle>
        <CardDescription className="text-xs">
          Identified content gaps where competitors are underperforming
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        {gaps.map((gap) => (
          <div key={gap.id} className="border rounded-lg p-3 space-y-2 overflow-hidden">
            <div className="flex items-start justify-between gap-2">
              <h4 className="font-medium text-sm break-words leading-tight flex-1 min-w-0">{gap.title}</h4>
              <Badge variant="outline" className="text-xs flex-shrink-0 px-1 py-0">
                {gap.confidence}%
              </Badge>
            </div>
            
            <p className="text-xs text-muted-foreground break-words leading-relaxed">
              {gap.description}
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-950/20 p-2 rounded text-xs">
              <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">
                💡 Opportunity
              </p>
              <p className="text-blue-700 dark:text-blue-300 break-words leading-relaxed">
                {gap.opportunity}
              </p>
            </div>
            
            <div className="flex items-center justify-between gap-2">
              <div className="flex gap-1 flex-wrap">
                <Badge className={`${getDifficultyColor(gap.difficulty)} text-xs px-1 py-0`}>
                  {gap.difficulty}
                </Badge>
                <Badge className={`${getImpactColor(gap.impact)} text-xs px-1 py-0`}>
                  {gap.impact}
                </Badge>
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground flex-shrink-0">
                <Calendar className="h-3 w-3" />
                <span className="truncate">{gap.timeframe}</span>
              </div>
            </div>
            
            <Button size="sm" className="w-full text-xs px-2 py-1 h-7">
              <TrendingUp className="h-3 w-3 mr-1" />
              Implement Strategy
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
