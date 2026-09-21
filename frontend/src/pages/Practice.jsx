import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Target, ChevronRight, Sparkles, Upload, RefreshCw } from 'lucide-react'
import { questionsAPI, examAPI, dumpsAPI, ragAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'

const QUESTION_TYPES = [
  { key: 'all',       label: 'All Types',       desc: 'Mixed question types' },
  { key: 'single',    label: 'Single Choice',   desc: 'One correct answer' },
  { key: 'multiple',  label: 'Multiple Choice', desc: 'Multiple correct answers' },
  { key: 'truefalse', label: 'True / False',    desc: 'Binary decisions' },
]

const COUNTS = [10, 20, 40, 60]

export default function Practice() {
  const navigate = useNavigate()
  const { selectedCert } = useStore()
  const [topics, setTopics]   = useState([])
  const [topic, setTopic]     = useState('')
  const [qType, setQType]     = useState('all')
  const [count, setCount]     = useState(20)
  const [custom, setCustom]   = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  // Source selection — same as ExamSetup
  const [tab, setTab]         = useState('generate')
  const [banks, setBanks]     = useState([])
  const [selBank, setSelBank] = useState(null)

  useEffect(() => {
    questionsAPI.topics(selectedCert).then(setTopics).catch(() => {})
    dumpsAPI.list(selectedCert).then(setBanks).catch(() => {})
  }, [selectedCert])

  const effectiveCount = custom ? parseInt(custom) : count

  async function startPractice() {
    if (!effectiveCount || effectiveCount < 1) {
      setError('Choose a valid question count.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const types = qType === 'all' ? null : [qType]
      let bankId = tab === 'dump' && selBank ? selBank : undefined
      let total  = effectiveCount

      if (tab === 'generate') {
        const generateResult = await ragAPI.generate({
          cert_id: selectedCert,
          topic: topic || undefined,
          count: effectiveCount,
          q_types: types,
        })
        bankId = generateResult.bank_id
        total  = generateResult.questions?.length || effectiveCount
      }

      // When we have a specific bank_id, don't pass extra filters
      const session = await examAPI.start({
        cert_id:      selectedCert,
        bank_id:      bankId,
        total,
        q_types:      bankId ? null : types,
        topic:        bankId ? undefined : (topic || undefined),
        session_type: 'practice',
      })
      navigate(`/exam/run/${session.session_id}`, { state: { session } })
    } catch (e) {
      setError(e.response?.data?.detail || 'Could not start practice session.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-2xl font-bold text-ink">Practice Mode</h1>
        <p className="text-sm text-muted mt-1">Choose your focus area and question source</p>
      </div>

      {/* Question Source — Generate vs Dump Bank */}
      <Card>
        <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Question Source
        </div>
        <div className="flex gap-1 p-1 bg-elevated rounded-xl mb-5">
          {[
            { key: 'generate', label: 'Generate Questions', icon: Sparkles },
            { key: 'dump',     label: 'From Dump Bank',     icon: Upload },
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition-all ${
                tab === key
                  ? 'bg-surface text-ink shadow-sm'
                  : 'text-muted hover:text-ink'
              }`}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>

        {tab === 'generate' && (
          <div className="space-y-5">
            <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-accent/5 border border-accent/15 text-xs text-accent-soft">
              <RefreshCw size={14} className="mt-0.5 shrink-0" />
              <div>
                <span className="font-semibold">Fresh questions every time</span>
                <span className="text-muted ml-1">— AI generates brand new questions. Explanations are pre-generated so they appear instantly.</span>
              </div>
            </div>
          </div>
        )}

        {tab === 'dump' && (
          <div className="space-y-3">
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">
              Select Question Bank
            </div>
            {banks.length === 0 ? (
              <div className="flex flex-col items-center py-8 text-center">
                <Upload size={28} className="text-muted mb-3" />
                <p className="text-sm text-muted">No dump banks uploaded yet.</p>
                <Button
                  variant="secondary"
                  size="sm"
                  className="mt-3"
                  onClick={() => navigate('/dumps')}
                >
                  Upload Dump PDF
                </Button>
              </div>
            ) : (
              banks.map(b => (
                <button
                  key={b.id}
                  onClick={() => setSelBank(b.id)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-sm transition-all ${
                    selBank === b.id
                      ? 'border-accent bg-accent/10 text-ink'
                      : 'border-border bg-elevated/40 text-muted hover:text-ink'
                  }`}
                >
                  <div className="text-left">
                    <div className="font-medium text-ink">{b.source_name}</div>
                    <div className="text-xs text-muted mt-0.5">{b.total_questions} questions extracted</div>
                  </div>
                  {selBank === b.id && <div className="w-2 h-2 rounded-full bg-accent-soft" />}
                </button>
              ))
            )}
          </div>
        )}
      </Card>

      {/* Topic selector */}
      <Card>
        <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
          Topic <span className="normal-case font-normal text-muted/60">(optional)</span>
        </div>
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            onClick={() => setTopic('')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              !topic ? 'border-accent bg-accent/15 text-accent-soft' : 'border-border text-muted hover:text-ink'
            }`}
          >
            All Topics
          </button>
          {topics.map(t => (
            <button
              key={t.topic}
              onClick={() => setTopic(t.topic)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                topic === t.topic ? 'border-accent bg-accent/15 text-accent-soft' : 'border-border text-muted hover:text-ink'
              }`}
            >
              {t.topic}
              <span className="ml-1.5 opacity-50">{t.count}</span>
            </button>
          ))}
        </div>
        <input
          type="text"
          value={topic}
          onChange={e => setTopic(e.target.value)}
          placeholder="Or type a specific topic..."
          className="w-full bg-elevated border border-border rounded-xl px-4 py-2.5 text-sm text-ink placeholder:text-muted outline-none focus:border-accent/50 transition-colors"
        />
      </Card>

      {/* Question type */}
      <Card>
        <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Question Type</div>
        <div className="grid grid-cols-2 gap-2">
          {QUESTION_TYPES.map(({ key, label, desc }) => (
            <button
              key={key}
              onClick={() => setQType(key)}
              className={`p-3 rounded-xl border text-left transition-all ${
                qType === key ? 'border-accent bg-accent/10' : 'border-border bg-elevated/40 hover:border-border/70'
              }`}
            >
              <div className={`text-sm font-semibold ${qType === key ? 'text-accent-soft' : 'text-ink'}`}>{label}</div>
              <div className="text-xs text-muted mt-0.5">{desc}</div>
            </button>
          ))}
        </div>
      </Card>

      {/* Question count */}
      <Card>
        <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Questions</div>
        <div className="grid grid-cols-4 gap-2 mb-3">
          {COUNTS.map(n => (
            <button
              key={n}
              onClick={() => { setCount(n); setCustom('') }}
              className={`py-3 rounded-xl text-sm font-semibold border transition-all ${
                count === n && !custom ? 'border-accent bg-accent/15 text-accent-soft' : 'border-border bg-elevated/40 text-muted hover:text-ink'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <input
          type="number"
          min="1"
          max="200"
          value={custom}
          onChange={e => { setCustom(e.target.value); setCount(0) }}
          placeholder="Custom number..."
          className="w-full bg-elevated border border-border rounded-xl px-4 py-2.5 text-sm text-ink placeholder:text-muted outline-none focus:border-accent/50 transition-colors font-mono"
        />
      </Card>

      {error && (
        <div className="px-4 py-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">{error}</div>
      )}

      <Button
        onClick={startPractice}
        disabled={loading || (tab === 'dump' && !selBank && banks.length > 0)}
        className="w-full"
        size="lg"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            {tab === 'generate' ? 'Generating questions...' : 'Preparing practice...'}
          </span>
        ) : (
          <>
            {tab === 'generate' ? <Sparkles size={18} /> : <Target size={18} />}
            {tab === 'generate'
              ? `Generate & Start · ${effectiveCount || '?'} Questions`
              : `Start Practice · ${effectiveCount || '?'} Questions`
            }
            <ChevronRight size={16} />
          </>
        )}
      </Button>
    </div>
  )
}

