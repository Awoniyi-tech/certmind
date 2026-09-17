import { useState } from 'react'
import { CheckCircle, ClipboardCheck, XCircle, AlertCircle } from 'lucide-react'
import { ragAPI } from '../lib/api.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function EvaluationLab() {
  const [form, setForm] = useState({ name: 'Response quality check', response: '', expected: '', required: '', forbidden: '', maxLength: '' })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const update = (key, value) => setForm(current => ({ ...current, [key]: value }))

  async function runEvaluation(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null)
    try {
      setResult(await ragAPI.evaluate({
        name: form.name,
        response: form.response,
        expected: form.expected || null,
        required_phrases: form.required.split(',').map(item => item.trim()).filter(Boolean),
        forbidden_phrases: form.forbidden.split(',').map(item => item.trim()).filter(Boolean),
        max_length: form.maxLength ? Number(form.maxLength) : null,
      }))
    } catch (err) { setError(err.response?.data?.detail || 'Evaluation failed.') }
    finally { setBusy(false) }
  }

  return <div className="space-y-6 animate-fade-in">
    <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center"><ClipboardCheck size={20} className="text-accent-soft" /></div><div><h1 className="font-display text-2xl font-bold text-ink">Evaluation Lab</h1><p className="text-sm text-muted mt-1">Measure an AI response with transparent, repeatable checks.</p></div></div>
    <div className="grid lg:grid-cols-[1.1fr_.9fr] gap-5">
      <Card><form onSubmit={runEvaluation} className="space-y-4">
        <div><label className="text-xs font-semibold text-muted uppercase tracking-wider">Evaluation name</label><input value={form.name} onChange={e => update('name', e.target.value)} className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent" /></div>
        <div><label className="text-xs font-semibold text-muted uppercase tracking-wider">Model response</label><textarea required rows={8} value={form.response} onChange={e => update('response', e.target.value)} placeholder="Paste the response you want to evaluate..." className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent resize-y" /></div>
        <div><label className="text-xs font-semibold text-muted uppercase tracking-wider">Expected answer <span className="normal-case font-normal">(optional)</span></label><textarea rows={3} value={form.expected} onChange={e => update('expected', e.target.value)} placeholder="Reference answer for token-overlap checking" className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent resize-y" /></div>
        <div className="grid sm:grid-cols-2 gap-3"><div><label className="text-xs font-semibold text-muted uppercase tracking-wider">Required phrases</label><input value={form.required} onChange={e => update('required', e.target.value)} placeholder="e.g. OSPF, TCP" className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent" /></div><div><label className="text-xs font-semibold text-muted uppercase tracking-wider">Forbidden phrases</label><input value={form.forbidden} onChange={e => update('forbidden', e.target.value)} placeholder="e.g. I am not sure" className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent" /></div></div>
        <div className="flex items-end gap-3"><div className="flex-1"><label className="text-xs font-semibold text-muted uppercase tracking-wider">Maximum characters</label><input type="number" min="1" value={form.maxLength} onChange={e => update('maxLength', e.target.value)} placeholder="Optional" className="mt-1.5 w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent" /></div><Button type="submit" disabled={busy}>{busy ? 'Evaluating...' : 'Run evaluation'}</Button></div>
      </form>{error && <div className="mt-4 flex gap-2 items-center text-sm text-danger"><AlertCircle size={15} />{error}</div>}</Card>
      <Card className="h-fit"><div className="flex items-center justify-between mb-5"><h2 className="font-display font-semibold text-ink">Evaluation result</h2>{result && <Badge variant={result.passed ? 'success' : 'danger'}>{result.passed ? 'PASS' : 'REVIEW'}</Badge>}</div>{!result ? <div className="py-12 text-center text-sm text-muted"><ClipboardCheck size={30} className="mx-auto mb-3 opacity-50" /><p>Your score and check breakdown will appear here.</p></div> : <><div className="flex items-end gap-3 mb-6"><span className={`font-display text-5xl font-bold ${result.passed ? 'text-success' : 'text-warning'}`}>{result.score}</span><span className="text-sm text-muted mb-2">/ 100</span></div><div className="space-y-2">{result.checks.map(check => <div key={check.name} className="flex items-start gap-2.5 rounded-lg bg-elevated/60 px-3 py-2.5"><span className="mt-0.5">{check.passed ? <CheckCircle size={15} className="text-success" /> : <XCircle size={15} className="text-danger" />}</span><div><p className="text-xs font-semibold text-ink">{check.name}</p><p className="text-[11px] text-muted mt-0.5">{check.detail}</p></div></div>)}</div></>}</Card>
    </div>
  </div>
}
