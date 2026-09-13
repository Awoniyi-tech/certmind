import { useState, useEffect, useRef } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Flag, Loader } from 'lucide-react'
import { examAPI, ragAPI } from '../lib/api.js'
import OptionButton from '../components/exam/OptionButton.jsx'
import ConfidenceSelector from '../components/exam/ConfidenceSelector.jsx'
import ExamTimer from '../components/exam/ExamTimer.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function ExamRunner() {
  const { sessionId } = useParams()
  const { state }     = useLocation()
  const navigate      = useNavigate()

  const session    = state?.session
  const [questions, setQuestions] = useState(session?.questions ?? [])
  const startTime  = useRef(Date.now())

  const [idx, setIdx]           = useState(0)
  const [answers, setAnswers]   = useState({})
  const [results, setResults]   = useState({})
  const [confidence, setConf]   = useState(null)
  const [multiSel, setMultiSel] = useState([])
  const [submitting, setSubmitting]       = useState(false)
  const [finishing, setFinishing]         = useState(false)
  const [sourceScope, setSourceScope]     = useState('official')
  const [explaining, setExplaining]       = useState(false)

  const q        = questions[idx]
  const total    = questions.length
  const answered = idx in answers
  const result   = results[idx]
  const isMultiple = q?.type === 'multiple'

  if (!session || !q) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted mb-4">No exam session found.</p>
          <Button onClick={() => navigate('/exam')}>Back to Setup</Button>
        </div>
      </div>
    )
  }

  async function submitAnswer(selected) {
    setSubmitting(true)
    try {
      const res = await examAPI.answer(sessionId, {
        question_id:  q.id,
        selected,
        confidence,
        time_taken_s: Math.floor((Date.now() - startTime.current) / 1000),
      })
      setAnswers(a => ({ ...a, [idx]: selected }))
      setResults(r => ({ ...r, [idx]: res }))
      setConf(null)
      setMultiSel([])

      setExplaining(true)
      try {
        const explanation = await ragAPI.explain({
          question: q.question,
          options: q.options,
          answer_key: q.answer_key,
          user_answer: selected,
          topic: q.topic,
          cert_id: q.cert_id || session.cert_id,
          attempt_id: res.attempt_id,
          source_scope: sourceScope,
        })
        setQuestions(current => current.map(item => item.id === q.id
          ? { ...item, explanation: explanation.explanation, sources: explanation.sources || [] }
          : item
        ))
      } finally {
        setExplaining(false)
      }
    } catch (e) {
      console.error('Submit failed', e)
    } finally {
      setSubmitting(false)
    }
  }

  async function finishExam() {
    setFinishing(true)
    try {
      const timeTaken = Math.floor((Date.now() - startTime.current) / 1000)
      const finishData = await examAPI.finish(sessionId, timeTaken)
      navigate(`/exam/results/${sessionId}`, {
        state: { timeTaken, total, answers, results, bankInfo: finishData.bank_info }
      })
    } finally {
      setFinishing(false)
    }
  }

  function getOptionState(opt) {
    const letter = opt[0].toUpperCase()
    if (!answered) return 'idle'
    const correctKey = Array.isArray(q.answer_key)
      ? q.answer_key.map(k => k.toUpperCase())
      : [q.answer_key.toUpperCase()]
    const userAns = Array.isArray(answers[idx])
      ? answers[idx].map(k => k.toUpperCase())
      : [String(answers[idx]).toUpperCase()]

    if (correctKey.includes(letter)) return 'correct'
    if (userAns.includes(letter))    return 'wrong'
    return 'neutral'
  }

  const correctCount = Object.values(results).filter(r => r?.is_correct).length
  const pct = answered ? Math.round(correctCount / (idx + 1) * 100) : null

  return (
    <div className="min-h-screen bg-void flex flex-col">
      {/* Top bar */}
      <div className="border-b border-border bg-surface/60 backdrop-blur-sm px-6 py-3 flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-muted font-mono">
          <span className="text-ink font-semibold">{idx + 1}</span>
          <span>/</span>
          <span>{total}</span>
        </div>

        {/* Progress dots */}
        <div className="flex-1 flex items-center gap-1 overflow-hidden">
          {questions.map((_, i) => (
            <button
              key={i}
              onClick={() => setIdx(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === idx
                  ? 'w-6 bg-accent'
                  : i in results
                    ? results[i]?.is_correct ? 'w-2 bg-success/70' : 'w-2 bg-danger/70'
                    : 'w-2 bg-border hover:bg-muted'
              }`}
            />
          ))}
        </div>

        <div className="flex items-center gap-3">
          {pct !== null && (
            <span className={`font-mono text-sm font-semibold ${
              pct >= 70 ? 'text-success' : pct >= 50 ? 'text-warning' : 'text-danger'
            }`}>
              {pct}%
            </span>
          )}
          <ExamTimer startTime={startTime.current} />
          <Button
            variant="ghost"
            size="sm"
            onClick={finishExam}
            disabled={finishing}
            className="text-muted gap-1.5"
          >
            <Flag size={14} />
            {finishing ? 'Finishing...' : 'Finish'}
          </Button>
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
          {/* Topic + type badge */}
          <div className="flex items-center gap-2">
            {q.topic && <Badge variant="accent">{q.topic}</Badge>}
            <Badge variant="default">
              {{ single: 'Single', multiple: 'Multiple', truefalse: 'True/False' }[q.type] ?? q.type}
            </Badge>
          </div>

          <div className="flex items-center justify-between gap-3 rounded-xl border border-border bg-elevated/30 px-4 py-3">
            <div><p className="text-xs font-semibold text-ink">Explanation sources</p><p className="text-[11px] text-muted mt-0.5">Choose what the AI coach may use.</p></div>
            <select value={sourceScope} onChange={e => setSourceScope(e.target.value)} className="bg-surface border border-border rounded-lg px-2.5 py-2 text-xs text-ink outline-none">
              <option value="official">Official knowledge</option>
              <option value="personal">My knowledge</option>
              <option value="both">Official + my knowledge</option>
            </select>
          </div>

          {/* Question */}
          <div className="bg-surface border border-border rounded-2xl p-6">
            <p className="text-base leading-relaxed text-ink">{q.question}</p>
          </div>

          {/* Multiple choice notice */}
          {isMultiple && !answered && (
            <p className="text-xs text-warning font-medium">
              ⚠ Select ALL correct answers, then click Submit.
            </p>
          )}

          {/* Options */}
          <div className="space-y-2.5">
            {q.options.map((opt) => {
              const letter = opt[0].toUpperCase()
              const state  = getOptionState(opt)
              const text   = opt.slice(2).trim()

              if (isMultiple && !answered) {
                return (
                  <button
                    key={opt}
                    onClick={() => setMultiSel(prev =>
                      prev.includes(letter)
                        ? prev.filter(l => l !== letter)
                        : [...prev, letter]
                    )}
                    className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl border text-sm font-medium transition-all text-left ${
                      multiSel.includes(letter)
                        ? 'border-accent bg-accent/10 text-ink'
                        : 'border-border bg-elevated/40 text-ink hover:border-accent/40 hover:bg-elevated'
                    }`}
                  >
                    <span className={`w-7 h-7 shrink-0 rounded-lg flex items-center justify-center text-xs font-bold font-mono ${
                      multiSel.includes(letter) ? 'bg-accent/25 text-accent-soft' : 'bg-elevated text-muted'
                    }`}>
                      {multiSel.includes(letter) ? '✓' : letter}
                    </span>
                    {text}
                  </button>
                )
              }

              return (
                <OptionButton
                  key={opt}
                  label={letter}
                  text={text}
                  state={state}
                  onClick={() => !answered && submitAnswer(letter)}
                  disabled={submitting || answered}
                />
              )
            })}
          </div>

          {/* Multiple submit */}
          {isMultiple && !answered && multiSel.length > 0 && (
            <Button
              className="w-full"
              onClick={() => submitAnswer(multiSel)}
              disabled={submitting}
            >
              {submitting ? 'Checking...' : `Submit (${multiSel.join(', ')})`}
            </Button>
          )}

          {/* Confidence selector — before answer */}
          {!answered && (
            <ConfidenceSelector value={confidence} onChange={setConf} />
          )}

          {/* Explanation — displays INSTANTLY because it's pre-loaded */}
          {answered && (
            <div className={`rounded-2xl border p-5 space-y-4 ${
              result?.is_correct
                ? 'border-success/30 bg-success/5'
                : 'border-danger/30 bg-danger/5'
            }`}>
              <div className={`font-display font-bold text-base ${
                result?.is_correct ? 'text-success' : 'text-danger'
              }`}>
                {result?.is_correct ? '✓ Correct' : '✗ Incorrect'}
                {!result?.is_correct && (
                  <span className="text-sm font-normal text-muted ml-2">
                    Correct: {Array.isArray(result?.correct_key)
                      ? result.correct_key.join(', ')
                      : result?.correct_key}
                  </span>
                )}
              </div>

              {q.explanation ? (
                <div className="text-sm text-ink/90 leading-relaxed whitespace-pre-wrap font-body">
                  {q.explanation}
                </div>
              ) : (
                <div className="text-sm text-warning/80 bg-warning/5 border border-warning/15 rounded-xl px-4 py-3">
                  <div className="font-medium mb-1">{explaining ? 'Generating grounded explanation...' : 'Explanation unavailable'}</div>
                  <div className="text-muted">
                    The correct answer is <span className="font-semibold text-ink">{Array.isArray(q.answer_key) ? q.answer_key.join(', ') : q.answer_key}</span>.
                    The system could not generate an explanation for this question at this time.
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bottom nav */}
      <div className="border-t border-border bg-surface/60 backdrop-blur-sm px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <Button
            variant="secondary"
            onClick={() => setIdx(i => Math.max(0, i - 1))}
            disabled={idx === 0}
          >
            <ChevronLeft size={16} /> Previous
          </Button>

          <div className="flex items-center gap-2">
            <span className="text-xs text-muted font-mono">
              {Object.keys(answers).length} / {total} answered
            </span>
          </div>

          {idx < total - 1 ? (
            <Button
              variant={answered ? 'primary' : 'secondary'}
              onClick={() => setIdx(i => i + 1)}
            >
              Next <ChevronRight size={16} />
            </Button>
          ) : (
            <Button onClick={finishExam} disabled={finishing}>
              {finishing ? 'Finishing...' : 'Finish Exam'}
              <Flag size={16} />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

