import clsx from 'clsx'

export default function Card({ children, className, hover = false, ...props }) {
  return (
    <div
      className={clsx(
        'bg-surface border border-border rounded-2xl p-5',
        hover && 'card-hover',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
