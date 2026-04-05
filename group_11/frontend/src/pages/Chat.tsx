import { useCallback, useEffect, useRef, useState } from 'react'
import Navbar from '../components/Navbar'
import { sendChatMessage } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  agentName?: string
  agentDisplayName?: string
}

const SUGGESTED_QUESTIONS = [
  { text: 'Analyze my debt and tell me what needs urgent attention', agent: 'Debt Analyzer', agentKey: 'debt_analyzer' },
  { text: 'Create a savings plan for me based on my income', agent: 'Savings Strategist', agentKey: 'savings_strategist' },
  { text: 'What budget changes should I make?', agent: 'Budget Advisor', agentKey: 'budget_advisor' },
  { text: 'Compare avalanche vs snowball payoff strategies for my debts', agent: 'Payoff Optimizer', agentKey: 'payoff_optimizer' },
  { text: 'What is hurting my credit score the most?', agent: 'Debt Analyzer', agentKey: 'debt_analyzer' },
]

const AGENT_COLORS: Record<string, string> = {
  orchestrator: 'bg-blue-100 text-blue-700',
  debt_analyzer: 'bg-red-100 text-red-700',
  savings_strategist: 'bg-green-100 text-green-700',
  budget_advisor: 'bg-purple-100 text-purple-700',
  payoff_optimizer: 'bg-orange-100 text-orange-700',
  error: 'bg-red-100 text-red-700',
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: msg }])
    setLoading(true)

    try {
      const res = await sendChatMessage(msg, sessionId)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.message,
          agentName: res.agent_name,
          agentDisplayName: res.agent_display_name,
        },
      ])
    } catch (err: any) {
      const raw = err.message || 'Unknown error'
      // Extract the friendly detail from "API error 500: {json}" format
      let friendly = raw
      try {
        const jsonMatch = raw.match(/\{.*\}/)
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0])
          friendly = parsed.detail || raw
        }
      } catch {
        // keep raw message
      }
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: friendly, agentName: 'error', agentDisplayName: 'System' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-16 max-w-4xl mx-auto flex flex-col h-[calc(100vh-4rem)]">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-4">
          {messages.length === 0 && (
            <div className="text-center py-2">
              <div className="w-16 h-16 bg-brand-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-slate-900 mb-2">AI Financial Coach</h2>
              <p className="text-slate-500 mb-8 max-w-md mx-auto">
                Ask me about your debts, savings, budget, or debt payoff strategies. I have access to your credit report data.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q.text}
                    onClick={() => handleSend(q.text)}
                    className="relative text-left p-3 pt-5 rounded-xl border border-slate-200 bg-white hover:border-brand-300 hover:bg-brand-50 text-sm text-slate-700 transition-colors"
                  >
                    <span className={`absolute -top-2.5 right-3 text-xs font-medium px-2 py-0.5 rounded-full ${AGENT_COLORS[q.agentKey] || 'bg-gray-100 text-gray-700'}`}>
                      {q.agent}
                    </span>
                    {q.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-1' : ''}`}>
                {msg.role === 'assistant' && msg.agentName && (
                  <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full mb-1 ${AGENT_COLORS[msg.agentName] || 'bg-gray-100 text-gray-700'}`}>
                    {msg.agentDisplayName || msg.agentName}
                  </span>
                )}
                <div
                  className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-brand-600 text-white'
                      : msg.agentName === 'error'
                        ? 'bg-red-50 border border-red-200 text-red-800'
                        : 'bg-white border border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-slate-200 bg-white px-4 py-4">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your finances..."
              rows={1}
              className="flex-1 resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
