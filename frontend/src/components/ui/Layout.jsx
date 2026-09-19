import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, BookOpen, Target, Timer, XCircle,
  MessageSquare, BarChart3, Upload, Zap, LogOut, BookMarked, ClipboardCheck, FlaskConical, Activity
} from 'lucide-react'
import { useStore } from '../../store/useStore.js'
import { useAuthStore } from '../../store/authStore.js'

const NAV_ITEMS = [
  { to: '/',               icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/learn',          icon: BookOpen,        label: 'Learn' },
  { to: '/practice',       icon: Target,          label: 'Practice' },
  { to: '/exam',           icon: Timer,           label: 'Exam Simulation' },
  { to: '/wrong-questions',icon: XCircle,         label: 'Wrong Questions' },
  { to: '/tutor',          icon: MessageSquare,   label: 'AI Tutor' },
  { to: '/analytics',      icon: BarChart3,       label: 'Analytics' },
  { to: '/dumps',          icon: Upload,          label: 'Dump Manager' },
  { to: '/knowledge',      icon: BookMarked,      label: 'Personal Knowledge' },
  { to: '/evaluations',    icon: ClipboardCheck,  label: 'Evaluation Lab' },
  { to: '/experiments',    icon: FlaskConical,    label: 'Experiment Lab' },
  { to: '/observability',  icon: Activity,        label: 'Observability' },
]

export default function Layout({ children }) {
  const { selectedCert, setCert, certifications } = useStore()
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()
  const isExamRunning = location.pathname.startsWith('/exam/run')

  function handleLogout() {
    logout()
    navigate('/login')
  }

  if (isExamRunning) {
    return <div className="min-h-screen bg-void">{children}</div>
  }

  // Get initials for avatar
  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?'

  return (
    <div className="h-screen overflow-hidden bg-void flex">
      {/* Sidebar */}
      <aside className="h-full w-64 shrink-0 border-r border-border bg-surface/40 backdrop-blur-sm flex flex-col min-h-0">
        <div className="px-6 py-6 border-b border-border">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-cyan-400 flex items-center justify-center">
              <Zap size={16} className="text-white" strokeWidth={2.5} />
            </div>
            <span className="font-display font-bold text-lg tracking-tight">
              Cert<span className="gradient-text">Mind</span>
            </span>
          </div>
        </div>

        {/* User profile section */}
        {user && (
          <div className="px-3 pt-4 pb-2">
            <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-elevated/40 border border-border/50">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent/80 to-cyan-500/80 flex items-center justify-center shrink-0">
                <span className="text-[11px] font-bold text-white">{initials}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-ink truncate">{user.name}</div>
                <div className="text-[10px] text-muted truncate">{user.email}</div>
              </div>
            </div>
          </div>
        )}

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-accent/15 text-accent-soft border border-accent/20'
                    : 'text-muted hover:text-ink hover:bg-elevated/60'
                }`
              }
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 space-y-2 border-t border-border">
          {/* Certification selector */}
          <div className="px-3 py-2.5 rounded-lg bg-elevated/50 border border-border">
            <div className="text-[10px] uppercase tracking-wider text-muted font-semibold mb-1.5">
              Active Certification
            </div>
            <select
              value={selectedCert}
              onChange={(e) => setCert(e.target.value)}
              className="w-full bg-transparent text-sm font-medium text-ink outline-none cursor-pointer"
            >
              {certifications.map(c => (
                <option key={c.id} value={c.id} className="bg-elevated">
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Logout button */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-muted hover:text-danger hover:bg-danger/10 transition-all"
          >
            <LogOut size={17} strokeWidth={2} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-h-0 overflow-y-auto">
        <div className="max-w-[1400px] mx-auto px-8 py-7">
          {children}
        </div>
      </main>
    </div>
  )
}

