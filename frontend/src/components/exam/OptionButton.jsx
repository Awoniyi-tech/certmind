import clsx from 'clsx'

export default function OptionButton({ label, text, state = 'idle', onClick, disabled }) {
  const styles = {
    idle:     'border-border bg-elevated/40 text-ink hover:border-accent/40 hover:bg-elevated',
    correct:  'border-success bg-success/10 text-success',
    wrong:    'border-danger bg-danger/10 text-danger',
    neutral:  'border-border bg-surface text-muted',
    selected: 'border-accent bg-accent/10 text-accent-soft',
  }

  const icons = { correct: '✓', wrong: '✗', idle: '', neutral: '', selected: '' }

  return (
    <button
      onClick={onClick}
      disabled={disabled || state !== 'idle'}
      className={clsx(
        'w-full flex items-center gap-3 px-4 py-3.5 rounded-xl border text-sm font-medium',
        'transition-all duration-150 text-left',
        state === 'idle' && !disabled && 'active:scale-[0.99] cursor-pointer',
        disabled && state === 'idle' && 'opacity-50 cursor-not-allowed',
        styles[state]
      )}
    >
      <span className={clsx(
        'w-7 h-7 shrink-0 rounded-lg flex items-center justify-center text-xs font-bold font-mono',
        state === 'correct' ? 'bg-success/20 text-success' :
        state === 'wrong'   ? 'bg-danger/20 text-danger' :
        'bg-elevated text-muted'
      )}>
        {icons[state] || label}
      </span>
      <span className="flex-1">{text}</span>
    </button>
  )
}
