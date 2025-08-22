"use client"

import { useState, useEffect, useRef } from "react"
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
  isTyping?: boolean
}

// Function to format AI responses for better readability with more emojis and ChatGPT-like styling
function formatAIResponse(content: string): string {
  return content
    .replace(/### (.*?)(?:\n|$)/g, '<h3 class="text-lg font-bold text-gray-900 mb-2 mt-4">$1</h3>') // Convert ### headers to HTML
    .replace(/## (.*?)(?:\n|$)/g, '<h2 class="text-xl font-bold text-gray-900 mb-3 mt-6">$1</h2>') // Convert ## headers to HTML
    .replace(/# (.*?)(?:\n|$)/g, '<h1 class="text-2xl font-bold text-gray-900 mb-4 mt-8">$1</h1>') // Convert # headers to HTML
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>') // Convert bold markdown to HTML
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>') // Convert italic markdown to HTML
    .replace(/^\s*[-*]\s+/gm, '• ') // Convert list markers to bullets
    .replace(/\n\s*\n/g, '\n\n') // Clean up extra line breaks
    .replace(/Campaign Data:/g, '📊 <strong class="font-semibold">Campaign Data:</strong>')
    .replace(/Competitor Data:/g, '🏢 <strong class="font-semibold">Competitor Data:</strong>')
    .replace(/Market Monitoring:/g, '👁️ <strong class="font-semibold">Market Monitoring:</strong>')
    .replace(/Overall Performance Summary:/g, '📈 <strong class="font-semibold">Overall Performance Summary:</strong>')
    .replace(/Campaign Optimization:/g, '🚀 <strong class="font-semibold">Campaign Optimization:</strong>')
    .replace(/Budget Management:/g, '💰 <strong class="font-semibold">Budget Management:</strong>')
    .replace(/Performance Analysis:/g, '📊 <strong class="font-semibold">Performance Analysis:</strong>')
    .replace(/Risk Assessment:/g, '⚠️ <strong class="font-semibold">Risk Assessment:</strong>')
    .replace(/Actionable Steps:/g, '✅ <strong class="font-semibold">Actionable Steps:</strong>')
    .replace(/Recommendations:/g, '💡 <strong class="font-semibold">Recommendations:</strong>')
    .replace(/High-Performing Campaigns:/g, '🏆 <strong class="font-semibold">High-Performing Campaigns:</strong>')
    .replace(/Low-Performing Campaigns:/g, '📉 <strong class="font-semibold">Low-Performing Campaigns:</strong>')
    .replace(/Ongoing Campaigns:/g, '🔄 <strong class="font-semibold">Ongoing Campaigns:</strong>')
    .replace(/Status:/g, '📋 <strong class="font-semibold">Status:</strong>')
    .replace(/Impressions:/g, '👁️ <strong class="font-semibold">Impressions:</strong>')
    .replace(/Clicks:/g, '🖱️ <strong class="font-semibold">Clicks:</strong>')
    .replace(/CTR:/g, '📊 <strong class="font-semibold">CTR:</strong>')
    .replace(/CPC:/g, '💰 <strong class="font-semibold">CPC:</strong>')
    .replace(/Spend:/g, '💸 <strong class="font-semibold">Spend:</strong>')
    .replace(/Budget:/g, '📈 <strong class="font-semibold">Budget:</strong>')
    .replace(/Conversions:/g, '🎯 <strong class="font-semibold">Conversions:</strong>')
    .replace(/Net Profit:/g, '💵 <strong class="font-semibold">Net Profit:</strong>')
    .replace(/Risk Score:/g, '⚠️ <strong class="font-semibold">Risk Score:</strong>')
    .replace(/Performance Score:/g, '📊 <strong class="font-semibold">Performance Score:</strong>')
    .replace(/Health Score:/g, '🏥 <strong class="font-semibold">Health Score:</strong>')
    .replace(/Critical Risk/g, '🔴 <strong class="font-semibold">Critical Risk</strong>')
    .replace(/High Risk/g, '🟠 <strong class="font-semibold">High Risk</strong>')
    .replace(/Medium Risk/g, '🟡 <strong class="font-semibold">Medium Risk</strong>')
    .replace(/Low Risk/g, '🟢 <strong class="font-semibold">Low Risk</strong>')
    .replace(/Good/g, '✅ <strong class="font-semibold">Good</strong>')
    .replace(/Poor/g, '❌ <strong class="font-semibold">Poor</strong>')
    .replace(/Excellent/g, '🌟 <strong class="font-semibold">Excellent</strong>')
    .replace(/Average/g, '📊 <strong class="font-semibold">Average</strong>')
    .replace(/Below Average/g, '📉 <strong class="font-semibold">Below Average</strong>')
    .replace(/Above Average/g, '📈 <strong class="font-semibold">Above Average</strong>')
    .trim()
}

// Function to split text into lines for progressive display
function splitIntoLines(text: string): string[] {
  // Split by lines but preserve HTML tags
  const lines = text.split('\n')
  const result: string[] = []
  
  for (const line of lines) {
    if (line.trim() !== '') {
      result.push(line)
    }
  }
  
  return result
}

// Inner component that requires authentication
function AIChatWidgetInner() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! 👋 I'm your AI marketing assistant! 🤖 I can help you with campaign optimization, performance analysis, competitor insights, and answer any business questions. What would you like to know? 💡",
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [typingMessageId, setTypingMessageId] = useState<string | null>(null)
  const [currentLineIndex, setCurrentLineIndex] = useState(0)
  const [currentLines, setCurrentLines] = useState<string[]>([])
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Get API client - this will only be called when user is signed in
  const { apiClient, userId } = useApiClient()

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  // Progressive text typing effect
  useEffect(() => {
    if (typingMessageId && currentLines.length > 0 && currentLineIndex < currentLines.length) {
      const timer = setTimeout(() => {
        setMessages(prev => prev.map(msg => 
          msg.id === typingMessageId 
            ? { 
                ...msg, 
                content: formatAIResponse(currentLines.slice(0, currentLineIndex + 1).join('\n'))
              }
            : msg
        ))
        setCurrentLineIndex(prev => prev + 1)
      }, 80) // Slightly slower for better readability

      return () => clearTimeout(timer)
    } else if (typingMessageId && currentLineIndex >= currentLines.length) {
      // Finished typing
      setTypingMessageId(null)
      setCurrentLineIndex(0)
      setCurrentLines([])
    }
  }, [typingMessageId, currentLines, currentLineIndex])

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
      
      const response = await apiClient.chatWithAI(userId, currentInput) as { response: string }
      console.log("✅ AI response received:", response)
      console.log("✅ AI response.response:", response.response)
      console.log("✅ AI response type:", typeof response.response)
      
      // Create AI message with typing indicator
      const aiMessageId = (Date.now() + 1).toString()
      const aiMessage: Message = {
        id: aiMessageId,
        content: "",
        isUser: false,
        timestamp: new Date(),
        isTyping: true
      }
      
      setMessages(prev => [...prev, aiMessage])
      
      // Start progressive typing with raw text first
      const lines = splitIntoLines(response.response)
      setCurrentLines(lines)
      setCurrentLineIndex(0)
      setTypingMessageId(aiMessageId)
      
    } catch (error) {
      console.error('❌ Failed to get AI response:', error)
      console.error('❌ Error details:', handleApiError(error))
      
      // Fallback to mock response
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I'm having trouble connecting to the server right now. Please try again later. 😔",
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
    "How are my campaigns performing? 📊",
    "What are the top optimization opportunities? 🚀",
    "Any budget risks I should know about? ⚠️",
    "How do I compare to competitors? 🏢",
    "What's my campaign health score? 🏥"
  ]

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full h-16 w-16 shadow-lg hover:shadow-xl transition-all duration-200 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          <MessageCircle className="h-8 w-8" />
        </Button>
      </div>
    )
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Card className={`w-[650px] shadow-2xl transition-all duration-300 ${isMinimized ? 'h-16' : 'h-[750px]'}`}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center space-x-2">
            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <CardTitle className="text-lg font-semibold">AI Marketing Assistant 🤖</CardTitle>
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
          <CardContent className="flex flex-col h-[682px] p-0">
            {/* Messages */}
            <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex items-start space-x-3 max-w-[85%] ${
                        message.isUser ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      <div
                        className={`h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                          message.isUser
                            ? 'bg-gray-200'
                            : 'bg-gradient-to-r from-blue-600 to-purple-600'
                        }`}
                      >
                        {message.isUser ? (
                          <User className="h-5 w-5 text-gray-600" />
                        ) : (
                          <Bot className="h-5 w-5 text-white" />
                        )}
                      </div>
                      <div
                        className={`rounded-lg p-4 ${
                          message.isUser
                            ? 'bg-blue-600 text-white ml-10'
                            : 'bg-white text-gray-900 mr-10 border border-gray-200 shadow-sm'
                        }`}
                      >
                        <div 
                          className={`text-base whitespace-pre-wrap leading-relaxed ${
                            message.isUser ? '' : 'prose prose-base max-w-none'
                          }`}
                          dangerouslySetInnerHTML={{
                            __html: message.isUser ? message.content : message.content
                          }}
                        />
                        <p className="text-sm mt-2 opacity-70">
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
                    <div className="flex items-start space-x-3">
                      <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-gray-100 rounded-lg p-4">
                        <div className="flex space-x-2">
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-pulse"></div>
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-pulse delay-100"></div>
                          <div className="w-3 h-3 bg-gray-400 rounded-full animate-pulse delay-200"></div>
                        </div>
                        <p className="text-sm text-gray-500 mt-2">AI is thinking... 🤔</p>
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
                  placeholder="Ask about your campaigns... 💬"
                  className="flex-1 text-base"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="sm"
                  className="h-10 px-4"
                >
                  {isLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </Button>
              </div>
              
              {/* Quick Questions */}
              <div className="flex flex-wrap gap-2 mt-3">
                {quickQuestions.map((question) => (
                  <Button
                    key={question}
                    variant="outline"
                    size="sm"
                    onClick={() => setInputValue(question)}
                    className="text-sm h-8 px-3"
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

// Main component that handles authentication
export function AIChatWidget() {
  const { user, isSignedIn } = useUser()

  // Only render the widget if user is signed in
  if (!isSignedIn || !user) {
    return null
  }

  return <AIChatWidgetInner />
}
