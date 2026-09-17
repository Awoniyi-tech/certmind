import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { BookOpen, Search, ChevronRight, Loader } from 'lucide-react'
import { ragAPI, questionsAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

const FEATURED_TOPICS = [
  'OSPF Basics', 'BGP Path Attributes', 'MPLS LDP',
  'MSTP Configuration', 'VRRP Failover', 'BGP Route Reflector',
  'IS-IS Routing', 'QoS MQC', 'IPv6 NDP', 'DHCP Relay',
]

function cleanLessonText(value) {
  return String(value || '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/^\s*\*\s+/gm, 'â€¢ ')
    .replace(/^\s*#{1,6}\s*/gm, '')
}

export default function Learn() {
  const { selectedCert } = useStore()
  const [searchParams]   = useSearchParams()
  const [topic, setTopic]     = useState(searchParams.get('topic') || '')
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(false)
  const [depth, setDepth]     = useState('standard')
  const [topics, setTopics]   = useState([])

  useEffect(() => {
    questionsAPI.topics(selectedCert).then(setTopics).catch(() => {})
  }, [selectedCert])

  useEffect(() => {
    const t = searchParams.get('topic')
    if (t) { setTopic(t); fetchContent(t) }
  }, [searchParams])

  async function fetchContent(t, requestedDepth = depth) {
    const query = t || topic
    if (!query.trim()) return
    setLoading(true)
    const extending = requestedDepth === 'deep' && content?.topic === query
    try {
      const res = await ragAPI.learn({ topic: query, cert_id: selectedCert, depth: requestedDepth })
      setContent(prev => extending && prev
        ? { ...res, topic: query, content: `${prev.content}\n\nDEEP DIVE\n\n${res.content}`, sources: [...new Set([...(prev.sources || []), ...(res.sources || [])])] }
        : res)
    } catch {
      setContent(prev => extending && prev ? prev : { content: 'Could not load topic. Check your knowledge base.', topic: query, sources: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-2xl font-bold text-ink">Learn</h1>
        <p className="text-sm text-muted mt-1">Study from your certification materials</p>
      </div>

      {/* Search */}
      <Card>
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && fetchContent()}
              placeholder="Search any networking topic..."
              className="w-full bg-elevated border border-border rounded-xl pl-9 pr-4 py-3 text-sm text-ink placeholder:text-muted outline-none focus:border-accent/50 transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={depth}
              onChange={e => setDepth(e.target.value)}
              className="bg-elevated border border-border rounded-xl px-3 text-sm text-ink outline-none"
            >
              <option value="standard">Standard</option>
              <option value="deep">Deep Dive</option>
            </select>
            <Button onClick={() => fetchContent()} disabled={loading || !topic.trim()}>
              {loading ? <Loader size={15} className="animate-spin" /> : <BookOpen size={15} />}
              {loading ? 'Loading...' : 'Learn'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Featured topics */}
      {!content && !loading && (
        <div className="space-y-4">
          <h2 className="font-display font-semibold text-sm text-ink">Featured Topics</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {FEATURED_TOPICS.map(t => (
              <button
                key={t}
                onClick={() => { setTopic(t); fetchContent(t) }}
                className="px-3 py-2.5 rounded-xl bg-surface border border-border hover:border-accent/40 hover:bg-elevated text-xs font-medium text-muted hover:text-ink transition-all text-left"
              >
                {t}
              </button>
            ))}
          </div>

          {topics.length > 0 && (
            <>
              <h2 className="font-display font-semibold text-sm text-ink pt-2">From Your Question Bank</h2>
              <div className="flex flex-wrap gap-2">
                {topics.map(t => (
                  <button
                    key={t.topic}
                    onClick={() => { setTopic(t.topic); fetchContent(t.topic) }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-elevated border border-border hover:border-accent/40 text-xs text-muted hover:text-ink transition-all"
                  >
                    {t.topic}
                    <span className="opacity-50">{t.count}</span>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <Card className="flex items-center justify-center py-16">
          <div className="text-center space-y-3">
            <div className="w-10 h-10 border-2 border-accent/30 border-t-accent rounded-full animate-spin mx-auto" />
            <p className="text-sm text-muted">Searching documentation for <span className="text-ink">{topic}</span>...</p>
          </div>
        </Card>
      )}

      {/* Content */}
      {content && !loading && (
        <div className="space-y-4 animate-slide-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="font-display font-bold text-xl text-ink">{content.topic}</h2>
              {depth === 'deep' && <Badge variant="accent">Deep Dive</Badge>}
            </div>
            <Button variant="ghost" size="sm" onClick={() => setContent(null)}>
              â† Back
            </Button>
          </div>

          <Card>
            <div className="prose prose-invert max-w-none">
              {content.lesson ? (
                <div className="space-y-5">
                  {content.lesson.objective && (
                    <div className="rounded-xl bg-elevated border border-border p-4">
                      <p className="text-xs uppercase tracking-wide text-accent mb-1">Objective</p>
                      <p className="text-sm text-ink/90">{content.lesson.objective}</p>
                    </div>
                  )}
                  {content.lesson.overview && (
                    <section>
                      <h3 className="font-display font-semibold text-ink mb-2">Overview</h3>
                      <p className="text-sm text-ink/90 leading-relaxed">{content.lesson.overview}</p>
                    </section>
                  )}
                  {(content.lesson.sections || []).map((section, i) => (
                    <section key={i}>
                      <h3 className="font-display font-semibold text-ink mb-2">{section.title}</h3>
                      <p className="text-sm text-ink/90 leading-relaxed whitespace-pre-wrap">{section.content}</p>
                    </section>
                  ))}
                  {[
                    ['Key facts', content.lesson.key_facts],
                    ['Exam points', content.lesson.exam_points],
                    ['Common mistakes', content.lesson.common_mistakes],
                    ['Quick check', content.lesson.quick_check],
                  ].map(([label, items]) => items?.length > 0 && (
                    <section key={label}>
                      <h3 className="font-display font-semibold text-ink mb-2">{label}</h3>
                      <ol className="list-decimal ml-5 space-y-1 text-sm text-ink/90">
                        {items.map((item, i) => <li key={i}>{item}</li>)}
                      </ol>
                    </section>
                  ))}
                </div>
              ) : (
                <pre className="whitespace-pre-wrap font-body text-sm text-ink/90 leading-relaxed">
                  {cleanLessonText(content.content)}
                </pre>
              )}
            </div>

            {content.sources?.length > 0 && (
              <div className="mt-6 pt-4 border-t border-border">
                <p className="text-xs text-muted font-medium mb-2">Sources</p>
                <div className="flex flex-wrap gap-1.5">
                  {content.sources.filter(Boolean).slice(0, 5).map((s, i) => (
                    <Badge key={i} variant="default">
                      {String(s).split('/').pop()?.replace('.md', '') || s}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </Card>

          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => { setDepth('deep'); fetchContent(undefined, 'deep') }}
              disabled={depth === 'deep' || loading}
            >
              Deep Dive â†’
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                const url = `/practice?topic=${encodeURIComponent(content.topic)}`
                window.location.href = url
              }}
            >
              Practice This Topic
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

