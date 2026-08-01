import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, Mail, Lock, User, ArrowRight, Eye, EyeOff, Loader } from 'lucide-react'
import { useAuthStore } from '../store/authStore.js'

export default function Login() {
  const navigate = useNavigate()
  const { login, register } = useAuthStore()

  const [mode, setMode]         = useState('login')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [name, setName]         = useState('')
  const [showPw, setShowPw]     = useState(false)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mode === 'register') {
        await register(email, password, name)
      } else {
        await login(email, password)
      }
      navigate('/')
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-void flex">
      {/* Left — branding panel */}
      <div className="hidden lg:flex lg:w-[45%] relative overflow-hidden">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#0f1724] via-[#131d30] to-[#0a1628]" />

        {/* Glowing orbs */}
        <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] rounded-full bg-accent/8 blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-cyan-500/6 blur-[100px]" />

        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '60px 60px'
          }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-cyan-400 flex items-center justify-center shadow-lg shadow-accent/20">
              <Zap size={20} className="text-white" strokeWidth={2.5} />
            </div>
            <span className="font-display font-bold text-2xl tracking-tight text-white">
              Cert<span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-cyan-400">Mind</span>
            </span>
          </div>

          <div className="max-w-md">
            <h1 className="font-display text-4xl font-bold text-white leading-tight mb-6">
              Master your<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-cyan-400">
                certifications
              </span>
              <br />with AI.
            </h1>
            <p className="text-[#8b9cc0] text-lg leading-relaxed">
              Practice with smart exam simulations, AI-powered explanations,
              and personalized study plans. Pass HCIP, CCNA, CCNP, AWS and more.
            </p>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-6 mt-10">
              {[
                { value: '6+', label: 'Certifications' },
                { value: 'AI', label: 'Powered' },
                { value: '24/7', label: 'Access' },
              ].map(({ value, label }) => (
                <div key={label}>
                  <div className="text-2xl font-display font-bold text-white">{value}</div>
                  <div className="text-xs text-[#6b7fa3] uppercase tracking-wider mt-1">{label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="text-xs text-[#4a5d80]">
            © 2026 CertMind · AI-Powered Certification Training
          </div>
        </div>
      </div>

      {/* Right — form panel */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-[420px]">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2.5 mb-10">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-cyan-400 flex items-center justify-center">
              <Zap size={18} className="text-white" strokeWidth={2.5} />
            </div>
            <span className="font-display font-bold text-xl tracking-tight">
              Cert<span className="gradient-text">Mind</span>
            </span>
          </div>

          {/* Title */}
          <div className="mb-8">
            <h2 className="font-display text-2xl font-bold text-ink">
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </h2>
            <p className="text-sm text-muted mt-2">
              {mode === 'login'
                ? 'Sign in to continue your certification journey'
                : 'Start mastering your certifications today'}
            </p>
          </div>

          {/* Tab switch */}
          <div className="flex gap-1 p-1 bg-elevated rounded-xl mb-6">
            {[
              { key: 'login', label: 'Sign In' },
              { key: 'register', label: 'Create Account' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => { setMode(key); setError('') }}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  mode === key
                    ? 'bg-surface text-ink shadow-sm'
                    : 'text-muted hover:text-ink'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" />
                  <input
                    type="text"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    placeholder="Your full name"
                    required
                    className="w-full bg-elevated border border-border rounded-xl pl-11 pr-4 py-3 text-sm text-ink placeholder:text-muted/60 outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">
                Email
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full bg-elevated border border-border rounded-xl pl-11 pr-4 py-3 text-sm text-ink placeholder:text-muted/60 outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-muted uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted" />
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder={mode === 'register' ? 'Min 6 characters' : 'Your password'}
                  required
                  minLength={6}
                  className="w-full bg-elevated border border-border rounded-xl pl-11 pr-11 py-3 text-sm text-ink placeholder:text-muted/60 outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted hover:text-ink transition-colors"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="px-4 py-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm animate-fade-in">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-gradient-to-r from-accent to-cyan-500 text-white font-semibold text-sm shadow-lg shadow-accent/20 hover:shadow-xl hover:shadow-accent/30 transition-all disabled:opacity-60 disabled:cursor-not-allowed active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                </>
              ) : (
                <>
                  {mode === 'login' ? 'Sign In' : 'Create Account'}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Footer hint */}
          <p className="text-center text-xs text-muted mt-6">
            {mode === 'login' ? (
              <>Don't have an account? <button onClick={() => setMode('register')} className="text-accent-soft hover:underline font-medium">Sign up free</button></>
            ) : (
              <>Already have an account? <button onClick={() => setMode('login')} className="text-accent-soft hover:underline font-medium">Sign in</button></>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}
