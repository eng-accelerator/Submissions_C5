import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { uploadDocument, listDocuments, deleteDocument } from '../services/api'
import type { DocumentInfo } from '../services/api'

const STATUS_STYLES: Record<string, string> = {
  processed: 'bg-green-100 text-green-700',
  processing: 'bg-blue-100 text-blue-700',
  uploaded: 'bg-slate-100 text-slate-700',
  failed: 'bg-red-100 text-red-700',
}

const FILE_TYPE_ICONS: Record<string, string> = {
  pdf: 'PDF',
  csv: 'CSV',
  json: 'JSON',
  xlsx: 'XLS',
  png: 'IMG',
  jpg: 'IMG',
  jpeg: 'IMG',
  webp: 'IMG',
}

const DOC_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  credit_report: { label: 'Credit Report', color: 'bg-blue-100 text-blue-700' },
  bank_statement: { label: 'Bank Statement', color: 'bg-green-100 text-green-700' },
  pay_stub: { label: 'Pay Stub', color: 'bg-purple-100 text-purple-700' },
  expense_report: { label: 'Expense Report', color: 'bg-amber-100 text-amber-700' },
  unknown: { label: 'Document', color: 'bg-slate-100 text-slate-700' },
}

function formatNum(n: number) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n)
}

interface DocSummary {
  id: string
  filename: string
  file_type: string
  doc_type: string
  chunks: number
  highlights: Array<{ key: string; value: string }>
  numbers: { count?: number; min?: number; max?: number; total?: number; avg?: number }
  credit_score?: number
  banks?: string[]
}

type Tab = 'upload' | 'summary'

