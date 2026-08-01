import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, Cell } from 'recharts'
import { analyticsAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import StatCard from '../components/ui/StatCard.jsx'
import Badge from '../components/ui/Badge.jsx'
import { TrendingUp, Target, XCircle, Timer } from 'lucide-react'

const TOOLTIP_STYLE = {
  contentStyle: { background: '#0D1B2A', border: '1px solid #1E2D45', borderRadius: 12, fontSize: 12 },
  labelStyle:   { color: '#94A3B8' },
  itemStyle:    { color: '#F1F5F9' },
}

export default function Analytics() {
  const { selectedCert } = useStore()
  const [overview, setOverview]   = useState(null)
  const [topics, setTopics]       = useState({ all: [], weak: [], strong: [] })
  const [trend, setTrend]         = useState([])
  const [confidence, setConf]     = useState([])
  const [history, setHistory]     = useState([])
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      analyticsAPI.overview(selectedCert),
      analyticsAPI.topics(selectedCert),
      analyticsAPI.trend(selectedCert),
      analyticsAPI.confidence(selectedCert),
      analyticsAPI.history(selectedCert),
    ]).then(([ov, tp, tr, cf, hi]) => {
      setOverview(ov)
      setTopics(tp)
      setTrend(tr.map((d, i) => ({ ...d, name: `Exam ${i + 1}` })))
      setConf(cf)
      setHistory(hi)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [selectedCert])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
    </div>
  )

  const topicChartData = topics.all?.slice(0, 12).map(t => ({
    topic:    t.topic?.length > 8 ? t.topic.slice(0, 8) + '…' : t.topic,
    accuracy: t.accuracy,
    total:    t.total,
  })) ?? []

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-2xl font-bold text-ink">Analytics</h1>
        <p className="text-sm text-muted mt-1">Your performance insights</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total Exams"   value={overview?.total_exams ?? 0}        icon={Timer}      accentColor="accent"  />
        <StatCard label="Average Score" value={`${overview?.avg_score ?? 0}%`}     icon={TrendingUp} accentColor="success" />
        <StatCard label="Best Score"    value={`${overview?.best_score ?? 0}%`}    icon={Target}     accentColor="success" />
        <StatCard label="Wrong Q's"     value={overview?.wrong_count ?? 0}         icon={XCircle}    accentColor="danger"  />
      </div>

      {/* Trend line */}
      {trend.length > 1 && (
        <Card>
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Score Trend</h2>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={trend} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [`${v}%`, 'Score']} />
              <defs>
                <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%"   stopColor="#06B6D4" />
                  <stop offset="100%" stopColor="#3B82F6" />
                </linearGradient>
              </defs>
              <Line
                type="monotone" dataKey="score"
                stroke="url(#lineGrad)" strokeWidth={2.5}
                dot={{ fill: '#3B82F6', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Topic accuracy */}
      {topicChartData.length > 0 && (
        <Card>
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Topic Accuracy</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topicChartData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <XAxis dataKey="topic" tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748B', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [`${v}%`, 'Accuracy']} />
              <Bar dataKey="accuracy" radius={[6, 6, 0, 0]}>
                {topicChartData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.accuracy >= 70 ? '#10B981' : entry.accuracy >= 50 ? '#F59E0B' : '#EF4444'}
                    fillOpacity={0.85}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weak topics */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-sm text-ink">Weak Areas</h2>
            <Badge variant="danger">Need Focus</Badge>
          </div>
          {topics.weak?.length > 0 ? (
            <div className="space-y-3">
              {topics.weak.map(t => (
                <div key={t.topic}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-ink">{t.topic}</span>
                    <span className="text-danger">{t.accuracy}%</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-elevated overflow-hidden">
                    <div className="h-full bg-danger rounded-full" style={{ width: `${t.accuracy}%` }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted py-4 text-center">No weak areas detected yet.</p>
          )}
        </Card>

        {/* Confidence analysis */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-sm text-ink">Confidence vs Accuracy</h2>
          </div>
          {confidence.length > 0 ? (
            <div className="space-y-4">
              {confidence.map(c => (
                <div key={c.confidence}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="capitalize font-medium text-ink">{c.confidence} Confidence</span>
                    <span className={c.accuracy >= 70 ? 'text-success' : 'text-warning'}>
                      {c.accuracy}% · {c.total} answers
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-elevated overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        c.confidence === 'high' ? 'bg-success' :
                        c.confidence === 'medium' ? 'bg-accent' : 'bg-warning'
                      }`}
                      style={{ width: `${c.accuracy}%` }}
                    />
                  </div>
                </div>
              ))}
              <p className="text-xs text-muted mt-2">
                High confidence + wrong answer = dangerous misconception. Study those topics first.
              </p>
            </div>
          ) : (
            <p className="text-sm text-muted py-4 text-center">Use confidence tracking during exams to see this data.</p>
          )}
        </Card>
      </div>

      {/* Exam history */}
      {history.length > 0 && (
        <Card>
          <h2 className="font-display font-semibold text-sm text-ink mb-4">Exam History</h2>
          <div className="space-y-2">
            {history.map(s => {
              const score = s.score ?? 0
              const color = score >= 70 ? 'text-success' : score >= 50 ? 'text-warning' : 'text-danger'
              const mins  = Math.floor((s.time_taken_s ?? 0) / 60)
              return (
                <div key={s.id} className="flex items-center justify-between px-4 py-3 rounded-xl bg-elevated/40 border border-border">
                  <div>
                    <div className="text-sm font-medium text-ink">
                      {s.session_type === 'exam' ? 'Exam Simulation' : 'Practice'}
                    </div>
                    <div className="text-xs text-muted">
                      {new Date(s.started_at).toLocaleDateString()} · {s.total_questions}Q · {mins}m
                    </div>
                  </div>
                  <span className={`font-display font-bold text-xl ${color}`}>{score}%</span>
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}
