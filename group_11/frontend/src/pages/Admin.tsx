import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { generateBlog, listBlogs } from '../services/api'
import type { BlogListItem, BlogPost } from '../services/api'

const PRESET_TOPICS = [
  { label: 'Savings Tips', topic: 'Simple savings tips for beginners' },
  { label: 'Credit Score', topic: 'How to improve your credit score quickly' },
  { label: 'Debt Management', topic: 'Smart strategies to get out of debt' },
  { label: 'Budgeting', topic: 'How to create a monthly budget that works' },
  { label: 'Emergency Fund', topic: 'Why you need an emergency fund and how to build one' },
  { label: 'Investing Basics', topic: 'Investing basics for absolute beginners' },
]

const SpeechRecognition =
  typeof window !== 'undefined'
    ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    : null

export default function Admin() {
  const [searchParams] = useSearchParams()
  const isWriteMode = searchParams.get('mode') === 'write'

  const [topic, setTopic] = useState('')
  const [listening, setListening] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [generatingStep, setGeneratingStep] = useState('')
  const [result, setResult] = useState<BlogPost | null>(null)
  const [error, setError] = useState('')
  const [blogs, setBlogs] = useState<BlogListItem[]>([])
  const recognitionRef = useRef<any>(null)

  const speechSupported = !!SpeechRecognition

  useEffect(() => {
    listBlogs().then(setBlogs).catch(() => {})
  }, [result])

  const startListening = useCallback(() => {
    if (!SpeechRecognition) return
    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = true
    recognition.continuous = false
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((r: any) => r[0].transcript)
        .join('')
      setTopic(transcript)
    }
    recognition.onend = () => setListening(false)
    recognition.onerror = () => setListening(false)
    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
  }, [])

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop()
    setListening(false)
  }, [])

  const handleGenerate = async (topicText?: string) => {
    const t = (topicText ?? topic).trim()
    if (!t || generating) return
    setTopic(t)
    setError('')
    setResult(null)
    setGenerating(true)
    setGeneratingStep('Writing tip...')
    try {
      const blog = await generateBlog(t)
      setResult(blog)
      setGeneratingStep('')
    } catch (err: any) {
      let msg = err.message || 'Generation failed'
      try {
        const m = msg.match(/\{.*\}/)
        if (m) msg = JSON.parse(m[0]).detail || msg
      } catch { /* keep raw */ }
      setError(msg)
      setGeneratingStep('')
    } finally {
      setGenerating(false)
    }
  }

  const backendUrl = import.meta.env.VITE_BACKEND_URL || ''

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-20 pb-12 px-4 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          {isWriteMode ? 'Write a Tip' : 'Tips'}
        </h1>
        <p className="text-slate-500 mb-8">
          {isWriteMode
            ? 'Speak or type a topic. AI generates the tip, image, and podcast.'
            : 'AI-generated financial tips with images and podcasts.'}
        </p>

        {/* Write block — only in write mode (via Admin button) */}
        {isWriteMode && (
          <>
            {/* Mic + Input area */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
              <div className="flex flex-col items-center mb-6">
                <button
                  onClick={listening ? stopListening : startListening}
                  disabled={!speechSupported && !listening}
                  className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
                    listening
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-200'
                      : speechSupported
                        ? 'bg-brand-600 hover:bg-brand-700 shadow-lg shadow-brand-200'
                        : 'bg-slate-300 cursor-not-allowed'
                  }`}
                  title={speechSupported ? (listening ? 'Stop listening' : 'Click to speak') : 'Speech not supported in this browser'}
                >
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
                <span className="text-xs text-slate-400 mt-2">
                  {listening ? 'Listening... speak your topic' : speechSupported ? 'Tap to speak' : 'Type your topic below'}
                </span>
                {!speechSupported && (
                  <span className="text-xs text-amber-500 mt-1">Voice input not supported in this browser. Use text input instead.</span>
                )}
              </div>

              <div className="flex gap-3">
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                  placeholder="Type a tip topic..."
                  maxLength={200}
                  className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                />
                <button
                  onClick={() => handleGenerate()}
                  disabled={generating || !topic.trim()}
                  className="px-6 py-3 bg-brand-600 text-white rounded-xl hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                >
                  {generating ? 'Generating...' : 'Generate'}
                </button>
              </div>
              <div className="text-xs text-slate-400 mt-1 text-right">{topic.length}/200</div>
            </div>

            {/* Quick topic presets */}
            <div className="mb-6">
              <div className="text-sm font-medium text-slate-700 mb-2">Quick topics</div>
              <div className="flex flex-wrap gap-2">
                {PRESET_TOPICS.map((p) => (
                  <button
                    key={p.label}
                    onClick={() => handleGenerate(p.topic)}
                    disabled={generating}
                    className="px-3 py-1.5 text-xs font-medium rounded-full border border-slate-200 bg-white hover:border-brand-300 hover:bg-brand-50 text-slate-600 transition-colors disabled:opacity-50"
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Generation progress */}
            {generating && (
              <div className="bg-brand-50 border border-brand-200 rounded-2xl p-5 mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm font-medium text-brand-800">{generatingStep}</span>
                </div>
                <p className="text-xs text-brand-600 mt-2">Generating tip, image, and podcast. This may take 15-30 seconds...</p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6">
                <div className="text-sm text-red-800">{error}</div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden mb-8">
                {result.image_url && (
                  <img src={`${backendUrl}${result.image_url}`} alt={result.title} className="w-full h-48 object-cover" />
                )}
                <div className="p-5">
                  <h2 className="text-lg font-bold text-slate-900 mb-2">{result.title}</h2>
                  <p className="text-sm text-slate-600 whitespace-pre-line mb-4">{result.content}</p>
                  {result.audio_url && (
                    <div>
                      <div className="text-xs font-medium text-slate-500 mb-1">Podcast</div>
                      <audio controls className="w-full" src={`${backendUrl}${result.audio_url}`} />
                    </div>
                  )}
                  <Link to={`/admin/blog/${result.id}`} className="inline-block mt-3 text-sm text-brand-600 hover:text-brand-700 font-medium">
                    View full tip &rarr;
                  </Link>
                </div>
              </div>
            )}
          </>
        )}

        {/* Tips list — always shown */}
        {blogs.length > 0 ? (
          <div>
            {isWriteMode && <h2 className="text-lg font-semibold text-slate-900 mb-3">Previous Tips</h2>}
            <div className="space-y-2">
              {blogs.map((b) => (
                <Link
                  key={b.id}
                  to={`/admin/blog/${b.id}`}
                  className="flex items-center gap-4 bg-white rounded-xl border border-slate-200 p-4 hover:border-brand-300 transition-colors"
                >
                  {b.image_url && (
                    <img src={`${backendUrl}${b.image_url}`} alt="" className="w-16 h-16 rounded-lg object-cover flex-shrink-0" />
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium text-slate-900 truncate">{b.title}</div>
                    <div className="text-xs text-slate-400">{b.topic}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ) : (
          !isWriteMode && (
            <div className="text-center py-12 text-slate-400">
              <p>No tips yet.</p>
              <Link to="/admin?mode=write" className="text-brand-600 hover:text-brand-700 text-sm font-medium mt-2 inline-block">
                Write your first tip &rarr;
              </Link>
            </div>
          )
        )}
      </div>
    </div>
  )
}
