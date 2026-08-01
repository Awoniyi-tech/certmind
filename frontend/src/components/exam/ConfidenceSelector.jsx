import clsx from 'clsx'

const LEVELS = [
  { key: 'low',    label: 'Low',    color: 'border-warning/40 text-warning' },
  { key: 'medium', label: 'Medium', color: 'border-accent/40 text-accent-soft' },
  { key: 'high',   label: 'High',   color: 'border-success/40 text-success' },
]

export default function ConfidenceSelector({ value, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted font-medium mr-1">Confidence:</span>
      {LEVELS.map(({ key, label, color }) => (
        <button
          key={key}
          onClick={() => onChange(key)}
          className={clsx(
            'px-3 py-1 rounded-full text-xs font-semibold border transition-all',
            value === key
              ? clsx(color, 'bg-elevated')
              : 'border-border text-muted hover:text-ink'
          )}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
