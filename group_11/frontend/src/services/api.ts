import type { CreditReport } from './types'

/**
 * Base URL for the FastAPI backend (no trailing slash).
 */
function apiBaseUrl(): string {
  const raw = import.meta.env.VITE_BACKEND_URL
  if (typeof raw === 'string' && raw.trim() !== '') {
    return raw.replace(/\/$/, '')
  }
  return ''
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const base = apiBaseUrl()
  const url = `${base}${path.startsWith('/') ? path : `/${path}`}`
  const response = await fetch(url, options)
  if (!response.ok) {
    const message = await response.text().catch(() => response.statusText)
    throw new Error(`API error ${response.status}: ${message}`)
  }
  return response.json() as Promise<T>
}

// ── Reports ──
export async function getSampleReport(): Promise<CreditReport> {
  return request<CreditReport>('/api/report/get')
}

// ── Chat ──
export interface ChatResponse {
  message: string
  agent_name: string
  agent_display_name: string
  session_id: string
}

export async function sendChatMessage(message: string, sessionId: string = 'default'): Promise<ChatResponse> {
  return request<ChatResponse>('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
}

export async function getChatHistory(sessionId: string): Promise<{ messages: Array<{ role: string; content: string; agent?: string }> }> {
  return request(`/api/chat/sessions/${sessionId}/history`)
}

export async function clearChatSession(sessionId: string): Promise<void> {
  await request(`/api/chat/sessions/${sessionId}`, { method: 'DELETE' })
}

// ── Dashboard ──
export interface DashboardOverview {
  credit_score: number
  credit_score_band: string
  total_debt: number
  total_overdue: number
  monthly_income: number
  monthly_expenses: number
  total_min_payments: number
  debt_count: number
  active_accounts: number
  risk_flags: string[]
  positive_factors: string[]
}

export interface Insight {
  type: 'warning' | 'critical' | 'positive' | 'tip'
  title: string
  description: string
}

export async function getDashboardOverview(): Promise<DashboardOverview> {
  return request<DashboardOverview>('/api/dashboard/overview')
}

export async function getDebtBreakdown(): Promise<{ debts: any[]; dti: any }> {
  return request('/api/dashboard/debt-breakdown')
}

export async function getPayoffPlan(): Promise<{ strategies: any[]; recommendation: string; extra_monthly_payment: number }> {
  return request('/api/dashboard/payoff-plan')
}

export async function getBudgetAnalysis(): Promise<any> {
  return request('/api/dashboard/budget-analysis')
}

export async function getInsights(): Promise<{ insights: Insight[] }> {
  return request('/api/dashboard/insights')
}

// ── Documents ──
export interface DocumentInfo {
  id: string
  filename: string
  file_type: string
  status: string
  chunks: number
}

export async function uploadDocument(file: File): Promise<{ document: DocumentInfo; message: string }> {
  const formData = new FormData()
  formData.append('file', file)
  const base = apiBaseUrl()
  const response = await fetch(`${base}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    const message = await response.text().catch(() => response.statusText)
    throw new Error(`Upload failed: ${message}`)
  }
  return response.json()
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  return request<DocumentInfo[]>('/api/documents')
}

export async function deleteDocument(docId: string): Promise<void> {
  await request(`/api/documents/${docId}`, { method: 'DELETE' })
}

// ── Blog ──
export interface BlogPost {
  id: string
  topic: string
  title: string
  content: string
  image_url: string | null
  audio_url: string | null
  created_at: string
}

export interface BlogListItem {
  id: string
  title: string
  topic: string
  image_url: string | null
  created_at: string
}

export async function generateBlog(topic: string): Promise<BlogPost> {
  return request<BlogPost>('/api/blog/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  })
}

export async function listBlogs(): Promise<BlogListItem[]> {
  return request<BlogListItem[]>('/api/blog')
}

export async function getBlog(id: string): Promise<BlogPost> {
  return request<BlogPost>(`/api/blog/${id}`)
}

export async function deleteBlog(id: string): Promise<void> {
  await request(`/api/blog/${id}`, { method: 'DELETE' })
}
