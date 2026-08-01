import clsx from 'clsx'

const VARIANTS = {
  default: 'bg-elevated text-muted border-border',
  accent:  'bg-accent/15 text-accent-soft border-accent/30',
  success: 'bg-success/15 text-success border-success/30',
  danger:  'bg-danger/15 text-danger border-danger/30',
  warning: 'bg-warning/15 text-warning border-warning/30',
}

export default function Badge({ children, variant = 'default', className }) {
  return (
    <span className={clsx(
      'inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wide border',
      VARIANTS[variant],
      className
    )}>
      {children}
    </span>
  )
}
