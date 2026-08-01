import { useState, useRef, useEffect } from 'react'
import { Send, Zap, RotateCcw } from 'lucide-react'
import { ragAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

const SUGGESTED = [
  'Explain OSPF DR/BDR election process',
  'How does BGP route reflector work?',
  'What is the difference between MSTP and RSTP?',
  'Explain MPLS label switching',
  'How does VRRP handle failover?',
  'What are the BGP path selection attributes in order?',
]

export default function AITutor() {
  const { selectedCert, certifications } = useStore()
  const cert = certifications.find(c => c.id === selectedCert)
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(text) {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')

    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const history = messages.slice(-8).map(m => ({ role: m.role, content: m.content }))
      const res = await ragAPI.tutor({ message: msg, cert_id: selectedCert, history })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response,
        sources: res.sources ?? [],
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Tutor unavailable right now. Check your API key and knowledge base.',
        sources: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">AI Tutor</h1>
          <p className="text-sm text-muted mt-1">
            Powered by {cert?.name} documentation
          </p>
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => setMessages([])}>
            <RotateCcw size={14} /> Clear
          </Button>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl bg-accent/15 flex items-center justify-center">
              <Zap size={24} className="text-accent-soft" />
            </div>
            <div>
              <p className="font-display font-semibold text-ink">Ask Anything</p>
              <p className="text-sm text-muted mt-1 max-w-sm">
                Your AI tutor is grounded in the {cert?.name} documentation. No hallucinations — just verified answers.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-xl">
              {SUGGESTED.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left px-4 py-3 rounded-xl bg-surface border border-border hover:border-accent/40 hover:bg-elevated transition-all text-xs text-muted hover:text-ink"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] ${m.role === 'user' ? 'order-1' : 'order-2'}`}>
                  {m.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-1.5">
                      <div className="w-5 h-5 rounded-md bg-accent/20 flex items-center justify-center">
                        <Zap size={11} className="text-accent-soft" />
                      </div>
                      <span className="text-xs font-medium text-muted">CertMind Tutor</span>
                    </div>
                  )}
                  <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-accent text-white rounded-tr-sm'
                      : 'bg-surface border border-border text-ink rounded-tl-sm'
                  }`}>
                    <pre className="whitespace-pre-wrap font-body">{m.content}</pre>
                  </div>
                  {m.sources?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {m.sources.slice(0, 3).map((s, j) => (
                        <Badge key={j} variant="default">
                          {String(s).split('/').pop()?.replace('.md', '') || s}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-surface border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1">
                    {[0, 1, 2].map(i => (
                      <div
                        key={i}
                        className="w-2 h-2 rounded-full bg-muted animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}
            <div ref={endRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="border border-border rounded-2xl bg-surface flex items-end gap-3 px-4 py-3">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
          }}
          placeholder="Ask about any networking concept, command, or exam topic..."
          rows={1}
          className="flex-1 bg-transparent text-sm text-ink placeholder:text-muted outline-none resize-none max-h-32"
          style={{ height: 'auto' }}
          onInput={e => {
            e.target.style.height = 'auto'
            e.target.style.height = e.target.scrollHeight + 'px'
          }}
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="w-9 h-9 rounded-xl bg-accent hover:bg-accent-soft disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-all active:scale-95 shrink-0"
        >
          <Send size={15} className="text-white" />
        </button>
      </div>
    </div>
  )
}
