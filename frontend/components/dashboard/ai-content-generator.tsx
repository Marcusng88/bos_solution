/**
 * AI Content Generation Modal Component
 * Modal for creating AI-generated content using the content planning API
 */

"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Sparkles, Copy, CheckCircle } from "lucide-react"
import { useContentPlanning } from "@/hooks/use-content-planning"
import type { ContentGenerationRequest } from "@/lib/content-planning-api"

interface AIContentGeneratorProps {
  trigger?: React.ReactNode
}

export function AIContentGenerator({ trigger }: AIContentGeneratorProps) {
  const [open, setOpen] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<any>(null)
  const [copied, setCopied] = useState(false)
  
  const { generateContent, supportedOptions } = useContentPlanning({ autoLoad: true })

  // Form state
  const [formData, setFormData] = useState<ContentGenerationRequest>({
    platform: 'instagram',
    content_type: 'promotional',
    industry: 'technology',
    target_audience: 'professionals',
    tone: 'professional'
  })
  
  const [topic, setTopic] = useState('')

  const handleGenerate = async () => {
    if (!topic.trim()) return

    try {
      setGenerating(true)
      const requestData = {
        ...formData,
        custom_requirements: `Topic: ${topic}. ${formData.custom_requirements || ''}`
      }
      const response = await generateContent(requestData)
      setGeneratedContent(response.content)
    } catch (error) {
      console.error('Failed to generate content:', error)
    } finally {
      setGenerating(false)
    }
  }

  const handleCopy = async () => {
    if (!generatedContent) return
    
    try {
      await navigator.clipboard.writeText(generatedContent.post_content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }

  const resetForm = () => {
    setGeneratedContent(null)
    setTopic('')
    setFormData({
      platform: 'instagram',
      content_type: 'promotional',
      industry: 'technology',
      target_audience: 'professionals',
      tone: 'professional'
    })
  }

  return (
    <Dialog open={open} onOpenChange={(newOpen) => {
      setOpen(newOpen)
      if (!newOpen) {
        resetForm()
      }
    }}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Sparkles className="mr-2 h-4 w-4" />
            Generate AI Content
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            AI Content Generator
          </DialogTitle>
          <DialogDescription>
            Create engaging social media content with AI assistance
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!generatedContent ? (
            // Generation Form
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="platform">Platform</Label>
                <Select 
                  value={formData.platform} 
                  onValueChange={(value) => setFormData({...formData, platform: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedOptions?.platforms.map((platform) => (
                      <SelectItem key={platform} value={platform}>
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                      </SelectItem>
                    )) || [
                      <SelectItem key="instagram" value="instagram">Instagram</SelectItem>,
                      <SelectItem key="twitter" value="twitter">Twitter</SelectItem>,
                      <SelectItem key="linkedin" value="linkedin">LinkedIn</SelectItem>,
                      <SelectItem key="facebook" value="facebook">Facebook</SelectItem>
                    ]}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="content_type">Content Type</Label>
                <Select 
                  value={formData.content_type} 
                  onValueChange={(value) => setFormData({...formData, content_type: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="promotional">Promotional</SelectItem>
                    <SelectItem value="educational">Educational</SelectItem>
                    <SelectItem value="entertaining">Entertaining</SelectItem>
                    <SelectItem value="news">News/Updates</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                <Select 
                  value={formData.industry} 
                  onValueChange={(value) => setFormData({...formData, industry: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {supportedOptions?.industries.map((industry) => (
                      <SelectItem key={industry} value={industry}>
                        {industry.charAt(0).toUpperCase() + industry.slice(1)}
                      </SelectItem>
                    )) || [
                      <SelectItem key="technology" value="technology">Technology</SelectItem>,
                      <SelectItem key="fashion" value="fashion">Fashion</SelectItem>,
                      <SelectItem key="food" value="food">Food & Beverage</SelectItem>,
                      <SelectItem key="fitness" value="fitness">Fitness</SelectItem>
                    ]}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tone">Tone</Label>
                <Select 
                  value={formData.tone} 
                  onValueChange={(value) => setFormData({...formData, tone: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">Professional</SelectItem>
                    <SelectItem value="casual">Casual</SelectItem>
                    <SelectItem value="humorous">Humorous</SelectItem>
                    <SelectItem value="inspirational">Inspirational</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="md:col-span-2 space-y-2">
                <Label htmlFor="topic">Topic *</Label>
                <Input
                  id="topic"
                  placeholder="Enter your content topic or theme..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>

              <div className="md:col-span-2 space-y-2">
                <Label htmlFor="requirements">Specific Requirements</Label>
                <Textarea
                  id="requirements"
                  placeholder="Any specific requirements, key points to include, or style preferences..."
                  rows={3}
                  value={formData.custom_requirements || ''}
                  onChange={(e) => setFormData({...formData, custom_requirements: e.target.value})}
                />
              </div>
            </div>
          ) : (
            // Generated Content Display
            <div className="space-y-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold">Generated Content</h3>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCopy}
                        className="flex items-center gap-2"
                      >
                        {copied ? (
                          <>
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4" />
                            Copy
                          </>
                        )}
                      </Button>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                      <p className="text-sm leading-relaxed">{generatedContent.post_content}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Platform:</span> {generatedContent.platform}
                      </div>
                      <div>
                        <span className="font-medium">Character Count:</span> {generatedContent.character_count}
                      </div>
                      <div>
                        <span className="font-medium">Estimated Engagement:</span> {generatedContent.estimated_engagement}
                      </div>
                      <div>
                        <span className="font-medium">Tone:</span> {generatedContent.tone}
                      </div>
                    </div>

                    {generatedContent.hashtags && generatedContent.hashtags.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Suggested Hashtags</h4>
                        <div className="flex flex-wrap gap-2">
                          {generatedContent.hashtags.map((hashtag: string, index: number) => (
                            <Badge key={index} variant="secondary">
                              {hashtag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {generatedContent.call_to_action && (
                      <div>
                        <h4 className="font-medium mb-2">Call to Action</h4>
                        <p className="text-sm bg-blue-50 dark:bg-blue-950/20 p-3 rounded">
                          {generatedContent.call_to_action}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            {generatedContent ? (
              <>
                <Button variant="outline" onClick={resetForm}>
                  Generate New
                </Button>
                <Button onClick={() => setOpen(false)}>
                  Done
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleGenerate}
                  disabled={!topic.trim() || generating}
                >
                  {generating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Generate Content
                    </>
                  )}
                </Button>
              </>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
