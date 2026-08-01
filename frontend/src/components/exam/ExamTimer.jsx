import { useState, useEffect } from 'react'
import { Clock } from 'lucide-react'
import clsx from 'clsx'

export default function ExamTimer({ startTime, warningAt = 300 }) {
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [startTime])

  const mins = Math.floor(elapsed / 60)
  const secs = elapsed % 60
  const isWarning = elapsed > warningAt

  return (
    <div className={clsx(
      'flex items-center gap-1.5 font-mono text-sm font-medium px-3 py-1.5 rounded-lg',
      isWarning ? 'text-warning bg-warning/10' : 'text-muted bg-elevated/50'
    )}>
      <Clock size={14} />
      {String(mins).padStart(2, '0')}:{String(secs).padStart(2, '0')}
    </div>
  )
}