export default function Upload() {
  const [tab, setTab] = useState<Tab>('upload')
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [summaries, setSummaries] = useState<DocSummary[]>([])
  const [hasData, setHasData] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadDocs = useCallback(async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch { /* backend might not be running */ }
  }, [])

  const loadSummary = useCallback(async () => {
    try {
      const base = import.meta.env.VITE_BACKEND_URL || ''
      const res = await fetch(`${base}/api/documents/summary`)
      const data = await res.json()
      setHasData(data.has_data)
      setSummaries(data.documents || [])
    } catch { /* ignore */ }
  }, [])

  useEffect(() => {
    loadDocs()
    loadSummary()
  }, [loadDocs, loadSummary])

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setError('')
    setMessage('')

    for (const file of Array.from(files)) {
      try {
        const res = await uploadDocument(file)
        setMessage(res.message)
        setDocuments((prev) => [...prev, res.document])
      } catch (err: any) {
        setError(err.message)
      }
    }
    setUploading(false)
    loadSummary()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleUpload(e.dataTransfer.files)
  }

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      loadSummary()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const processedCount = documents.filter((d) => d.status === 'processed').length

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-20 pb-12 px-4 max-w-4xl mx-auto">
        {/* Tabs */}
        <div className="flex items-center gap-1 mb-6 border-b border-slate-200">
          <button
            onClick={() => setTab('upload')}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === 'upload'
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Upload Documents
          </button>
          <button
            onClick={() => { setTab('summary'); loadSummary() }}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
              tab === 'summary'
                ? 'border-brand-600 text-brand-700'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Financial Summary
            {processedCount > 0 && (
              <span className="bg-brand-100 text-brand-700 text-xs font-medium px-1.5 py-0.5 rounded-full">{processedCount}</span>
            )}
          </button>
        </div>

        {/* ─── Upload Tab ─── */}
        {tab === 'upload' && (
          <>
            <p className="text-slate-500 mb-6">
              Upload your financial documents (credit reports, bank statements, salary slips, etc.) to give the AI coach more context.
            </p>

            {/* Drop zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
                dragOver ? 'border-brand-500 bg-brand-50' : 'border-slate-300 bg-white'
              }`}
            >
              <svg className="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-slate-600 mb-2">
                {uploading ? 'Processing...' : 'Drag & drop files here, or click to browse'}
              </p>
              <p className="text-xs text-slate-400 mb-4">Supports PDF, CSV, JSON, XLSX, PNG, JPG (max 10MB)</p>
              <label className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 cursor-pointer transition-colors text-sm">
                <input
                  type="file"
                  accept=".pdf,.csv,.json,.xlsx,.png,.jpg,.jpeg,.webp"
                  multiple
                  onChange={(e) => handleUpload(e.target.files)}
                  className="hidden"
                  disabled={uploading}
                />
                {uploading ? 'Uploading...' : 'Choose Files'}
              </label>
            </div>

            {message && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-xl text-sm text-green-700">{message}</div>
            )}
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>
            )}

            {documents.length > 0 && (
              <div className="mt-8">
                <h2 className="text-lg font-semibold text-slate-900 mb-3">Uploaded Documents</h2>
                <div className="space-y-2">
                  {documents.map((doc) => (
                    <div key={doc.id} className="bg-white rounded-xl border border-slate-200 p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-xs font-bold text-slate-600">
                          {FILE_TYPE_ICONS[doc.file_type] || doc.file_type.toUpperCase()}
                        </span>
                        <div>
                          <div className="text-sm font-medium text-slate-900">{doc.filename}</div>
                          <div className="text-xs text-slate-400">
                            {doc.chunks > 0 ? `${doc.chunks} chunks indexed` : doc.status}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_STYLES[doc.status] || ''}`}>
                          {doc.status}
                        </span>
                        <button onClick={() => handleDelete(doc.id)} className="text-slate-400 hover:text-red-500 transition-colors" title="Delete">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                {processedCount > 0 && (
                  <div className="mt-4 flex items-center gap-4">
                    <button
                      onClick={() => { setTab('summary'); loadSummary() }}
                      className="text-sm text-brand-600 hover:text-brand-700 font-medium"
                    >
                      View Financial Summary &rarr;
                    </button>
                    <Link
                      to="/plan"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 text-sm font-medium transition-colors"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Generate Financial Plan
                    </Link>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* ─── Financial Summary Tab ─── */}
        {tab === 'summary' && (
          <>
            {!hasData ? (
              <div className="text-center py-16">
                <svg className="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-slate-500 mb-2">No documents uploaded yet</p>
                <button onClick={() => setTab('upload')} className="text-brand-600 hover:text-brand-700 text-sm font-medium">
                  Upload your first document &rarr;
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {summaries.map((doc) => {
                  const typeInfo = DOC_TYPE_LABELS[doc.doc_type] || DOC_TYPE_LABELS.unknown
                  return (
                    <div key={doc.id} className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
                      {/* Header */}
                      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-xs font-bold text-slate-600">
                            {FILE_TYPE_ICONS[doc.file_type] || doc.file_type.toUpperCase()}
                          </span>
                          <div>
                            <div className="text-sm font-semibold text-slate-900">{doc.filename}</div>
                            <div className="text-xs text-slate-400">{doc.chunks} chunks indexed</div>
                          </div>
                        </div>
                        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${typeInfo.color}`}>
                          {typeInfo.label}
                        </span>
                      </div>

                      {/* Stats row */}
                      <div className="px-5 py-4">
                        {/* Credit score + banks (if credit report) */}
                        {doc.credit_score && (
                          <div className="flex items-center gap-6 mb-4">
                            <div className="text-center">
                              <div className={`text-3xl font-bold ${doc.credit_score < 600 ? 'text-red-600' : doc.credit_score < 700 ? 'text-amber-600' : 'text-green-600'}`}>
                                {doc.credit_score}
                              </div>
                              <div className="text-xs text-slate-400">Credit Score</div>
                            </div>
                            {doc.banks && doc.banks.length > 0 && (
                              <div>
                                <div className="text-xs text-slate-500 mb-1">Banks Found</div>
                                <div className="flex flex-wrap gap-1">
                                  {doc.banks.map((b) => (
                                    <span key={b} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{b}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Number stats */}
                        {doc.numbers.count && doc.numbers.count > 0 && (
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                            <StatCard label="Data Points" value={formatNum(doc.numbers.count!)} />
                            <StatCard label="Total" value={formatNum(doc.numbers.total!)} color="blue" />
                            <StatCard label="Highest" value={formatNum(doc.numbers.max!)} color="red" />
                            <StatCard label="Average" value={formatNum(doc.numbers.avg!)} color="green" />
                          </div>
                        )}

                        {/* Highlights — key data from document */}
                        {doc.highlights.length > 0 && (
                          <div>
                            <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">Key Data</div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                              {doc.highlights.map((h, i) => (
                                <div key={i} className="flex items-start gap-2 text-xs bg-slate-50 rounded-lg px-3 py-2">
                                  <span className="text-slate-400 flex-shrink-0 min-w-[80px]">{h.key}</span>
                                  <span className="text-slate-700 font-medium">{h.value}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Visual bar for numbers spread */}
                        {doc.numbers.count && doc.numbers.max && doc.numbers.total && (
                          <div className="mt-4">
                            <div className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wide">Value Distribution</div>
                            <div className="flex gap-1 h-8 rounded-lg overflow-hidden bg-slate-100">
                              {(() => {
                                const max = doc.numbers.max!
                                const avg = doc.numbers.avg!
                                const min = doc.numbers.min!
                                const total = max + avg + min || 1
                                return (
                                  <>
                                    <div className="bg-green-400 rounded-l-lg flex items-center justify-center text-xs text-white font-medium" style={{ width: `${(min / total) * 100}%` }}>
                                      {min > total * 0.1 ? `Min` : ''}
                                    </div>
                                    <div className="bg-blue-400 flex items-center justify-center text-xs text-white font-medium" style={{ width: `${(avg / total) * 100}%` }}>
                                      Avg
                                    </div>
                                    <div className="bg-red-400 rounded-r-lg flex items-center justify-center text-xs text-white font-medium" style={{ width: `${(max / total) * 100}%` }}>
                                      Max
                                    </div>
                                  </>
                                )
                              })()}
                            </div>
                            <div className="flex justify-between text-xs text-slate-400 mt-1">
                              <span>{formatNum(doc.numbers.min!)}</span>
                              <span>{formatNum(doc.numbers.avg!)}</span>
                              <span>{formatNum(doc.numbers.max!)}</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: string; color?: string }) {
  const colorMap: Record<string, string> = {
    blue: 'text-blue-600',
    red: 'text-red-600',
    green: 'text-green-600',
  }
  return (
    <div className="bg-slate-50 rounded-xl p-3 text-center">
      <div className={`text-lg font-bold ${colorMap[color || ''] || 'text-slate-900'}`}>{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  )
}
