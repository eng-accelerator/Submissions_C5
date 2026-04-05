# DemoAI - AI Financial Coach Agent Platform

## Plan, Architecture & Deployment Guide

---

## 1. Vision

A **multi-agent AI financial advisor** that ingests user financial documents (credit reports, bank statements, pay stubs), builds a personal financial profile, and delivers:

- **Debt Analyzer Agent** - Analyzes debt portfolio, identifies high-risk accounts, recommends payoff strategies (avalanche, snowball, hybrid)
- **Savings Strategy Agent** - Personalized savings plans based on income, expenses, and goals
- **Budget Advisor Agent** - Actionable budget recommendations with category-level insights
- **Debt Payoff Optimizer Agent** - Optimized payoff schedules with projected timelines and interest savings
- **Orchestrator Agent** - Routes user queries to the right specialist agent, maintains conversation context

All agents share a common financial profile built from uploaded documents via **Tabular RAG** (structured data extraction + vector retrieval).

---

## 2. Current State (MVP)

| Layer | Status | What Exists |
|-------|--------|-------------|
| Backend | FastAPI skeleton | Health check, sample credit report endpoint, Supabase JWT utility |
| Frontend | React + Vite | Landing page, credit report viewer, Google OAuth via Supabase |
| Database | None | Placeholder Supabase config, no tables |
| AI/Agents | None | Placeholder API keys in .env, no LangChain/LangGraph code |
| Deployment | Partial | Render (backend), Vercel (frontend), Supabase (auth only) |

---

## 3. Target Architecture

```
                                    FRONTEND (Vercel)
                                    React + Vite + Tailwind
                                    ┌──────────────────────────┐
                                    │  Pages:                  │
                                    │  - Landing               │
                                    │  - Dashboard (NEW)       │
                                    │  - Chat (NEW)            │
                                    │  - Report Viewer         │
                                    │  - Upload Documents (NEW)│
                                    └──────────┬───────────────┘
                                               │ HTTPS / WSS
                                               ▼
                                    BACKEND (Render)
                                    FastAPI + LangGraph
                                    ┌──────────────────────────┐
                                    │  API Layer               │
                                    │  ├── /api/auth/*         │
                                    │  ├── /api/report/*       │
                                    │  ├── /api/documents/*    │
                                    │  ├── /api/chat/*         │
                                    │  ├── /api/agents/*       │
                                    │  └── /api/dashboard/*    │
                                    │                          │
                                    │  Agent Orchestration     │
                                    │  (LangGraph StateGraph)  │
                                    │  ┌────────────────────┐  │
                                    │  │   Orchestrator     │  │
                                    │  │   ┌─────┬─────┐   │  │
                                    │  │   │Debt │Savngs│   │  │
                                    │  │   │Anlzr│Strtgy│   │  │
                                    │  │   ├─────┼─────┤   │  │
                                    │  │   │Budgt│Payoff│   │  │
                                    │  │   │Advsr│Optmzr│   │  │
                                    │  │   └─────┴─────┘   │  │
                                    │  └────────────────────┘  │
                                    │                          │
                                    │  RAG Pipeline            │
                                    │  (LangChain)             │
                                    │  ├── Document Loader     │
                                    │  ├── Tabular Extractor   │
                                    │  ├── Embeddings          │
                                    │  └── Vector Store        │
                                    └──────────┬───────────────┘
                                               │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                  ▼
                        SUPABASE            SUPABASE           LANGSMITH
                        Auth + DB           Storage            Observability
                        ┌──────────┐        ┌──────────┐      ┌──────────┐
                        │ Users    │        │ Documents│      │ Traces   │
                        │ Profiles │        │ (PDFs,   │      │ Evals    │
                        │ Sessions │        │  CSVs)   │      │ Metrics  │
                        │ Fin Data │        └──────────┘      └──────────┘
                        └──────────┘
```

---

## 4. Directory Structure (Target)

