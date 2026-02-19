'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import api from '@/lib/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  sources?: string[]
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your TechPro AI assistant. I can help you with product information, order tracking, refunds, and more. How can I help you today?",
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const sessionId = useRef(`session-${Date.now()}`)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await api.sendMessage(input, sessionId.current)

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        intent: response.intent,
        sources: response.sources,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickQuestions = [
    "What laptops do you have?",
    "Track order ORD-1002",
    "Compare products 1 and 2",
    "What's your return policy?",
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
        {/* Chat Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-lg backdrop-blur-sm">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">AI Shopping Assistant</h2>
              <p className="text-sm text-blue-100">Ask me anything about products, orders, or support</p>
            </div>
          </div>
        </div>

        {/* Messages Container */}
        <div className="h-[500px] overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`flex items-start space-x-3 max-w-[80%] ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                {/* Avatar */}
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.role === 'user'
                      ? 'bg-blue-600'
                      : 'bg-gradient-to-br from-purple-500 to-blue-600'
                  }`}
                >
                  {message.role === 'user' ? (
                    <User className="h-5 w-5 text-white" />
                  ) : (
                    <Bot className="h-5 w-5 text-white" />
                  )}
                </div>

                {/* Message Content */}
                <div
                  className={`rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  {message.intent && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <span className="text-xs text-gray-500">Intent: {message.intent}</span>
                    </div>
                  )}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-500 mb-1">Sources:</p>
                      {message.sources.map((source, i) => (
                        <span key={i} className="text-xs text-gray-400 block">
                          • {source}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-600">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                    <span className="text-sm text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="px-6 py-3 bg-white border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Quick questions:</p>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInput(question)}
                  className="text-xs px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about products, orders, or support..."
                rows={1}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                disabled={isLoading}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
