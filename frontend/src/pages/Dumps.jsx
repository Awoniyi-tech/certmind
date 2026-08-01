import { useEffect, useState, useRef } from 'react'
import { Upload, Trash2, Loader, CheckCircle, AlertCircle, Database, Sparkles } from 'lucide-react'
import { dumpsAPI } from '../lib/api.js'
import { useStore } from '../store/useStore.js'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'

export default function Dumps() {
  const { selectedCert, certifications } = useStore()
  const [banks, setBanks]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState({})
  const [error, setError]       = useState('')
  const [progresses, setProgresses] = useState({})
  const fileRef = useRef(null)
  const pollTimers = useRef({})

  useEffect(() => {
    loadBanks()
    return () => {
      // Clean up polling timers on unmount
      Object.values(pollTimers.current).forEach(clearInterval)
    }
  }, [selectedCert])

  function loadBanks() {
    setLoading(true)
    dumpsAPI.list(selectedCert).then(data => {
      setBanks(data)
      // Start polling for any banks that are still generating
      data.forEach(b => {
        const bankId = b.bank_id || b.id
        const progress = b.explanation_progress
        if (progress && progress !== 'complete' && progress !== 'failed') {
          startPolling(bankId)
        }
      })
    }).catch(() => {}).finally(() => setLoading(false))
  }

  function startPolling(bankId) {
    if (pollTimers.current[bankId]) return // already polling

    const poll = async () => {
      try {
        const status = await dumpsAPI.status(bankId)
        setProgresses(prev => ({ ...prev, [bankId]: status }))
        if (status.is_complete || status.progress === 'failed') {
          clearInterval(pollTimers.current[bankId])
          delete pollTimers.current[bankId]
          // Refresh banks list to get updated data
          dumpsAPI.list(selectedCert).then(setBanks).catch(() => {})
        }
      } catch {
        clearInterval(pollTimers.current[bankId])
        delete pollTimers.current[bankId]
      }
    }

    poll() // immediate first check
    pollTimers.current[bankId] = setInterval(poll, 4000)
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const res = await dumpsAPI.upload(file, selectedCert)
      setBanks(prev => [res, ...prev])
      await processBank(res.bank_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Try again.')
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  async function processBank(bankId) {
    setProcessing(p => ({ ...p, [bankId]: true }))
    try {
      const res = await dumpsAPI.process(bankId)
      setBanks(prev => prev.map(b =>
        (b.bank_id || b.id) === bankId
          ? { ...b, total_questions: res.questions_added, status: 'processed' }
          : b
      ))
      // Start polling for explanation progress
      startPolling(bankId)
    } catch (err) {
      setError(err.response?.data?.detail || 'Processing failed.')
    } finally {
      setProcessing(p => ({ ...p, [bankId]: false }))
    }
  }

  async function deleteBank(bankId) {
    if (!confirm('Delete this question bank? This cannot be undone.')) return
    await dumpsAPI.delete(bankId)
    setBanks(prev => prev.filter(b => b.id !== bankId && b.bank_id !== bankId))
    if (pollTimers.current[bankId]) {
      clearInterval(pollTimers.current[bankId])
      delete pollTimers.current[bankId]
    }
  }

  const cert = certifications.find(c => c.id === selectedCert)

  function renderExplanationProgress(bankId, questionCount) {
    const progress = progresses[bankId]
    const bank = banks.find(b => (b.bank_id || b.id) === bankId)
    const bankProgress = bank?.explanation_progress

    // No progress info yet
    if (!progress && !bankProgress) return null
    if (bankProgress === 'complete' || progress?.is_complete) {
      return (
        <div className="flex items-center gap-1.5 text-xs text-success">
          <CheckCircle size={12} />
          Explanations ready
        </div>
      )
    }
    if (bankProgress === 'failed' || progress?.progress === 'failed') {
      return (
        <div className="flex items-center gap-1.5 text-xs text-danger">
          <AlertCircle size={12} />
          Explanation generation failed
        </div>
      )
    }

    // In progress
    const done = progress?.with_explanation || 0
    const total = progress?.total_questions || questionCount || 0
    const pct = total > 0 ? Math.round((done / total) * 100) : 0

    return (
      <div className="space-y-1.5 mt-2">
        <div className="flex items-center gap-1.5 text-xs text-accent-soft">
          <Sparkles size={12} className="animate-pulse" />
          Generating explanations: {done}/{total}
        </div>
        <div className="h-1.5 bg-elevated rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-accent to-accent-soft rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Dump Manager</h1>
          <p className="text-sm text-muted mt-1">Upload exam dump PDFs for {cert?.name}</p>
        </div>
      </div>

      {/* Upload zone */}
      <Card>
        <div
          onClick={() => fileRef.current?.click()}
          className="border-2 border-dashed border-border hover:border-accent/50 rounded-xl p-10 flex flex-col items-center gap-4 cursor-pointer transition-all group"
        >
          <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center group-hover:bg-accent/20 transition-all">
            {uploading
              ? <Loader size={22} className="text-accent-soft animate-spin" />
              : <Upload size={22} className="text-accent-soft" />
            }
          </div>
          <div className="text-center">
            <p className="font-semibold text-ink">
              {uploading ? 'Uploading...' : 'Drop your dump PDF here'}
            </p>
            <p className="text-sm text-muted mt-1">
              {uploading
                ? 'Extracting questions from PDF. This may take a moment.'
                : 'PDF format only · Max 50MB · Questions extracted automatically'
              }
            </p>
          </div>
          {!uploading && (
            <Button variant="secondary" size="sm" onClick={e => { e.stopPropagation(); fileRef.current?.click() }}>
              Browse Files
            </Button>
          )}
        </div>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          onChange={handleUpload}
          className="hidden"
        />
        {error && (
          <div className="mt-3 flex items-center gap-2 px-4 py-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm">
            <AlertCircle size={15} />
            {error}
          </div>
        )}
      </Card>

      {/* Banks list */}
      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
        </div>
      ) : banks.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12 text-center">
          <Database size={32} className="text-muted mb-3" />
          <p className="font-semibold text-ink">No question banks yet</p>
          <p className="text-sm text-muted mt-1">Upload a dump PDF to get started.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          <h2 className="font-display font-semibold text-sm text-ink">
            Question Banks ({banks.length})
          </h2>
          {banks.map(b => {
            const bankId = b.bank_id || b.id
            const isProcessing = processing[bankId]
            const questionCount = b.total_questions || 0
            return (
              <Card key={bankId}>
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    questionCount > 0 ? 'bg-success/10' : 'bg-warning/10'
                  }`}>
                    {questionCount > 0
                      ? <CheckCircle size={18} className="text-success" />
                      : <Database size={18} className="text-warning" />
                    }
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-ink text-sm truncate">
                        {b.source_name || b.filename || 'Dump PDF'}
                      </p>
                      <Badge variant={questionCount > 0 ? 'success' : 'warning'}>
                        {questionCount > 0 ? `${questionCount} Q's` : 'Not processed'}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted mt-0.5">
                      {b.cert_id} · Uploaded {new Date(b.created_at || Date.now()).toLocaleDateString()}
                    </p>
                    {questionCount > 0 && renderExplanationProgress(bankId, questionCount)}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {questionCount === 0 && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => processBank(bankId)}
                        disabled={isProcessing}
                      >
                        {isProcessing
                          ? <><Loader size={13} className="animate-spin" /> Processing...</>
                          : 'Extract Questions'
                        }
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteBank(bankId)}
                      className="text-danger hover:text-danger"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {/* Info card */}
      <Card className="border-accent/20 bg-accent/5">
        <h3 className="font-semibold text-sm text-accent-soft mb-2">How Dump Processing Works</h3>
        <div className="space-y-1.5 text-xs text-muted">
          <p>1. Upload your Huawei exam dump PDF</p>
          <p>2. The system extracts every question, option, and answer automatically</p>
          <p>3. AI explanations are generated in the background (you can leave this page)</p>
          <p>4. Once ready, start exams with instant explanations for every question</p>
          <p>5. Questions are stored in the question bank linked to {cert?.name}</p>
        </div>
      </Card>
    </div>
  )
}