```
demoai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, CORS, lifespan
│   │   ├── settings.py                # All config from .env (single source)
│   │   ├── dependencies.py            # FastAPI dependency injection
│   │   │
│   │   ├── routes/                    # API endpoints (thin controllers)
│   │   │   ├── __init__.py
│   │   │   ├── reports.py             # Credit report endpoints
│   │   │   ├── documents.py           # Document upload & processing
│   │   │   ├── chat.py                # Agent chat (streaming)
│   │   │   ├── dashboard.py           # Dashboard data endpoints
│   │   │   └── health.py              # Health check
│   │   │
│   │   ├── agents/                    # LangGraph agent definitions
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py        # Router agent (LangGraph StateGraph)
│   │   │   ├── debt_analyzer.py       # Debt analysis specialist
│   │   │   ├── savings_strategist.py  # Savings strategy specialist
│   │   │   ├── budget_advisor.py      # Budget advice specialist
│   │   │   ├── payoff_optimizer.py    # Debt payoff optimization
│   │   │   ├── state.py              # Shared agent state schema
│   │   │   ├── tools.py              # Agent tools (DB queries, calculations)
│   │   │   └── prompts.py            # System prompts for each agent
│   │   │
│   │   ├── rag/                       # RAG pipeline
│   │   │   ├── __init__.py
│   │   │   ├── loader.py             # Document loaders (PDF, CSV, JSON)
│   │   │   ├── extractor.py          # Tabular data extraction
│   │   │   ├── embeddings.py         # Embedding model config
│   │   │   ├── vectorstore.py        # Vector store operations
│   │   │   └── retriever.py          # Retrieval chain
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py   # Document processing orchestration
│   │   │   ├── profile_service.py    # Financial profile management
│   │   │   ├── session_service.py    # Chat session & memory management
│   │   │   └── dashboard_service.py  # Dashboard aggregation
│   │   │
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── credit_report.py      # (existing)
│   │   │   ├── financial_profile.py  # User financial profile
│   │   │   ├── chat.py               # Chat request/response models
│   │   │   └── document.py           # Document upload models
│   │   │
│   │   ├── db/                        # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── client.py             # Supabase client singleton
│   │   │   ├── repositories.py       # Data access (profiles, sessions, docs)
│   │   │   └── migrations/           # SQL migration files
│   │   │       ├── 001_users_profiles.sql
│   │   │       ├── 002_documents.sql
│   │   │       ├── 003_chat_sessions.sql
│   │   │       └── 004_financial_data.sql
│   │   │
│   │   ├── utils/
│   │   │   ├── auth.py               # (existing) Supabase JWT verification
│   │   │   └── calculations.py       # Financial math utilities
│   │   │
│   │   └── data/
│   │       └── sample_credit_score.json
│   │
│   ├── tests/                         # Backend tests
│   │   ├── conftest.py
│   │   ├── test_agents/
│   │   ├── test_rag/
│   │   └── test_routes/
│   │
│   ├── .env                           # Local dev (git-ignored)
│   ├── .env.example                   # Template with all keys documented
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Container build
│   └── render.yaml                    # Render.com config
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx            # (existing)
│   │   │   ├── SampleReport.tsx       # (existing)
│   │   │   ├── Dashboard.tsx          # NEW - Financial dashboard
│   │   │   ├── Chat.tsx               # NEW - Agent chat interface
│   │   │   └── Upload.tsx             # NEW - Document upload
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.tsx             # (existing, extend)
│   │   │   ├── ScoreGauge.tsx         # (existing)
│   │   │   ├── report/               # (existing)
│   │   │   ├── chat/                  # NEW
│   │   │   │   ├── ChatWindow.tsx     # Message thread + streaming
│   │   │   │   ├── MessageBubble.tsx  # Individual message
│   │   │   │   ├── AgentBadge.tsx     # Shows which agent responded
│   │   │   │   └── SuggestedQuestions.tsx
│   │   │   ├── dashboard/            # NEW
│   │   │   │   ├── DebtOverview.tsx   # Debt summary cards
│   │   │   │   ├── BudgetChart.tsx    # Budget breakdown (chart)
│   │   │   │   ├── PayoffTimeline.tsx # Debt payoff projection
│   │   │   │   ├── SavingsGoals.tsx   # Savings tracker
│   │   │   │   └── InsightCards.tsx   # AI-generated insights
│   │   │   └── upload/               # NEW
│   │   │       ├── DropZone.tsx       # Drag-and-drop file upload
│   │   │       └── ProcessingStatus.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # (existing)
│   │   │   ├── useChat.ts            # NEW - Chat with streaming
│   │   │   └── useDashboard.ts       # NEW - Dashboard data fetching
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                # (existing, extend)
│   │   │   └── types.ts              # (existing, extend)
│   │   │
│   │   ├── lib/
│   │   │   └── supabase.ts           # (existing)
│   │   │
│   │   └── ...
│   │
│   └── ...
│
├── db/
│   └── schema.sql                     # Full Supabase schema (reference)
│
├── docs/
│   ├── ARCHITECTURE.md                # This plan (detailed version)
│   └── AGENTS.md                      # Agent design & prompt docs
│
├── scripts/
│   ├── setup.sh                       # Local dev setup
│   ├── migrate.sh                     # Run DB migrations against Supabase
│   └── seed.sh                        # Seed sample data
│
├── .env.example                       # Root-level template (references backend/frontend)
├── PLAN.md                            # This file
└── README.md
```

