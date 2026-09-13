import { useEffect, useRef, useState } from 'react'
import { BookOpen, CheckCircle, FileText, Loader, Upload, AlertCircle } from 'lucide-react'
import { ragAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function Knowledge() {
  const { selectedCert } = useStore()
  const [sources, setSources] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  async function loadSources() {
    try { setSources(await ragAPI.knowledgeSources()) } catch { setError('Could not load your knowledge sources.') }
  }

  useEffect(() => { loadSources() }, [])

  useEffect(() => {
    if (!sources.some(source => source.status === 'processing')) return undefined
    const timer = setInterval(loadSources, 4000)
    return () => clearInterval(timer)
  }, [sources])

  async function handleUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return
    setBusy(true); setError('')
    try {
      const result = await ragAPI.uploadKnowledge(file, selectedCert)
      setSources(current => [result, ...current])
      await loadSources()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try another Markdown file.')
    } finally {
      setBusy(false)
      event.target.value = ''
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center"><BookOpen size={20} className="text-accent-soft" /></div>
          <div><h1 className="font-display text-2xl font-bold text-ink">Personal Knowledge</h1><p className="text-sm text-muted mt-1">Teach CertMind from your own notes, one source at a time.</p></div>
        </div>
      </div>

      <Card>
        <div onClick={() => inputRef.current?.click()} className="border-2 border-dashed border-border hover:border-accent/50 rounded-xl p-9 flex flex-col items-center gap-3 cursor-pointer transition-all">
          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">{busy ? <Loader size={21} className="text-accent-soft animate-spin" /> : <Upload size={21} className="text-accent-soft" />}</div>
          <p className="font-semibold text-ink">{busy ? 'Uploading your notes...' : 'Upload a Markdown knowledge file'}</p>
          <p className="text-sm text-muted">.md, .markdown, or .mdown · Maximum 5MB · UTF-8</p>
          {!busy && <Button variant="secondary" size="sm" onClick={e => { e.stopPropagation(); inputRef.current?.click() }}>Choose Markdown File</Button>}
        </div>
        <input ref={inputRef} type="file" accept=".md,.markdown,.mdown,text/markdown" onChange={handleUpload} className="hidden" />
        {error && <div className="mt-3 flex items-center gap-2 px-4 py-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm"><AlertCircle size={15} />{error}</div>}
      </Card>

      <Card className="border-accent/20 bg-accent/5">
        <div className="flex items-start gap-3"><FileText size={17} className="text-accent-soft mt-0.5" /><div><p className="font-semibold text-sm text-ink">How personal retrieval works</p><p className="text-xs text-muted mt-1 leading-relaxed">Your file is split into searchable sections and embedded with your account identity. When you choose Personal or Both in an AI explanation, CertMind can use these sections without exposing them to other users.</p></div></div>
      </Card>

      <div className="space-y-3">
        <h2 className="font-display font-semibold text-sm text-ink">Your sources ({sources.length})</h2>
        {sources.length === 0 ? <Card className="py-10 text-center"><FileText size={28} className="text-muted mx-auto mb-2" /><p className="text-sm text-muted">No personal sources yet.</p></Card> : sources.map(source => (
          <Card key={source.source_id || source.id}>
            <div className="flex items-center gap-3"><div className="w-9 h-9 rounded-lg bg-elevated flex items-center justify-center"><FileText size={16} className="text-accent-soft" /></div><div className="flex-1 min-w-0"><p className="font-medium text-sm text-ink truncate">{source.filename || source.name}</p><p className="text-xs text-muted mt-0.5">{source.chunk_count ? `${source.chunk_count} searchable sections` : 'Preparing searchable sections'}</p></div><Badge variant={source.status === 'ready' ? 'success' : source.status === 'failed' ? 'danger' : 'warning'}>{source.status === 'ready' ? <><CheckCircle size={11} /> Ready</> : source.status}</Badge></div>
            {source.error && <p className="text-xs text-danger mt-3">{source.error}</p>}
          </Card>
        ))}
      </div>
    </div>
  )
}

