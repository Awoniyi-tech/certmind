import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { XCircle, RotateCcw, Target, ChevronDown, ChevronUp } from 'lucide-react'
import { questionsAPI, examAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function WrongQuestions() {
  const navigate = useNavigate()
  const { selectedCert } = useStore()
  const [questions, setQuestions] = useState([])
  const [loading, setLoading]     = useState(true)
  const [starting, setStarting]   = useState(false)
  const [expanded, setExpanded]   = useState(null)

  useEffect(() => {
    questionsAPI.wrong(selectedCert)
      .then(setQuestions)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [selectedCert])

  const topicMap = {}
  questions.forEach(q => {
    const t = q.topic || 'General'
    if (!topicMap[t]) topicMap[t] = []
    topicMap[t].push(q)
  })
  const topicEntries = Object.entries(topicMap).sort((a, b) => b[1].length - a[1].length)

  async function practiceAll() {
    setStarting(true)
    try {
      const session = await examAPI.start({
        cert_id:      selectedCert,
        total:        Math.min(questions.length, 60),
        session_type: 'practice',
        topic:        undefined,
      })
      navigate(`/exam/run/${session.session_id}`, { state: { session } })
    } catch {
      setStarting(false)
    }
  }

  async function practiceTopic(topic) {
    setStarting(true)
    try {
      const session = await examAPI.start({
        cert_id:      selectedCert,
        total:        topicMap[topic].length,
        topic,
        session_type: 'practice',
      })
      navigate(`/exam/run/${session.session_id}`, { state: { session } })
    } catch {
      setStarting(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Wrong Questions</h1>
          <p className="text-sm text-muted mt-1">
            {questions.length} question{questions.length !== 1 ? 's' : ''} to review
          </p>
        </div>
        {questions.length > 0 && (
          <Button onClick={practiceAll} disabled={starting}>
            <RotateCcw size={15} />
            {starting ? 'Starting...' : `Practice All (${questions.length})`}
          </Button>
        )}
      </div>

      {questions.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-14 h-14 rounded-2xl bg-success/10 flex items-center justify-center mb-4">
            <Target size={24} className="text-success" />
          </div>
          <h2 className="font-display font-bold text-ink mb-2">Clean Slate</h2>
          <p className="text-sm text-muted max-w-xs">
            No wrong questions yet. Complete some exams and your missed questions will appear here.
          </p>
          <Button className="mt-6" onClick={() => navigate('/exam')}>
            Start an Exam
          </Button>
        </Card>
      ) : (
        <>
          {/* Topic breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {topicEntries.map(([topic, qs]) => (
              <Card
                key={topic}
                hover
                className="cursor-pointer"
                onClick={() => practiceTopic(topic)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="w-8 h-8 rounded-lg bg-danger/10 flex items-center justify-center">
                    <XCircle size={15} className="text-danger" />
                  </div>
                  <Badge variant="danger">{qs.length}</Badge>
                </div>
                <div className="font-semibold text-sm text-ink">{topic}</div>
                <div className="text-xs text-muted mt-1">
                  {qs.length} question{qs.length !== 1 ? 's' : ''} wrong
                </div>
                <div className="mt-3 text-xs text-accent-soft font-medium">
                  Practice →
                </div>
              </Card>
            ))}
          </div>

          {/* Question list */}
          <Card>
            <h2 className="font-display font-semibold text-sm text-ink mb-4">All Wrong Questions</h2>
            <div className="space-y-2">
              {questions.map((q, i) => (
                <div key={q.id} className="rounded-xl bg-elevated/40 border border-border overflow-hidden">
                  <button
                    onClick={() => setExpanded(expanded === i ? null : i)}
                    className="w-full flex items-start gap-3 p-3 text-left"
                  >
                    <div className="w-6 h-6 rounded-full bg-danger/15 flex items-center justify-center shrink-0 mt-0.5">
                      <XCircle size={12} className="text-danger" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-ink leading-relaxed line-clamp-2">{q.question}</p>
                      <div className="flex items-center gap-2 mt-1.5">
                        {q.topic && <Badge variant="default">{q.topic}</Badge>}
                        <span className="text-xs text-muted">
                          Wrong {q.times_wrong}x
                        </span>
                      </div>
                    </div>
                    <div className="shrink-0 mt-0.5">
                      {expanded === i ? <ChevronUp size={14} className="text-muted" /> : <ChevronDown size={14} className="text-muted" />}
                    </div>
                  </button>

                  {expanded === i && (
                    <div className="px-4 pb-4 space-y-3 border-t border-border/50 pt-3">
                      <div className="space-y-1.5">
                        {q.options?.map(opt => {
                          const letter = opt[0].toUpperCase()
                          const correctKeys = Array.isArray(q.answer_key)
                            ? q.answer_key.map(k => k.toUpperCase())
                            : [String(q.answer_key).toUpperCase()]
                          const isCorrect = correctKeys.includes(letter)
                          return (
                            <div
                              key={opt}
                              className={`text-xs px-3 py-2 rounded-lg ${
                                isCorrect ? 'bg-success/10 text-success' : 'text-muted'
                              }`}
                            >
                              {opt}
                            </div>
                          )
                        })}
                      </div>

                      <div className="flex gap-4 text-xs">
                        {q.last_selected && (
                          <span className="text-muted">Your answer:
                            <span className="ml-1 font-semibold text-danger">
                              {Array.isArray(q.last_selected) ? q.last_selected.join(', ') : q.last_selected}
                            </span>
                          </span>
                        )}
                        <span className="text-muted">Correct:
                          <span className="ml-1 font-semibold text-success">
                            {Array.isArray(q.answer_key) ? q.answer_key.join(', ') : q.answer_key}
                          </span>
                        </span>
                      </div>

                      {q.explanation ? (
                        <div className="text-xs text-muted leading-relaxed bg-elevated rounded-lg p-3">
                          {formatAIText(q.explanation)}
                        </div>
                      ) : (
                        <div className="text-xs text-muted italic">
                          No explanation available for this question yet.
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}