---

## 5. Configuration Strategy (.env)

**Principle**: Every secret, URL, feature flag, and tunable parameter lives in `.env`. Code reads from `settings.py` only. No hardcoded keys anywhere.

### Backend `.env` (single file, all config)

```bash
# ============================================================
# DemoAI Backend Configuration
# Copy to .env and fill in values. NEVER commit .env itself.
# ============================================================

# --- App ---
APP_ENV=development                          # development | staging | production
APP_DEBUG=true                               # Enable debug logging
APP_PORT=8001                                # Uvicorn port

# --- CORS ---
CORS_ALLOWED_ORIGINS=http://localhost:5173   # Comma-separated frontend origins

# --- Supabase (Auth + DB + Storage) ---
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...                     # Public anon key (frontend parity)
SUPABASE_SERVICE_ROLE_KEY=eyJ...             # Server-only, never expose to client

# --- LLM Provider ---
LLM_PROVIDER=openai                          # openai | anthropic | azure_openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o                          # Model for agent reasoning
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# (Optional) Anthropic as alternative
# ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-sonnet-4-20250514

# (Optional) Azure OpenAI
# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_DEPLOYMENT=
# AZURE_OPENAI_API_VERSION=2024-02-01

# --- LangSmith (Observability) ---
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...                   # smith.langchain.com API key
LANGCHAIN_PROJECT=demoai                     # Project name in LangSmith
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# --- Vector Store ---
VECTOR_STORE_PROVIDER=supabase               # supabase | chroma | pinecone
# If using Supabase pgvector, no extra config needed (uses SUPABASE_* above)
# If using Pinecone:
# PINECONE_API_KEY=
# PINECONE_INDEX=demoai

# --- Document Processing ---
MAX_UPLOAD_SIZE_MB=10                        # Max document size
ALLOWED_FILE_TYPES=pdf,csv,json,xlsx         # Accepted file extensions

# --- Agent Config ---
AGENT_MAX_ITERATIONS=15                      # Max LangGraph steps per query
AGENT_TEMPERATURE=0.1                        # LLM temperature for agents
AGENT_TIMEOUT_SECONDS=120                    # Per-query timeout

# --- Session / Memory ---
SESSION_TTL_HOURS=24                         # Chat session expiry
MAX_MEMORY_MESSAGES=50                       # Messages kept in agent memory
```

### Frontend `.env`

```bash
# ============================================================
# DemoAI Frontend Configuration
# ============================================================

VITE_APP_NAME=DemoAI
VITE_BACKEND_URL=http://localhost:8001       # Backend API base URL
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...               # Public anon key ONLY
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8001 # Vite dev proxy target
```

### Settings.py (backend single source of truth)

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=..., extra="ignore")

    # App
    app_env: str = "development"
    app_debug: bool = False
    app_port: int = 8001

    # CORS
    cors_allowed_origins: str

    # Supabase
    supabase_url: str
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # LLM
    llm_provider: str = "openai"           # Swap provider without code changes
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "demoai"

    # Vector Store
    vector_store_provider: str = "supabase"

    # Agents
    agent_max_iterations: int = 15
    agent_temperature: float = 0.1
    agent_timeout_seconds: int = 120

    # Session
    session_ttl_hours: int = 24
    max_memory_messages: int = 50

    # Documents
    max_upload_size_mb: int = 10
    allowed_file_types: str = "pdf,csv,json,xlsx"
