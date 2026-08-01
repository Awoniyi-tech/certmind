import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts'

export default function AccuracyPulse({ data = [], height = 60 }) {
  const chartData = data.length > 0
    ? data.map((d, i) => ({ i, score: d.score }))
    : [{ i: 0, score: 0 }, { i: 1, score: 0 }]

  return (
    <div className="relative" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 4, right: 0, bottom: 4, left: 0 }}>
          <YAxis domain={[0, 100]} hide />
          <defs>
            <linearGradient id="pulseGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%"   stopColor="#06B6D4" />
              <stop offset="100%" stopColor="#3B82F6" />
            </linearGradient>
          </defs>
          <Line
            type="monotone"
            dataKey="score"
            stroke="url(#pulseGradient)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
            animationDuration={1200}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
