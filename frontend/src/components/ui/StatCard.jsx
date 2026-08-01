import clsx from 'clsx'
import Card from './Card.jsx'

export default function StatCard({ label, value, sublabel, trend, icon: Icon, accentColor = 'accent' }) {
  const colorMap = {
    accent:  'text-accent-soft bg-accent/10',
    success: 'text-success bg-success/10',
    danger:  'text-danger bg-danger/10',
    warning: 'text-warning bg-warning/10',
  }

  return (
    <Card hover className="animate-fade-in">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-muted uppercase tracking-wider">{label}</span>
        {Icon && (
          <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center', colorMap[accentColor])}>
            <Icon size={15} strokeWidth={2} />
          </div>
        )}
      </div>
      <div className="font-display text-3xl font-bold text-ink mb-1">{value}</div>
      {sublabel && (
        <div className="flex items-center gap-1.5 text-xs">
          {trend !== undefined && (
            <span className={clsx('font-semibold', trend >= 0 ? 'text-success' : 'text-danger')}>
              {trend >= 0 ? '+' : ''}{trend}%
            </span>
          )}
          <span className="text-muted">{sublabel}</span>
        </div>
      )}
    </Card>
  )
}