```

This design means:
- **Swap LLM provider** by changing `LLM_PROVIDER` + adding the right API key
- **Swap vector store** by changing `VECTOR_STORE_PROVIDER`
- **Disable tracing** by setting `LANGCHAIN_TRACING_V2=false`
- **No code changes needed** for configuration switches

---

## 6. Database Schema (Supabase / PostgreSQL)

```sql
-- Enable pgvector extension (for RAG)
create extension if not exists vector;

-- ===========================
-- 1. User Financial Profiles
-- ===========================
create table public.financial_profiles (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    
    -- Income
    monthly_income numeric(12,2),
    income_sources jsonb default '[]',
    
    -- Spending summary (auto-computed from documents)
    monthly_expenses numeric(12,2),
    expense_categories jsonb default '{}',
    
    -- Credit
    credit_score int,
    credit_score_band text,
    total_debt numeric(12,2),
    
    -- Metadata
    last_updated_at timestamptz default now(),
    created_at timestamptz default now(),
    
    unique(user_id)
);

-- ===========================
-- 2. Uploaded Documents
-- ===========================
create table public.documents (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    
    file_name text not null,
    file_type text not null,                -- pdf, csv, json, xlsx
    storage_path text not null,             -- Supabase Storage path
    document_type text,                     -- credit_report, bank_statement, pay_stub, etc.
    
    -- Processing status
    status text default 'uploaded',         -- uploaded, processing, processed, failed
    processed_data jsonb,                   -- Extracted structured data
    error_message text,
    
    created_at timestamptz default now(),
    processed_at timestamptz
);

-- ===========================
-- 3. Debt Records (extracted)
-- ===========================
create table public.debt_records (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    document_id uuid references public.documents(id) on delete set null,
    
    lender text not null,
    account_type text,                      -- credit_card, personal_loan, mortgage, etc.
    principal numeric(12,2),
    current_balance numeric(12,2),
    interest_rate numeric(5,2),
    minimum_payment numeric(12,2),
    monthly_payment numeric(12,2),
    status text,                            -- current, delinquent, written_off, closed
    due_date int,                           -- Day of month
    
    created_at timestamptz default now()
);

-- ===========================
-- 4. Chat Sessions
-- ===========================
create table public.chat_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    
    title text,
    is_active boolean default true,
    
    created_at timestamptz default now(),
    last_message_at timestamptz default now()
);

-- ===========================
-- 5. Chat Messages
-- ===========================
create table public.chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references public.chat_sessions(id) on delete cascade,
    
    role text not null,                     -- user, assistant, system, tool
    content text not null,
    agent_name text,                        -- Which agent responded (debt_analyzer, etc.)
    metadata jsonb default '{}',            -- Tool calls, confidence, sources
    
    created_at timestamptz default now()
);

-- ===========================
-- 6. Document Embeddings (RAG)
-- ===========================
create table public.document_embeddings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    document_id uuid references public.documents(id) on delete cascade,
    
    content text not null,                  -- Original text chunk
    metadata jsonb default '{}',            -- Source, page, table info
    embedding vector(1536),                 -- OpenAI text-embedding-3-small dimension
    
    created_at timestamptz default now()
);

-- Vector similarity search index
create index on public.document_embeddings
    using ivfflat (embedding vector_cosine_ops) with (lists = 100);

-- ===========================
-- Row Level Security (RLS)
-- ===========================
alter table public.financial_profiles enable row level security;
alter table public.documents enable row level security;
alter table public.debt_records enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.document_embeddings enable row level security;

-- Users can only access their own data
create policy "Users access own profiles"
    on public.financial_profiles for all
    using (auth.uid() = user_id);

create policy "Users access own documents"
    on public.documents for all
    using (auth.uid() = user_id);

create policy "Users access own debt records"
    on public.debt_records for all
    using (auth.uid() = user_id);

create policy "Users access own chat sessions"
    on public.chat_sessions for all
    using (auth.uid() = user_id);

create policy "Users access own chat messages"
    on public.chat_messages for all
    using (
        session_id in (
            select id from public.chat_sessions where user_id = auth.uid()
        )
    );

create policy "Users access own embeddings"
    on public.document_embeddings for all
    using (auth.uid() = user_id);

