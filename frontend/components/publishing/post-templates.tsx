"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { useToast } from "@/hooks/use-toast"
import { Search, Plus, Eye, Copy } from "lucide-react"

const templates = [
  {
    id: 1,
    name: "Product Launch",
    category: "Marketing",
    description: "Perfect for announcing new products or features",
    content:
      "🚀 Exciting news! We're thrilled to introduce [Product Name] - a game-changing solution that will [benefit]. \n\n✨ Key features:\n• [Feature 1]\n• [Feature 2]\n• [Feature 3]\n\nReady to transform your [industry/workflow]? Learn more: [link]\n\n#ProductLaunch #Innovation #[YourBrand]",
    platforms: ["facebook", "instagram", "linkedin"],
    engagement: "High",
  },
  {
    id: 2,
    name: "Behind the Scenes",
    category: "Engagement",
    description: "Show your team and company culture",
    content:
      "👋 Meet the amazing team behind [Company Name]! \n\nToday we're giving you a sneak peek into our [department/process]. Our passionate team works hard to [mission/goal].\n\n💡 Fun fact: [interesting detail about your team/process]\n\nWhat would you like to see more of behind the scenes? Let us know in the comments! 👇\n\n#BehindTheScenes #TeamSpotlight #CompanyCulture",
    platforms: ["instagram", "facebook"],
    engagement: "High",
  },
  {
    id: 3,
    name: "Customer Success Story",
    category: "Social Proof",
    description: "Highlight customer achievements and testimonials",
    content:
      '🌟 Customer Spotlight: [Customer Name]\n\n"[Customer testimonial quote]" - [Customer Name], [Title] at [Company]\n\n[Customer Name] achieved [specific result/improvement] using our [product/service]. Their success story shows how [benefit/value proposition].\n\n👏 Congratulations [Customer Name]! We\'re proud to be part of your journey.\n\n#CustomerSuccess #Testimonial #Results',
    platforms: ["linkedin", "facebook"],
    engagement: "Medium",
  },
  {
    id: 4,
    name: "Educational Content",
    category: "Value",
    description: "Share tips, insights, and industry knowledge",
    content:
      "📚 [Topic] 101: Everything You Need to Know\n\nHere are [number] essential tips for [topic]:\n\n1️⃣ [Tip 1 with brief explanation]\n2️⃣ [Tip 2 with brief explanation]\n3️⃣ [Tip 3 with brief explanation]\n\n💡 Pro tip: [Additional valuable insight]\n\nWhich tip will you try first? Share your thoughts below! 👇\n\n#Education #Tips #[Industry] #KnowledgeSharing",
    platforms: ["linkedin", "twitter"],
    engagement: "Medium",
  },
  {
    id: 5,
    name: "Seasonal Promotion",
    category: "Sales",
    description: "Promote seasonal offers and limited-time deals",
    content:
      "🎉 [Season/Holiday] Special Offer!\n\nFor a limited time, enjoy [discount/offer] on [product/service]! \n\n⏰ Offer valid until [date]\n🎁 Perfect for [use case/occasion]\n✅ [Benefit 1]\n✅ [Benefit 2]\n\nDon't miss out - shop now: [link]\n\n#Sale #LimitedTime #[Season] #SpecialOffer",
    platforms: ["facebook", "instagram"],
    engagement: "High",
  },
  {
    id: 6,
    name: "Question/Poll",
    category: "Engagement",
    description: "Engage your audience with questions and polls",
    content:
      "🤔 We want to hear from you!\n\n[Engaging question related to your industry/product]?\n\nA) [Option 1]\nB) [Option 2]\nC) [Option 3]\nD) [Other - tell us in comments!]\n\nYour feedback helps us [how it helps]. Can't wait to see your responses! 👇\n\n#Community #Feedback #YourVoiceMatters #[Topic]",
    platforms: ["facebook", "instagram", "twitter"],
    engagement: "High",
  },
]

export function PostTemplates() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const { toast } = useToast()

  const categories = ["all", ...Array.from(new Set(templates.map((t) => t.category)))]

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || template.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleUseTemplate = (template: (typeof templates)[0]) => {
    toast({
      title: "Template applied",
      description: `${template.name} template has been loaded into the post creator.`,
    })
  }

  const handlePreview = (template: (typeof templates)[0]) => {
    toast({
      title: "Template preview",
      description: "Opening template preview...",
    })
  }

  const handleCopy = (template: (typeof templates)[0]) => {
    navigator.clipboard.writeText(template.content)
    toast({
      title: "Template copied",
      description: "Template content has been copied to your clipboard.",
    })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Post Templates</CardTitle>
          <CardDescription>Pre-designed templates to speed up your content creation</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Search and Filter */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category === "all" ? "All" : category}
                </Button>
              ))}
            </div>
          </div>

          {/* Templates Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredTemplates.map((template) => (
              <Card key={template.id} className="p-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{template.name}</h3>
                      <p className="text-sm text-muted-foreground">{template.description}</p>
                    </div>
                    <Badge variant="secondary">{template.category}</Badge>
                  </div>

                  <div className="text-xs text-muted-foreground line-clamp-3 bg-gray-50 dark:bg-gray-800/50 p-2 rounded">
                    {template.content}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={template.engagement === "High" ? "default" : "secondary"} className="text-xs">
                        {template.engagement} engagement
                      </Badge>
                      <span className="text-xs text-muted-foreground">{template.platforms.length} platforms</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handlePreview(template)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleCopy(template)}>
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button size="sm" onClick={() => handleUseTemplate(template)}>
                        Use Template
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {filteredTemplates.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p>No templates found matching your criteria</p>
            </div>
          )}

          {/* Create Custom Template */}
          <Card className="mt-6 border-dashed">
            <CardContent className="flex items-center justify-center py-8">
              <div className="text-center">
                <Plus className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                <h3 className="font-semibold mb-1">Create Custom Template</h3>
                <p className="text-sm text-muted-foreground mb-4">Save your frequently used content as templates</p>
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Template
                </Button>
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  )
}
