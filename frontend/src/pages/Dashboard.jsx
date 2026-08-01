import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Timer, Target, XCircle, TrendingUp, BookOpen, ChevronRight, Zap, Flame } from 'lucide-react'
import { analyticsAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import StatCard from '../components/ui/StatCard.jsx'
import AccuracyPulse from '../components/ui/AccuracyPulse.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function Dashboard() {
  const { selectedCert, certifications } = useStore()
  const navigate = useNavigate()
  const [overview, setOverview] = useState(null)
  const [trend, setTrend] = useState([])
  const [topics, setTopics] = useState({ weak: [], strong: [] })
  const [recommendations, setRecommendations] = useState({ study_now: [] })
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  const cert = certifications.find(c => c.id === selectedCert)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      analyticsAPI.overview(selectedCert),
      analyticsAPI.trend(selectedCert),
      analyticsAPI.topics(selectedCert),
      analyticsAPI.recommendations(selectedCert),
      analyticsAPI.history(selectedCert),
    ]).then(([ov, tr, tp, rec, hist]) => {
      setOverview(ov)
      setTrend(tr)
      setTopics(tp)
      setRecommendations(rec)
      setHistory(hist.slice(0, 5))
    }).catch(() => { }).finally(() => setLoading(false))
  }, [selectedCert])

  const latestScore = trend.length > 0 ? trend[trend.length - 1]?.score : null
  const scoreColor = latestScore >= 70 ? 'text-success' : latestScore >= 50 ? 'text-warning' : 'text-danger'

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Dashboard</h1>
          <p className="text-sm text-muted mt-1">
            {cert?.vendor} · {cert?.name}
          </p>
        </div>
        <Button onClick={() => navigate('/exam')} className="gap-2">
          <Timer size={16} />
          Start Exam
        </Button>
      </div>

      {/* Accuracy Pulse Card */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-xs text-muted uppercase tracking-wider font-semibold mb-1">
              Performance Trend
            </div>
            {latestScore !== null ? (
              <div className={`font-display text-4xl font-bold ${scoreColor}`}>
                {latestScore}%
                <span className="text-base text-muted font-normal ml-2">latest exam</span>
              </div>
            ) : (
              <div className="font-display text-2xl font-semibold text-muted">No exams yet</div>
            )}
          </div>
          <div className="text-right">
            <div className="text-xs text-muted mb-1">Avg score</div>
            <div className="font-display text-xl font-bold text-ink">
              {overview?.avg_score ?? '—'}%
            </div>
          </div>
        </div>
        <AccuracyPulse data={trend} height={72} />
      </Card>

      {/* Stat row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Exams Taken"
          value={overview?.total_exams ?? 0}
          sublabel="total sessions"
          icon={Timer}
          accentColor="accent"
        />
        <StatCard
          label="Best Score"
          value={`${overview?.best_score ?? 0}%`}
          sublabel="personal best"
          icon={TrendingUp}
          accentColor="success"
        />
        <StatCard
          label="Wrong Questions"
          value={overview?.wrong_count ?? 0}
          sublabel="need review"
          icon={XCircle}
          accentColor="danger"
        />
        <StatCard
          label="Study Streak"
          value={`${overview?.study_streak ?? 0}d`}
          sublabel="consecutive days"
          icon={Flame}
          accentColor="warning"
        />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick actions */}
        <Card className="lg:col-span-1">
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Quick Actions</h2>
          <div className="space-y-2">
            {[
              { label: 'Start Exam Simulation', sub: 'Full exam experience', path: '/exam', icon: Timer, color: 'text-accent-soft' },
              { label: 'Practice Mode', sub: 'Choose topic & type', path: '/practice', icon: Target, color: 'text-success' },
              { label: 'Wrong Questions', sub: `${overview?.wrong_count ?? 0} to review`, path: '/wrong-questions', icon: XCircle, color: 'text-danger' },
              { label: 'AI Tutor', sub: 'Ask anything', path: '/tutor', icon: Zap, color: 'text-warning' },
              { label: 'Learn Topics', sub: 'Study materials', path: '/learn', icon: BookOpen, color: 'text-accent-soft' },
            ].map(({ label, sub, path, icon: Icon, color }) => (
              <button
                key={path}
                onClick={() => navigate(path)}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-elevated transition-all text-left group"
              >
                <div className={`w-8 h-8 rounded-lg bg-elevated flex items-center justify-center ${color}`}>
                  <Icon size={15} strokeWidth={2} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-ink">{label}</div>
                  <div className="text-xs text-muted">{sub}</div>
                </div>
                <ChevronRight size={14} className="text-muted group-hover:text-ink transition-colors" />
              </button>
            ))}
          </div>
        </Card>

        {/* Weak areas + recommendations */}
        <Card className="lg:col-span-1">
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Focus Areas</h2>
          {topics?.weak?.length > 0 ? (
            <div className="space-y-3">
              {topics.weak.slice(0, 5).map(t => (
                <div key={t.topic}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-ink font-medium">{t.topic}</span>
                    <span className={t.accuracy < 50 ? 'text-danger' : 'text-warning'}>
                      {t.accuracy}%
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-elevated overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${t.accuracy < 50 ? 'bg-danger' : 'bg-warning'}`}
                      style={{ width: `${t.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
              <Button
                variant="ghost"
                size="sm"
                className="w-full mt-2"
                onClick={() => navigate('/practice')}
              >
                Practice Weak Topics
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Target size={32} className="text-muted mb-3" />
              <p className="text-sm text-muted">No weak areas yet.</p>
              <p className="text-xs text-muted mt-1">Complete some exams to see insights.</p>
            </div>
          )}
        </Card>

        {/* Recent sessions */}
        <Card className="lg:col-span-1">
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Recent Exams</h2>
          {history.length > 0 ? (
            <div className="space-y-2">
              {history.map(s => {
                const score = s.score ?? 0
                const color = score >= 70 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-danger'
                const date = new Date(s.started_at).toLocaleDateString()
                const mins = Math.floor((s.time_taken_s ?? 0) / 60)
                return (
                  <button
                    key={s.id}
                    onClick={() => navigate(`/exam/results/${s.id}`)}
                    className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-elevated transition-all group"
                  >
                    <div className="text-left">
                      <div className="text-sm font-medium text-ink">{s.session_type === 'exam' ? 'Exam Simulation' : 'Practice'}</div>
                      <div className="text-xs text-muted">{date} · {s.total_questions}Q · {mins}m</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`font-display font-bold text-lg ${color}`}>{score}%</span>
                      <ChevronRight size={14} className="text-muted group-hover:text-ink" />
                    </div>
                  </button>
                )
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Timer size={32} className="text-muted mb-3" />
              <p className="text-sm text-muted">No exams yet.</p>
              <Button size="sm" className="mt-3" onClick={() => navigate('/exam')}>
                Start First Exam
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* Study recommendations */}
      {recommendations?.study_now?.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-sm text-ink">AI Recommendations</h2>
            <Badge variant="accent">Study Now</Badge>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {recommendations.study_now.map((r, i) => (
              <button
                key={r.topic}
                onClick={() => navigate(`/learn?topic=${encodeURIComponent(r.topic)}`)}
                className="flex items-center gap-3 p-3 rounded-xl bg-elevated hover:bg-elevated/70 border border-border hover:border-accent/30 transition-all text-left"
              >
                <div className="w-6 h-6 rounded-md bg-accent/15 text-accent-soft font-bold text-xs flex items-center justify-center font-mono">
                  {i + 1}
                </div>
                <div>
                  <div className="text-sm font-medium text-ink">{r.topic}</div>
                  <div className="text-xs text-danger">{r.accuracy}% accuracy</div>
                </div>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
