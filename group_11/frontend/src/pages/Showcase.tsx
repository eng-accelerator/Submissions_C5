import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

interface Feature {
  name: string
  description: string
  tryLink?: string
  tryLabel?: string
}

interface Category {
  title: string
  icon: string
  color: string
  features: Feature[]
}

const CATEGORIES: Category[] = [
  {
    title: 'Agent Orchestration',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
    color: 'blue',
    features: [
      {
        name: 'LangGraph',
        description: 'Multi-agent state graph — routes user queries through load_context → route → specialist → respond pipeline.',
        tryLink: '/chat',
        tryLabel: 'Try Chat',
      },
      {
        name: 'LangChain',
        description: 'LLM abstraction layer — ChatOpenAI, tool binding, message types (System, Human, AI, Tool), prompt templates.',
        tryLink: '/chat',
        tryLabel: 'Try Chat',
      },
      {
        name: 'Multi-Agent Financial Plan',
        description: 'All 4 specialist agents collaborate on one unified output — each contributes a section (snapshot, debt, budget, payoff, savings) to build a complete personalized financial plan.',
        tryLink: '/plan',
        tryLabel: 'View Plan',
      },
      {
        name: 'Agent Routing',
        description: 'Orchestrator classifies user intent and dynamically routes to one of 4 specialist agents or answers directly.',
        tryLink: '/chat',
        tryLabel: 'Try Chat',
      },
    ],
  },
  {
    title: 'AI Agents & Tool Use',
    icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    color: 'red',
    features: [
      {
        name: 'Debt Analyzer Agent',
        description: 'Analyzes debt portfolio, credit utilization, delinquencies, and risk flags with actionable recommendations.',
        tryLink: '/chat',
        tryLabel: 'Ask: "Analyze my debt"',
      },
      {
        name: 'Savings Strategist Agent',
        description: 'Creates personalized savings plans based on income, expenses, and goals. Uses the savings projection tool.',
        tryLink: '/chat',
        tryLabel: 'Ask: "Create a savings plan"',
      },
      {
        name: 'Budget Advisor Agent',
        description: 'Compares spending against 50/30/20 benchmarks. Uses the budget analysis tool for category breakdowns.',
        tryLink: '/chat',
        tryLabel: 'Ask: "Budget advice"',
      },
      {
        name: 'Payoff Optimizer Agent',
        description: 'Compares avalanche vs snowball strategies. Uses the payoff simulation tool for month-by-month projections.',
        tryLink: '/chat',
        tryLabel: 'Ask: "Compare payoff strategies"',
      },
      {
        name: 'LLM Tool Calling',
        description: 'Agents invoke calculator tools (DTI ratio, payoff simulator, savings projector, budget analyzer) — LLM decides when to call them.',
        tryLink: '/chat',
        tryLabel: 'Ask: "Calculate my DTI"',
      },
    ],
  },
  {
    title: 'RAG (Retrieval-Augmented Generation)',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    color: 'green',
    features: [
      {
        name: 'Document Ingestion',
        description: 'Upload PDF, CSV, JSON, or XLSX financial documents. Each file is parsed and split into searchable chunks.',
        tryLink: '/upload',
        tryLabel: 'Upload a file',
      },
      {
        name: 'Text Chunking',
        description: 'Documents are split into overlapping chunks — tables converted to natural language for better retrieval.',
      },
      {
        name: 'Embeddings',
        description: 'Each chunk is converted to a vector (numeric representation) using an embedding model. Enables semantic similarity search.',
      },
      {
        name: 'Vector Store & Semantic Search',
        description: 'User questions are embedded and matched against document chunks by cosine similarity. Top-K results injected into agent context.',
        tryLink: '/upload',
        tryLabel: 'Upload then Chat',
      },
    ],
  },
  {
    title: 'Generative AI & Diffusion',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
    color: 'purple',
    features: [
      {
        name: 'Text Generation (LLM)',
        description: 'LLM generates financial tips, blog content, and agent responses. Uses prompt engineering with system prompts and context injection.',
        tryLink: '/admin?mode=write',
        tryLabel: 'Write a Tip',
      },
      {
        name: 'Image Diffusion',
        description: 'AI generates images from text prompts via Pollinations.ai (diffusion model). LLM first creates an image description, then the diffusion model renders it.',
        tryLink: '/admin?mode=write',
        tryLabel: 'Generate an image',
      },
      {
        name: 'Text-to-Speech (TTS)',
        description: 'Written content is converted to spoken audio (MP3 podcast) using Google Text-to-Speech. Reverse of speech-to-text.',
        tryLink: '/admin?mode=write',
        tryLabel: 'Listen to podcast',
      },
      {
        name: 'Structured JSON Output',
        description: 'Financial Plan agents return strict JSON (not free text). Each section (snapshot, debt, budget, payoff, savings) is parsed and rendered as structured UI.',
        tryLink: '/plan',
        tryLabel: 'See structured plan',
      },
      {
        name: 'Tokenization',
        description: 'Text is split into tokens (subword units) before LLM processing. Affects cost, context window, and response quality. Handled by the model provider.',
      },
    ],
  },
  {
    title: 'Multimodal I/O',
    icon: 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
    color: 'amber',
    features: [
      {
        name: 'Image-to-Text (Vision)',
        description: 'Upload a photo of a bank statement, receipt, or credit report. Vision model (Gemini Flash) extracts all text and data, which feeds into RAG for chat.',
        tryLink: '/upload',
        tryLabel: 'Upload an image',
      },
      {
        name: 'Speech-to-Text (STT)',
        description: 'Browser Web Speech API captures voice input and converts to text. Works in Chrome/Edge; text fallback for other browsers.',
        tryLink: '/admin?mode=write',
        tryLabel: 'Speak a topic',
      },
      {
        name: 'Text-to-Image (Diffusion)',
        description: 'AI generates images from text prompts via diffusion model. LLM creates description, Pollinations.ai renders it.',
        tryLink: '/admin?mode=write',
        tryLabel: 'Generate image',
      },
      {
        name: 'Text-to-Speech (Audio)',
        description: 'Written content converted to spoken podcast audio (MP3) via Google TTS. Playable in-browser.',
        tryLink: '/admin',
        tryLabel: 'Play podcast',
      },
    ],
  },
  {
    title: 'LLM Infrastructure',
    icon: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2',
    color: 'slate',
    features: [
      {
        name: 'OpenRouter',
        description: 'Multi-model API gateway — access Google Gemini, Llama, DeepSeek, Claude, GPT via a single API key. Swap models in .env without code changes.',
      },
      {
        name: 'Prompt Engineering',
        description: 'Each agent has a tailored system prompt with financial context injection. Orchestrator uses a routing prompt to classify intent.',
        tryLink: '/chat',
        tryLabel: 'See agents respond',
      },
      {
        name: 'Temperature Control',
        description: 'Agents use 0.1 (deterministic, factual). Tip generation uses 0.7 (creative). Configurable via AGENT_TEMPERATURE in .env.',
      },
      {
        name: 'Configurable Provider',
        description: 'Switch between OpenRouter and OpenAI by changing LLM_PROVIDER in .env. All config centralized — no code changes needed.',
      },
    ],
  },
  {
    title: 'Observability & Monitoring',
    icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    color: 'indigo',
    features: [
      {
        name: 'LangSmith Tracing',
        description: 'Every LLM call, tool execution, and agent routing step is traced. View latency, tokens, prompts, and responses in the LangSmith dashboard.',
        tryLink: '/health',
        tryLabel: 'Check status',
      },
      {
        name: 'API Health Monitor',
        description: 'Real-time endpoint health check page — tests all 8+ API endpoints, shows response times, integration status.',
        tryLink: '/health',
        tryLabel: 'View Health',
      },
    ],
  },
  {
    title: 'Integrations & Automation',
    icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
    color: 'orange',
    features: [
      {
        name: 'n8n',
        description: 'Send your generated financial plan to any email via an n8n workflow webhook. Frontend posts plan content and email address directly to the configured n8n endpoint.',
        tryLink: '/plan',
        tryLabel: 'Send Plan',
      },
      {
        name: 'Configurable Webhook URL',
        description: 'n8n integration is opt-in — set VITE_N8N_WEBHOOK_URL in your environment to enable the "Send via Email" button on the Plan page. No backend changes needed.',
      },
    ],
  },
  {
    title: 'Data & Session Management',
    icon: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4',
    color: 'teal',
    features: [
      {
        name: 'Conversation Memory',
        description: 'Chat maintains a 20-message sliding window per session. Agents see conversation history for contextual follow-ups.',
        tryLink: '/chat',
        tryLabel: 'Have a conversation',
      },
      {
        name: 'Financial Profile',
        description: 'Credit score, debt records, income, and expenses loaded per session from sample data (or uploaded documents via RAG).',
        tryLink: '/dashboard',
        tryLabel: 'View Dashboard',
      },
      {
        name: 'Static Media Serving',
        description: 'Generated images and audio files stored in backend/data/blogs/ and served via FastAPI static mount at /media/.',
        tryLink: '/admin',
        tryLabel: 'View Tips',
      },
    ],
  },
]