-- ===========================
-- Supabase Storage Bucket
-- ===========================
-- Create via Supabase Dashboard or API:
-- Bucket: "user-documents" (private, 10MB max)
-- Policy: Users can only upload/read their own files (path prefix = user_id)
```

---

## 7. Agent Architecture (LangGraph)

### 7.1 State Schema

```python
# backend/app/agents/state.py
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class FinancialAgentState(TypedDict):
    # Conversation
    messages: Annotated[list, add_messages]
    
    # User context (loaded at start of each session)
    user_id: str
    financial_profile: dict          # From Supabase
    debt_records: list[dict]         # From Supabase
    
    # RAG context
    retrieved_documents: list[str]   # Relevant document chunks
    
    # Routing
    current_agent: str               # Which specialist is active
    needs_routing: bool              # Should orchestrator re-route?
    
    # Output
    agent_response: str              # Final response to user
    confidence: float                # Agent's confidence in response
```

### 7.2 Agent Graph

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Load User  │  ← Fetch profile + debts from Supabase
                    │  Context    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  RAG        │  ← Retrieve relevant document chunks
                    │  Retrieval  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
              ┌─────│ Orchestrator│─────┐
              │     │  (Router)   │     │
              │     └──────┬──────┘     │
              │            │            │
     ┌────────▼───┐ ┌─────▼─────┐ ┌───▼────────┐
     │   Debt     │ │  Savings  │ │  Budget    │
     │  Analyzer  │ │ Strategist│ │  Advisor   │
     └────────┬───┘ └─────┬─────┘ └───┬────────┘
              │            │            │
              │     ┌──────▼──────┐    │
              ├─────│  Payoff     │────┘
              │     │  Optimizer  │
              │     └──────┬──────┘
              │            │
              └─────┬──────┘
                    │
             ┌──────▼──────┐
             │  Format     │  ← Structure response, cite sources
             │  Response   │
             └──────┬──────┘
                    │
             ┌──────▼──────┐
             │    END      │
             └─────────────┘
```

### 7.3 Agent Responsibilities

| Agent | Input | Output | Tools |
|-------|-------|--------|-------|
| **Orchestrator** | User message + context | Route decision | `classify_intent` |
| **Debt Analyzer** | Debt records, credit report | Risk assessment, debt breakdown | `query_debts`, `calculate_dti`, `rag_search` |
| **Savings Strategist** | Income, expenses, goals | Savings plan with milestones | `query_profile`, `project_savings`, `rag_search` |
| **Budget Advisor** | Income, expense categories | Budget recommendations | `query_expenses`, `compare_benchmarks`, `rag_search` |
| **Payoff Optimizer** | Debt records, available cash | Optimal payoff schedule | `query_debts`, `simulate_payoff`, `rag_search` |

### 7.4 Agent Tools (LangChain Tools)

```python
# Defined in backend/app/agents/tools.py

@tool
def query_financial_profile(user_id: str) -> dict:
    """Fetch user's financial profile from database."""

@tool
def query_debt_records(user_id: str) -> list[dict]:
    """Fetch all debt records for a user."""

@tool
def calculate_debt_to_income(user_id: str) -> dict:
    """Calculate debt-to-income ratio and related metrics."""

@tool
def simulate_payoff(debts: list[dict], strategy: str, extra_payment: float) -> dict:
    """Simulate debt payoff with avalanche/snowball/hybrid strategy.
    Returns timeline, total interest, and monthly schedule."""

@tool
def project_savings(monthly_savings: float, months: int, rate: float) -> dict:
    """Project savings growth with compound interest."""

@tool
def compare_budget_benchmarks(income: float, categories: dict) -> dict:
    """Compare spending categories against recommended benchmarks (50/30/20 etc)."""

@tool
def rag_search(user_id: str, query: str) -> list[str]:
    """Search user's uploaded documents for relevant information."""
```

---

## 8. RAG Pipeline

### 8.1 Document Ingestion Flow

```
Upload (PDF/CSV/JSON/XLSX)
    │
    ▼
Store in Supabase Storage
    │
    ▼
Extract Text/Tables
    ├── PDF → PyMuPDF / pdfplumber (tables)
    ├── CSV → pandas DataFrame
    ├── JSON → structured parse
    └── XLSX → openpyxl → pandas
    │
    ▼
Tabular RAG Processing
    ├── Convert tables to natural language descriptions
    ├── Extract key financial metrics (debts, income, etc.)
    └── Chunk text (500 tokens, 50 token overlap)
    │
    ▼
Generate Embeddings (OpenAI text-embedding-3-small)
    │
    ▼
Store in Supabase pgvector (document_embeddings table)
    │
    ▼
Update Financial Profile (structured data → financial_profiles, debt_records)
```

