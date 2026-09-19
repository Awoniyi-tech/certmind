import { useEffect, useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { Trophy, XCircle, RotateCcw, BarChart3, ChevronDown, ChevronUp, Save, Check } from 'lucide-react'
import { examAPI, dumpsAPI } from '../lib/api.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function ExamResults() {
  const { sessionId } = useParams()
  const navigate      = useNavigate()
  const location      = useLocation()
  const [replay, setReplay]   = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  
  const bankInfo = location.state?.bankInfo
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    examAPI.replay(sessionId).then(setReplay).catch(() => {}).finally(() => setLoading(false))
  }, [sessionId])

  const correct = replay.filter(r => r.is_correct).length
  const total   = replay.length
  const score   = total > 0 ? Math.round(correct / total * 100) : 0
  const passed  = score >= 70

  const topicMap = {}
  replay.forEach(r => {
    if (!r.topic) return
    if (!topicMap[r.topic]) topicMap[r.topic] = { correct: 0, total: 0 }
    topicMap[r.topic].total++
    if (r.is_correct) topicMap[r.topic].correct++
  })
  const topicStats = Object.entries(topicMap).map(([topic, s]) => ({
    topic, ...s, accuracy: Math.round(s.correct / s.total * 100)
  })).sort((a, b) => a.accuracy - b.accuracy)

  async function handleSaveBank() {
    if (!bankInfo?.bank_id) return
    setSaving(true)
    try {
      await dumpsAPI.save(bankInfo.bank_id)
      setSaved(true)
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Score hero */}
      <Card className="text-center py-10 relative">
        {bankInfo?.source_type === 'generated' && (
          <div className="absolute top-4 right-4">
            <Button 
              variant={saved ? "success" : "secondary"} 
              size="sm" 
              onClick={handleSaveBank}
              disabled={saved || saving}
              className={saved ? "bg-success/20 text-success border-success/30" : ""}
            >
              {saving ? (
                <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : saved ? (
                <><Check size={14} /> Saved to Dump Manager</>
              ) : (
                <><Save size={14} /> Save to My Bank</>
              )}
            </Button>
          </div>
        )}
        <div className={`font-display text-7xl font-bold mb-2 ${passed ? 'text-success' : 'text-danger'}`}>
          {score}%
        </div>
        <div className="flex items-center justify-center gap-3 mb-6">
          <Badge variant={passed ? 'success' : 'danger'}>
            {passed ? '✓ Pass' : '✗ Fail'}
          </Badge>
          <span className="text-sm text-muted">{correct} / {total} correct</span>
        </div>
        <div className="flex items-center justify-center gap-3">
          <Button variant="secondary" onClick={() => navigate('/exam')}>
            <RotateCcw size={15} /> New Exam
          </Button>
          <Button variant="secondary" onClick={() => navigate('/analytics')}>
            <BarChart3 size={15} /> View Analytics
          </Button>
          <Button onClick={() => navigate('/wrong-questions')}>
            <XCircle size={15} /> Review Wrong
          </Button>
        </div>
      </Card>

      {/* Topic breakdown */}
      {topicStats.length > 0 && (
        <Card>
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Topic Breakdown</h2>
          <div className="space-y-3">
            {topicStats.map(t => (
              <div key={t.topic}>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="font-medium text-ink">{t.topic}</span>
                  <span className={t.accuracy >= 70 ? 'text-success' : t.accuracy >= 50 ? 'text-warning' : 'text-danger'}>
                    {t.correct}/{t.total} · {t.accuracy}%
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-elevated overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      t.accuracy >= 70 ? 'bg-success' : t.accuracy >= 50 ? 'bg-warning' : 'bg-danger'
                    }`}
                    style={{ width: `${t.accuracy}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Question replay */}
      <Card>
        <h2 className="font-display font-semibold text-sm text-ink mb-4">
          Question Replay
        </h2>
        <div className="space-y-2">
          {replay.map((item, i) => (
            <div key={i} className={`rounded-xl border transition-all ${
              item.is_correct ? 'border-success/20' : 'border-danger/20'
            }`}>
              <button
                onClick={() => setExpanded(expanded === i ? null : i)}
                className="w-full flex items-center gap-3 px-4 py-3 text-left"
              >
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                  item.is_correct ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'
                }`}>
                  {item.is_correct ? '✓' : '✗'}
                </span>
                <span className="flex-1 text-sm text-ink line-clamp-1">{item.question}</span>
                <div className="flex items-center gap-2 shrink-0">
                  {item.topic && <Badge variant="default">{item.topic}</Badge>}
                  {expanded === i ? <ChevronUp size={14} className="text-muted" /> : <ChevronDown size={14} className="text-muted" />}
                </div>
              </button>
              {expanded === i && (
                <div className="px-4 pb-4 space-y-3 border-t border-border/50 pt-3">
                  <div className="flex gap-4 text-xs">
                    <span className="text-muted">Your answer:
                      <span className={`ml-1 font-semibold ${item.is_correct ? 'text-success' : 'text-danger'}`}>
                        {Array.isArray(item.selected) ? item.selected.join(', ') : item.selected}
                      </span>
                    </span>
                    {!item.is_correct && (
                      <span className="text-muted">Correct:
                        <span className="ml-1 font-semibold text-success">
                          {Array.isArray(item.answer_key) ? item.answer_key.join(', ') : item.answer_key}
                        </span>
                      </span>
                    )}
                  </div>
                  {item.explanation && (
                    <div className="text-xs text-muted leading-relaxed bg-elevated rounded-lg p-3">
                      {formatAIText(item.explanation)}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