const COLOR_MAP: Record<string, { bg: string; border: string; icon: string; badge: string }> = {
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-600 bg-blue-100', badge: 'bg-blue-100 text-blue-700' },
  red: { bg: 'bg-red-50', border: 'border-red-200', icon: 'text-red-600 bg-red-100', badge: 'bg-red-100 text-red-700' },
  green: { bg: 'bg-green-50', border: 'border-green-200', icon: 'text-green-600 bg-green-100', badge: 'bg-green-100 text-green-700' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', icon: 'text-purple-600 bg-purple-100', badge: 'bg-purple-100 text-purple-700' },
  amber: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'text-amber-600 bg-amber-100', badge: 'bg-amber-100 text-amber-700' },
  slate: { bg: 'bg-slate-50', border: 'border-slate-200', icon: 'text-slate-600 bg-slate-100', badge: 'bg-slate-100 text-slate-700' },
  indigo: { bg: 'bg-indigo-50', border: 'border-indigo-200', icon: 'text-indigo-600 bg-indigo-100', badge: 'bg-indigo-100 text-indigo-700' },
  teal: { bg: 'bg-teal-50', border: 'border-teal-200', icon: 'text-teal-600 bg-teal-100', badge: 'bg-teal-100 text-teal-700' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', icon: 'text-orange-600 bg-orange-100', badge: 'bg-orange-100 text-orange-700' },
}

export default function Showcase() {
  const totalFeatures = CATEGORIES.reduce((acc, c) => acc + c.features.length, 0)

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="pt-20 pb-12 px-4 max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-slate-900 mb-3">AI Showcase</h1>
          <p className="text-slate-500 max-w-2xl mx-auto">
            Every AI feature, framework, and technique used in DemoAI — with links to try each one live.
          </p>
          <div className="flex items-center justify-center gap-4 mt-4">
            <span className="text-sm text-slate-400">{CATEGORIES.length} categories</span>
            <span className="text-slate-300">|</span>
            <span className="text-sm text-slate-400">{totalFeatures} features</span>
          </div>
        </div>

        {/* Tech stack pills */}
        <div className="flex flex-wrap justify-center gap-2 mb-10">
          {['LangGraph', 'LangChain', 'LangSmith', 'OpenRouter', 'RAG', 'Embeddings', 'Tool Use', 'Vision', 'Diffusion', 'TTS', 'STT', 'Multimodal', 'Structured Output', 'Multi-Agent Financial Plan', 'Memory', 'Multi-Agent Pipeline', 'Tokenization', 'Prompt Engineering', 'n8n Webhook'].map((t) => (
            <span key={t} className="px-3 py-1 text-xs font-medium rounded-full bg-brand-50 text-brand-700 border border-brand-100">
              {t}
            </span>
          ))}
        </div>

        {/* Categories */}
        <div className="space-y-8">
          {CATEGORIES.map((cat) => {
            const colors = COLOR_MAP[cat.color] || COLOR_MAP.slate
            return (
              <section key={cat.title}>
                <div className="flex items-center gap-3 mb-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${colors.icon}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={cat.icon} />
                    </svg>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900">{cat.title}</h2>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge}`}>
                    {cat.features.length}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {cat.features.map((feat) => (
                    <div
                      key={feat.name}
                      className={`${colors.bg} ${colors.border} border rounded-xl p-4`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <h3 className="text-sm font-semibold text-slate-900">{feat.name}</h3>
                        {feat.tryLink && (
                          <Link
                            to={feat.tryLink}
                            className={`flex-shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${colors.badge} hover:opacity-80 transition-opacity`}
                          >
                            {feat.tryLabel || 'Try it'}
                          </Link>
                        )}
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">{feat.description}</p>
                    </div>
                  ))}
                </div>
              </section>
            )
          })}
        </div>
      </div>
    </div>
  )
}