### 8.2 Tabular RAG Strategy

Standard RAG struggles with tables. Our approach:

1. **Table Detection** - Identify tables in PDFs/CSVs
2. **Table-to-Text** - Convert each row to a natural language statement:
   - `"HDFC Credit Card: balance ₹45,000, limit ₹1,50,000, utilization 30%, status Active"`
3. **Structured Extraction** - Also parse into typed records (debt_records table)
4. **Dual Retrieval** - Agents can use both:
   - `rag_search` for semantic similarity over text
   - `query_debt_records` for exact structured queries

---

## 9. Session & Memory

### Conversation Memory

Each chat session maintains:
1. **Message History** - Stored in `chat_messages` table (persists across reconnects)
2. **LangGraph Checkpointer** - Uses `langgraph.checkpoint.postgres` for graph state
3. **Windowed Context** - Last N messages sent to LLM (configurable via `MAX_MEMORY_MESSAGES`)

### User Context (per-session)

At session start, the orchestrator loads:
- Financial profile (income, expenses, credit score)
- Debt records (all active debts)
- Recent chat summary (if continuing a session)

This avoids re-fetching on every message and keeps agent context rich.

### Session Lifecycle

```
New Session → Load Context → Chat (multiple messages) → Session Expires (TTL)
                                     │
                                     ├── Each message: append to chat_messages
                                     ├── Agent state: checkpointed in LangGraph
                                     └── Profile updates: written to financial_profiles
```

---

## 10. API Design

### New Endpoints

```
# Documents
POST   /api/documents/upload          Upload a financial document
GET    /api/documents                  List user's documents
GET    /api/documents/{id}/status      Check processing status
DELETE /api/documents/{id}             Remove a document

# Chat (Agent Interaction)
POST   /api/chat/sessions              Create a new chat session
GET    /api/chat/sessions              List user's sessions
POST   /api/chat/sessions/{id}/message Send message (SSE streaming response)
GET    /api/chat/sessions/{id}/history Get message history

# Dashboard
GET    /api/dashboard/overview         Financial overview (score, debt, income)
GET    /api/dashboard/debt-breakdown   Debt by category/lender
GET    /api/dashboard/budget-analysis  Budget vs. benchmarks
GET    /api/dashboard/payoff-plan      Current recommended payoff plan
GET    /api/dashboard/insights         AI-generated insights (cached)

# Profile
GET    /api/profile                    Get financial profile
PUT    /api/profile                    Update profile (manual entries)
```

### Streaming Chat (SSE)

