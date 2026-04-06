import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getBlog, deleteBlog } from '../services/api'
import type { BlogPost } from '../services/api'

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>()
  const [blog, setBlog] = useState<BlogPost | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    getBlog(id)
      .then(setBlog)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  const handleDelete = async () => {
    if (!id || !confirm('Delete this tip?')) return
    try {
      await deleteBlog(id)
      window.location.href = '/admin'
    } catch (e: any) {
      setError(e.message)
    }
  }

  const backendUrl = import.meta.env.VITE_BACKEND_URL || ''

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="pt-20 text-center text-slate-500">Loading tip...</div>
      </div>
    )
  }

  if (error || !blog) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <div className="pt-20 text-center">
          <div className="text-red-500 mb-4">{error || 'Tip not found'}</div>
          <Link to="/admin" className="text-brand-600 hover:text-brand-700 text-sm font-medium">&larr; Back to Tips</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-20 pb-12 px-4 max-w-3xl mx-auto">
        {/* Back link */}
        <Link to="/admin" className="text-sm text-brand-600 hover:text-brand-700 font-medium">&larr; Back to Tips</Link>

        {/* Featured image */}
        {blog.image_url && (
          <img
            src={`${backendUrl}${blog.image_url}`}
            alt={blog.title}
            className="w-full h-64 object-cover rounded-2xl mt-4 mb-6"
          />
        )}

        {/* Title + meta */}
        <h1 className="text-2xl font-bold text-slate-900 mb-2">{blog.title}</h1>
        <div className="flex items-center gap-3 text-xs text-slate-400 mb-6">
          <span>Topic: {blog.topic}</span>
          <span>|</span>
          <span>{new Date(blog.created_at).toLocaleDateString()}</span>
          <button onClick={handleDelete} className="ml-auto text-red-400 hover:text-red-600 transition-colors">
            Delete
          </button>
        </div>

        {/* Blog content */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{blog.content}</div>
        </div>

        {/* Podcast player */}
        {blog.audio_url && (
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h2 className="text-sm font-semibold text-slate-900 mb-3">Listen to Podcast</h2>
            <audio controls className="w-full" src={`${backendUrl}${blog.audio_url}`}>
              Your browser does not support audio playback.
            </audio>
          </div>
        )}
      </div>
    </div>
  )
}
