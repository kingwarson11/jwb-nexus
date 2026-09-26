import { useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

type Message = { role: 'user' | 'assistant'; text: string }

const SUGGESTIONS = [
  'How is my business doing?',
  'What should I restock?',
  'Why did my profit fall?',
  'Which products are selling fastest?',
]

export default function AIAnalyst() {
  const { business } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const ask = async (question: string) => {
    if (!business || !question.trim()) return
    setMessages((m) => [...m, { role: 'user', text: question }])
    setInput('')
    setLoading(true)
    setError('')
    try {
      const res = await api.post(`/api/businesses/${business.id}/ai/query`, { question })
      setMessages((m) => [...m, { role: 'assistant', text: res.answer }])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reach the AI analyst')
    } finally {
      setLoading(false)
    }
  }

  if (!business) return null

  return (
    <div className="p-8 max-w-3xl mx-auto flex flex-col h-screen">
      <h1 className="text-2xl font-bold mb-1">AI Business Analyst</h1>
      <p className="text-gray-500 mb-4">Ask a plain-language question — answers are grounded in your actual data, never invented.</p>

      {messages.length === 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => ask(s)}
              className="text-sm bg-white border rounded-full px-3 py-1.5 hover:border-brand-500">
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`max-w-[85%] rounded-xl p-3 text-sm whitespace-pre-line ${
            m.role === 'user' ? 'bg-brand-600 text-white ml-auto' : 'bg-white border'
          }`}>
            {m.text}
          </div>
        ))}
        {loading && <div className="bg-white border rounded-xl p-3 text-sm text-gray-400 w-fit">Thinking…</div>}
      </div>

      {error && <div className="text-sm text-red-600 bg-red-50 rounded p-2 mb-3">{error}</div>}

      <form onSubmit={(e) => { e.preventDefault(); ask(input) }} className="flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your business…"
          className="flex-1 border rounded-lg px-3 py-2 text-sm" />
        <button disabled={loading} className="bg-brand-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
          Ask
        </button>
      </form>
    </div>
  )
}
