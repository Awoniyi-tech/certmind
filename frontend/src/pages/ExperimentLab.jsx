import { useState } from 'react'
import { FlaskConical, Trophy, Plus, X, AlertCircle } from 'lucide-react'
import { ragAPI } from '../lib/api.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function ExperimentLab() {
  const [name, setName] = useState('Prompt response comparison')
  const [candidates, setCandidates] = useState([{ name: 'Candidate A', response: '' }, { name: 'Candidate B', response: '' }])
  const [expected, setExpected] = useState('')
  const [required, setRequired] = useState('')
  const [forbidden, setForbidden] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  function updateCandidate(index, key, value) { setCandidates(items => items.map((item, i) => i === index ? { ...item, [key]: value } : item)) }
  async function run(event) {
    event.preventDefault(); setBusy(true); setError(''); setResult(null)
    try { setResult(await ragAPI.experiment({ name, candidates, expected: expected || null, required_phrases: required.split(',').map(x => x.trim()).filter(Boolean), forbidden_phrases: forbidden.split(',').map(x => x.trim()).filter(Boolean) })) }
    catch (err) { setError(err.response?.data?.detail || 'Experiment failed.') }
    finally { setBusy(false) }
  }
  return <div className="space-y-6 animate-fade-in">
    <div className="flex items-center gap-3"><div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center"><FlaskConical size={20} className="text-accent-soft" /></div><div><h1 className="font-display text-2xl font-bold text-ink">Experiment Lab</h1><p className="text-sm text-muted mt-1">Compare candidates against one reproducible evaluation rubric.</p></div></div>
    <div className="grid lg:grid-cols-[1.1fr_.9fr] gap-5"><Card><form onSubmit={run} className="space-y-4"><input value={name} onChange={e => setName(e.target.value)} className="w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent" placeholder="Experiment name" />
      {candidates.map((candidate, index) => <div key={index} className="rounded-xl border border-border p-3 space-y-2"><div className="flex gap-2"><input value={candidate.name} onChange={e => updateCandidate(index, 'name', e.target.value)} className="flex-1 bg-elevated border border-border rounded-lg px-3 py-2 text-xs text-ink outline-none" /><button type="button" onClick={() => setCandidates(items => items.filter((_, i) => i !== index))} className="text-muted hover:text-danger" disabled={candidates.length <= 1}><X size={15} /></button></div><textarea required rows={4} value={candidate.response} onChange={e => updateCandidate(index, 'response', e.target.value)} placeholder={`Paste ${candidate.name} response...`} className="w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent resize-y" /></div>)}
      <button type="button" onClick={() => setCandidates(items => [...items, { name: `Candidate ${String.fromCharCode(65 + items.length)}`, response: '' }])} disabled={candidates.length >= 20} className="flex items-center gap-1.5 text-xs font-semibold text-accent-soft hover:text-ink"><Plus size={14} /> Add candidate</button>
      <textarea rows={3} value={expected} onChange={e => setExpected(e.target.value)} placeholder="Expected answer (optional)" className="w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-sm text-ink outline-none focus:border-accent resize-y" /><div className="grid sm:grid-cols-2 gap-3"><input value={required} onChange={e => setRequired(e.target.value)} placeholder="Required phrases, comma separated" className="w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-xs text-ink outline-none focus:border-accent" /><input value={forbidden} onChange={e => setForbidden(e.target.value)} placeholder="Forbidden phrases, comma separated" className="w-full bg-elevated border border-border rounded-lg px-3 py-2.5 text-xs text-ink outline-none focus:border-accent" /></div><Button type="submit" disabled={busy}>{busy ? 'Running...' : 'Run experiment'}</Button></form>{error && <div className="mt-4 flex items-center gap-2 text-sm text-danger"><AlertCircle size={15} />{error}</div>}</Card>
      <Card className="h-fit"><div className="flex items-center justify-between mb-5"><h2 className="font-display font-semibold text-ink">Comparison</h2>{result && <Badge variant="success"><Trophy size={11} /> Winner: {result.winner}</Badge>}</div>{!result ? <p className="py-12 text-center text-sm text-muted">Run an experiment to compare candidates.</p> : <div className="space-y-3">{result.results.map(item => <div key={item.name} className={`rounded-xl border p-4 ${item.name === result.winner ? 'border-success/40 bg-success/5' : 'border-border bg-elevated/30'}`}><div className="flex justify-between items-center"><span className="text-sm font-semibold text-ink">{item.name}</span><span className="font-mono text-lg font-bold text-accent-soft">{item.score}</span></div><div className="mt-2 h-1.5 rounded-full bg-elevated overflow-hidden"><div className="h-full bg-accent rounded-full" style={{ width: `${item.score}%` }} /></div><p className="text-xs text-muted mt-2">{item.passed ? 'Passed evaluation threshold' : 'Needs review'}</p></div>)}</div>}</Card></div>
  </div>
}

