import clsx from 'clsx'

const VARIANTS = {
  primary:   'bg-accent hover:bg-accent-soft text-white glow-accent',
  secondary: 'bg-elevated hover:bg-elevated/70 text-ink border border-border',
  ghost:     'bg-transparent hover:bg-elevated/50 text-muted hover:text-ink',
  danger:    'bg-danger/15 hover:bg-danger/25 text-danger border border-danger/30',
  success:   'bg-success/15 hover:bg-success/25 text-success border border-success/30',
}

const SIZES = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-6 py-3 text-base',
}

export default function Button({
  children, variant = 'primary', size = 'md',
  className, disabled, ...props
}) {
  return (
    <button
      disabled={disabled}
      className={clsx(
        'inline-flex items-center justify-center gap-2 rounded-xl font-semibold',
        'transition-all duration-150 active:scale-[0.98]',
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