```python
@router.post("/sessions/{session_id}/message")
async def send_message(session_id: str, body: ChatMessageRequest, user=Depends(get_current_user)):
    async def event_stream():
        async for event in orchestrator.astream(state, config):
            if "agent_name" in event:
                yield f"data: {json.dumps({'type': 'agent', 'name': event['agent_name']})}\n\n"
            if "content" in event:
                yield f"data: {json.dumps({'type': 'token', 'content': event['content']})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

## 11. Frontend Pages (New)

### Dashboard Page
- **Score card** - Credit score gauge (existing component) + trend
- **Debt overview** - Total debt, DTI ratio, monthly obligations
- **Budget chart** - Spending by category vs. benchmarks (recharts/chart.js)
- **Payoff timeline** - Projected debt-free date with graph
- **AI insights** - 3-5 actionable tips from agents (cached, refreshed daily)

### Chat Page
- **Chat window** - Message thread with streaming responses
- **Agent badges** - Shows which specialist agent is responding
- **Suggested questions** - Quick-start prompts ("Analyze my debt", "Create a savings plan")
- **Source citations** - Links back to uploaded documents

### Upload Page
- **Drag-and-drop zone** - Accept PDF, CSV, JSON, XLSX
- **Processing status** - Real-time status updates
- **Document list** - Previously uploaded documents with type tags

---

## 12. Implementation Phases

### Phase 1: Foundation (Week 1-2)
> Goal: Database, auth enforcement, document upload

- [ ] Set up Supabase schema (run migrations)
- [ ] Expand `settings.py` with all new config
- [ ] Implement Supabase DB client + repositories
- [ ] Enforce JWT auth on all API routes
- [ ] Document upload endpoint + Supabase Storage integration
- [ ] Basic document processing (PDF text extraction)
- [ ] Frontend: Upload page with drag-and-drop
- [ ] Frontend: Protected routes (redirect to login if unauthenticated)

### Phase 2: RAG Pipeline (Week 2-3)
> Goal: Document ingestion, embeddings, retrieval

- [ ] Install LangChain dependencies (`langchain`, `langchain-openai`, `langchain-community`)
- [ ] Document loaders (PDF, CSV, JSON, XLSX)
- [ ] Tabular data extractor (table-to-text)
- [ ] Embedding generation + pgvector storage
- [ ] Retrieval chain with user-scoped filtering
- [ ] Financial profile auto-population from documents
- [ ] LangSmith tracing integration

### Phase 3: Agent System (Week 3-5)
> Goal: LangGraph multi-agent orchestration

- [ ] Install LangGraph (`langgraph`, `langgraph-checkpoint-postgres`)
- [ ] Define agent state schema
- [ ] Implement Orchestrator (intent classification + routing)
- [ ] Implement Debt Analyzer agent
- [ ] Implement Savings Strategist agent
- [ ] Implement Budget Advisor agent
- [ ] Implement Payoff Optimizer agent
- [ ] Agent tools (DB queries, calculations, RAG search)
- [ ] Chat session management + message persistence
- [ ] SSE streaming endpoint

### Phase 4: Dashboard & Frontend (Week 5-6)
> Goal: Live dashboard, chat UI, polish

- [ ] Dashboard API endpoints (aggregation queries)
- [ ] Frontend: Dashboard page with charts
- [ ] Frontend: Chat page with streaming + agent badges
- [ ] Frontend: Suggested questions + source citations
- [ ] Frontend: Navigation updates (dashboard, chat, upload links)
- [ ] Responsive design pass

### Phase 5: Polish & Deploy (Week 6-7)
> Goal: Production-ready deployment

- [ ] Error handling + graceful degradation
- [ ] Rate limiting on chat endpoints
- [ ] Caching for dashboard insights
- [ ] Backend tests (agents, RAG, routes)
- [ ] Frontend tests (key flows)
- [ ] Update Render config (new dependencies, env vars)
- [ ] Update Vercel config (new routes)
- [ ] Production environment variables
- [ ] LangSmith monitoring dashboards
- [ ] README + demo documentation

---

## 13. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        PRODUCTION                            │
│                                                              │
│  Vercel (Frontend)          Render (Backend)                 │
│  ┌──────────────┐          ┌──────────────────┐             │
│  │ React + Vite │ ──API──▶ │ FastAPI + Uvicorn│             │
│  │ Static CDN   │          │ + LangGraph      │             │
│  │              │          │ + LangChain      │             │
│  │ ENV:         │          │                  │             │
│  │ VITE_BACKEND │          │ ENV:             │             │
│  │ VITE_SUPA_*  │          │ All backend .env │             │
│  └──────────────┘          └────────┬─────────┘             │
│                                     │                        │
│              ┌──────────────────────┼──────────┐            │
│              ▼                      ▼          ▼            │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────┐     │
│  │    Supabase      │  │  Supabase    │  │LangSmith │     │
│  │  PostgreSQL +    │  │  Storage     │  │Tracing   │     │
│  │  pgvector + Auth │  │  (Documents) │  │          │     │
│  └──────────────────┘  └──────────────┘  └──────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Render Configuration (backend)

```yaml
# render.yaml
services:
  - type: web
    name: demoai-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: CORS_ALLOWED_ORIGINS
        value: https://demoai-one.vercel.app
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: LANGCHAIN_API_KEY
        sync: false
      - key: LANGCHAIN_TRACING_V2
        value: "true"
      - key: LANGCHAIN_PROJECT
        value: demoai
      - key: LLM_PROVIDER
        value: openai
      - key: OPENAI_MODEL
        value: gpt-4o
      - key: VECTOR_STORE_PROVIDER
        value: supabase
      - key: APP_ENV
        value: production
      - key: APP_DEBUG
        value: "false"
    healthCheckPath: /health
    plan: starter  # Upgrade if needed for memory (LangGraph can be RAM-heavy)
