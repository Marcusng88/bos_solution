"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useApiClient, handleApiError } from "@/lib/api-client"
import { MessageCircle, Send, Bot, User, X, Minimize2, Maximize2, Loader2 } from "lucide-react"
import { useUser } from "@clerk/nextjs"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

// Function to format AI responses for better readability (ChatGPT style)
function formatAIResponse(content: string): string {
  return content
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
    .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
    .replace(/^\s*[-*]\s+/gm, '• ') // Convert list markers to bullets
    .replace(/\n\s*\n/g, '\n\n') // Clean up extra line breaks
    .replace(/Campaign Data:/g, '📊 Campaign Data:')
    .replace(/Competitor Data:/g, '🏢 Competitor Data:')
    .replace(/Market Monitoring:/g, '👁️ Market Monitoring:')
    .replace(/Overall Performance Summary:/g, '📈 Overall Performance Summary:')
    .replace(/Campaign Optimization:/g, '🚀 Campaign Optimization:')
    .replace(/Budget Management:/g, '💰 Budget Management:')
    .replace(/Performance Analysis:/g, '📊 Performance Analysis:')
    .replace(/Risk Assessment:/g, '⚠️ Risk Assessment:')
    .replace(/Actionable Steps:/g, '✅ Actionable Steps:')
    .replace(/Recommendations:/g, '💡 Recommendations:')
    .replace(/High-Performing Campaigns:/g, '🏆 High-Performing Campaigns:')
    .replace(/Low-Performing Campaigns:/g, '📉 Low-Performing Campaigns:')
    .replace(/Ongoing Campaigns:/g, '🔄 Ongoing Campaigns:')
    .replace(/Status:/g, '📋 Status:')
    .replace(/Impressions:/g, '👁️ Impressions:')
    .replace(/Clicks:/g, '🖱️ Clicks:')
    .replace(/CTR:/g, '📊 CTR:')
    .replace(/CPC:/g, '💰 CPC:')
    .replace(/Spend:/g, '💸 Spend:')
    .replace(/Budget:/g, '📈 Budget:')
    .replace(/Conversions:/g, '🎯 Conversions:')
    .replace(/Net Profit:/g, '💵 Net Profit:')
    .trim()
}

export function AIChatWidget() {
  const { user, isSignedIn } = useUser()
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm your AI marketing assistant. I can help you with campaign optimization, performance analysis, competitor insights, and answer any business questions. What would you like to know?",
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  // Only show the widget if user is signed in
  if (!isSignedIn || !user) {
    return null
  }

  // Get API client - this will throw an error if user is not signed in, but we've already checked above
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
      console.log("🔍 Sending message to AI:", currentInput)
      console.log("🔍 User ID:", userId)
      
      const response = await apiClient.chatWithAI(userId, currentInput)
      console.log("✅ AI response received:", response)
      console.log("✅ AI response.response:", response.response)
      console.log("✅ AI response type:", typeof response.response)
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('❌ Failed to get AI response:', error)
      console.error('❌ Error details:', handleApiError(error))
      
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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickQuestions = [
    "How are my campaigns performing?",
    "What are the top optimization opportunities?",
    "Any budget risks I should know about?",
    "How do I compare to competitors?",
    "What's my campaign health score?"
  ]

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
             <Card className={`w-[600px] shadow-2xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[700px]'}`}>
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
                     <CardContent className="flex flex-col h-[632px] p-0">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-2 max-w-[80%] ${
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
                         className={`rounded-lg p-4 ${
                           message.isUser
                             ? 'bg-blue-600 text-white ml-8'
                             : 'bg-white text-gray-900 mr-8 border border-gray-200 shadow-sm'
                         }`}
                       >
                         <div className={`text-sm whitespace-pre-wrap leading-relaxed ${
                           message.isUser ? '' : 'prose prose-sm max-w-none'
                         }`}>
                           {message.isUser ? message.content : formatAIResponse(message.content)}
                         </div>
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
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              
              {/* Quick Questions */}
              <div className="flex flex-wrap gap-1 mt-2">
                {quickQuestions.map((question) => (
                  <Button
                    key={question}
                    variant="outline"
                    size="sm"
                    onClick={() => setInputValue(question)}
                    className="text-xs h-6 px-2"
                    disabled={isLoading}
                  >
                    {question}
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
