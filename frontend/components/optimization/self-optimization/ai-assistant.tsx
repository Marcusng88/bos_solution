"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { MessageCircle, Send, Bot, User, X, Minimize2, Maximize2 } from "lucide-react"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm your AI marketing assistant. I can help you optimize your campaigns, analyze performance, and provide actionable insights. What would you like to know?",
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const { apiClient, userId } = useApiClient()

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = inputValue
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await apiClient.chatWithAI(userId, currentInput)
      console.log('AI Response received:', response)
      console.log('Response type:', typeof response)
      console.log('Response keys:', Object.keys(response || {}))
      
      // Handle both response structures for backward compatibility
      let aiResponseText = ''
      if (typeof response === 'string') {
        aiResponseText = response
      } else if (response && typeof response === 'object' && 'response' in response) {
        aiResponseText = (response as any).response || 'No response content found'
      } else {
        console.warn('Unexpected response structure:', response)
        aiResponseText = 'I received your message but encountered an unexpected response format.'
      }
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponseText,
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error: any) {
      console.error('Failed to get AI response:', handleApiError(error))
      // Fallback to mock response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later.",
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase()
    
    if (input.includes('budget') || input.includes('spend')) {
      return "I see you're asking about budget management. Based on your recent data, you've utilized 74% of today's budget. I recommend setting up alerts when utilization exceeds 80% to prevent overspending. Would you like me to help you set up these alerts?"
    }
    
    if (input.includes('performance') || input.includes('ctr') || input.includes('conversion')) {
      return "Great question about performance! Your top performing campaign 'Summer Sale' has a 3.2% CTR and $2.15 CPC. However, 'Brand Awareness' campaign is underperforming with 0.8% CTR. I recommend pausing the underperforming campaign and reallocating budget to your winners."
    }
    
    if (input.includes('recommendation') || input.includes('optimize')) {
      return "I have several optimization recommendations for you: 1) Scale your 'Summer Sale' campaign budget by 30% - it's performing 40% above average. 2) Pause 'Brand Awareness' campaign - it has zero conversions after $200 spend. 3) Test new ad creatives for campaigns with CTR below 1.5%. Would you like detailed action steps for any of these?"
    }
    
    if (input.includes('alert') || input.includes('issue') || input.includes('problem')) {
      return "You currently have 3 active alerts: 1) 'Mobile Campaign' exceeded budget by 15% yesterday, 2) 'Retargeting Campaign' has declining CTR (down 25% this week), 3) Spending spike detected on 'Black Friday Prep' campaign. I recommend addressing the budget overage first. Shall I help you create an action plan?"
    }
    
    if (input.includes('competitor') || input.includes('market')) {
      return "While I focus on self-optimization, I can see your campaigns are performing well relative to industry benchmarks. Your average CTR of 2.4% is above the industry average of 1.9%. However, there's room for improvement in conversion rate optimization. Would you like suggestions for improving conversion rates?"
    }
    
    return "I understand you're looking for insights about your campaign optimization. I can help you with budget monitoring, performance analysis, risk detection, and actionable recommendations. Could you be more specific about what aspect of your campaigns you'd like to optimize?"
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full h-14 w-14 shadow-lg hover:shadow-xl transition-all duration-200 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className={`w-96 shadow-2xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[500px]'}`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <CardTitle className="text-sm font-medium">AI Marketing Assistant</CardTitle>
          </div>
          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-8 w-8 p-0"
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(false)}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {!isMinimized && (
          <CardContent className="flex flex-col h-[432px] p-0">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-2 max-w-[90%] ${
                        message.isUser ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <div
                        className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          message.isUser
                            ? 'bg-gray-200'
                            : 'bg-gradient-to-r from-blue-600 to-purple-600'
                        }`}
                      >
                        {message.isUser ? (
                          <User className="h-4 w-4 text-gray-600" />
                        ) : (
                          <Bot className="h-4 w-4 text-white" />
                        )}
                      </div>
                      <div
                        className={`rounded-lg p-3 ${
                          message.isUser
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm break-words whitespace-pre-wrap overflow-hidden" style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}>{message.content}</p>
                        <p className="text-xs mt-1 opacity-70">
                          {message.timestamp.toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start space-x-2">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-white" />
                      </div>
                      <div className="bg-gray-100 rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-100"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-200"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about your campaigns..."
                  className="flex-1"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-1 mt-2">
                {['Budget analysis', 'Performance review', 'Recommendations', 'Alert summary'].map((suggestion) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => setInputValue(suggestion)}
                    className="text-xs h-6 px-2"
                    disabled={isLoading}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  )
}