```

### Vercel Configuration (frontend)

```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://demoai-1awa.onrender.com/api/:path*" }
  ]
}
```

Set environment variables in Vercel dashboard:
- `VITE_BACKEND_URL` = `https://demoai-1awa.onrender.com`
- `VITE_SUPABASE_URL` = your Supabase URL
- `VITE_SUPABASE_ANON_KEY` = your Supabase anon key

---

## 14. Python Dependencies (Target)

```
# requirements.txt

# --- Framework ---
fastapi==0.115.12
uvicorn[standard]==0.34.0
python-dotenv==1.0.1
pydantic==2.12.0
pydantic-settings==2.7.0
httpx==0.28.1
python-multipart==0.0.18          # File uploads

# --- LangChain + LangGraph ---
langchain>=0.3.0
langchain-openai>=0.3.0
langchain-community>=0.3.0
langgraph>=0.3.0
langgraph-checkpoint-postgres>=0.1.0

# --- RAG / Document Processing ---
pymupdf>=1.25.0                    # PDF text + table extraction
pdfplumber>=0.11.0                 # PDF table extraction (fallback)
pandas>=2.2.0                      # Tabular data processing
openpyxl>=3.1.0                    # Excel file support

# --- Database ---
supabase>=2.0.0                    # Supabase Python client
vecs>=0.4.0                        # Supabase pgvector helper

# --- Observability ---
langsmith>=0.2.0

# --- Testing ---
pytest>=8.0.0
pytest-asyncio>=0.24.0
```

---

## 15. Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| **LLM Config** | `.env` driven, provider-agnostic factory | Swap OpenAI ↔ Anthropic without code changes |
| **Vector Store** | Supabase pgvector | Already using Supabase; no extra service to manage |
| **Agent Framework** | LangGraph (not raw LangChain agents) | Explicit state machine > implicit ReAct loops; better debugging |
| **Streaming** | SSE (Server-Sent Events) | Simpler than WebSockets for unidirectional streaming; works through Vercel rewrites |
| **Auth** | Supabase JWT (enforced) | Already scaffolded; RLS gives per-user data isolation for free |
| **Document Storage** | Supabase Storage | Unified platform; presigned URLs for secure access |
| **Tabular RAG** | Table-to-text + structured extraction | Dual approach handles both semantic queries and exact lookups |
| **Session Memory** | DB-backed (chat_messages) + LangGraph checkpointer | Survives restarts; pageable history; checkpoints enable graph replay |
| **Deployment** | Render (backend) + Vercel (frontend) + Supabase (data) | Already set up; free tiers for demo; easy to migrate later |

---

## 16. Decoupling Strategy

The codebase is designed for easy module swaps:

1. **LLM Provider** - Change `LLM_PROVIDER` env var → factory in `dependencies.py` picks the right LangChain LLM class
2. **Vector Store** - Change `VECTOR_STORE_PROVIDER` → factory in `rag/vectorstore.py` picks Supabase/Chroma/Pinecone
3. **Embedding Model** - Change `OPENAI_EMBEDDING_MODEL` → single place in `rag/embeddings.py`
4. **Database** - All DB access through `db/repositories.py` → swap Supabase client for raw PostgreSQL/SQLAlchemy if needed
5. **Document Loaders** - Registry pattern in `rag/loader.py` → add new file types without touching existing code
6. **Agents** - Each agent is a self-contained module → add/remove agents by editing the graph in `orchestrator.py`
7. **Deployment** - All config in `.env` → deploy to any cloud (Docker, AWS, GCP) by setting env vars

---

## 17. Accounts & URLs Reference

| Service | URL | Account |
|---------|-----|---------|
| GitHub | https://github.com/reallytechy/demoai.git | reallytechy |
| Render (Backend) | https://demoai-1awa.onrender.com | reallytechy@gmail.com |
| Vercel (Frontend) | https://demoai-one.vercel.app | reallytechy@gmail.com |
| Supabase | (Dashboard → project settings) | reallytechy@gmail.com |
| LangSmith | https://smith.langchain.com | reallytechy@gmail.com |

---

## 18. Next Steps

Start with **Phase 1**:
1. Run the Supabase schema migration (Section 6)
2. Expand `settings.py` (Section 5)
3. Build the document upload pipeline
4. Enforce auth on all routes

Then proceed phase by phase. Each phase is independently deployable — the app works at every stage, just with fewer features.
