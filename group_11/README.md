# DemoAI — AI Financial Coach Agent

A multi-agent AI financial advisor that analyzes credit reports, debt, spending, and savings — powered by LangChain, LangGraph, and OpenAI.

## Tech Stack

- **Backend:** FastAPI + LangChain + LangGraph (Python)
- **Frontend:** React 18 + Vite + Tailwind CSS (TypeScript)
- **AI:** OpenAI GPT-4o (configurable), LangGraph multi-agent orchestration
- **Auth:** Supabase (Google OAuth)
- **RAG:** Document ingestion (PDF/CSV/JSON/XLSX) + in-memory vector store
- **Observability:** LangSmith tracing (optional)

## Agents

| Agent | Role |
|-------|------|
| **Orchestrator** | Routes user queries to the right specialist |
| **Debt Analyzer** | Analyzes debt portfolio, risk flags, credit utilization |
| **Savings Strategist** | Personalized savings plans, emergency fund advice |
| **Budget Advisor** | Budget recommendations, 50/30/20 benchmark analysis |
| **Payoff Optimizer** | Avalanche vs snowball payoff strategies with projections |

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key with billing enabled (https://platform.openai.com/settings/organization/billing)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Edit `backend/.env` and set your real API key:

```
OPENAI_API_KEY=sk-your-real-key
```

Start the server:

```bash
source venv/bin/activate
uvicorn app.main:app --port 8001
```

Verify: http://localhost:8001/health

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

---

## Testing Guide

### Frontend URLs

| URL | Page |
|-----|------|
| http://localhost:5173/ | Landing page |
| http://localhost:5173/dashboard | Financial dashboard |
| http://localhost:5173/chat | AI Coach chat |
| http://localhost:5173/upload | Document upload |
| http://localhost:5173/report/get | Credit report viewer |

### Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check + agent list |
| GET | /api/report/get | Sample credit report |
| POST | /api/chat | Send message to AI coach |
| POST | /api/chat/stream | SSE streaming chat |
| GET | /api/chat/sessions/{id}/history | Chat history |
| DELETE | /api/chat/sessions/{id} | Clear session |
| POST | /api/documents/upload | Upload document (multipart) |
| GET | /api/documents | List uploaded documents |
| DELETE | /api/documents/{id} | Delete a document |
| GET | /api/dashboard/overview | Financial overview |
| GET | /api/dashboard/debt-breakdown | Debt details + DTI |
| GET | /api/dashboard/payoff-plan | Payoff strategy comparison |
| GET | /api/dashboard/budget-analysis | Budget vs 50/30/20 |
| GET | /api/dashboard/insights | AI-generated insights |

---

## How to Test Each Feature

### Feature 1: Landing Page

**URL:** http://localhost:5173/

**What to verify:**
1. Hero section renders with headline and CTA
2. Three feature cards show (Score Analysis, AI Insights, Secure & Private)
3. "How it works" section with 3 steps
4. Navigation bar has links: Dashboard, AI Coach, Upload, Report
5. Sign in button is visible (Google OAuth — requires Supabase config)

**Expected result:** Marketing page loads with no errors in browser console.

---

### Feature 2: Financial Dashboard

**URL:** http://localhost:5173/dashboard

**What to verify:**
1. **Credit Score Gauge** — Shows 548 (Poor) with color-coded circular gauge
2. **Stat Cards** — Total Debt (₹3,52,000), Monthly Income (₹50,000), Overdue (₹77,000)
3. **AI Insights** — 6 cards:
   - [WARNING] Low Credit Score
   - [WARNING] High Credit Utilization
   - [CRITICAL] Written-Off Account
   - [POSITIVE] Active credit history
   - [POSITIVE] Some recent on-time payments
   - [TIP] Savings Opportunity
4. **Payoff Strategies** — Two cards comparing Avalanche vs Snowball:
   - Both show ~2 years 4 months to debt-free
   - Interest: ₹59,483
   - Avalanche marked as "Recommended"
   - Payoff order: HDFC Credit Card first (month 12), then Axis Personal Loan (month 28)
5. **Budget Analysis** — 50/30/20 bars:
   - Needs: ₹35,900 / ₹25,000 (over budget — red bar)
   - Wants: ₹7,500 / ₹15,000 (under budget)
   - Savings: ₹6,600 / ₹10,000 (under target)
   - Expense breakdown grid (EMI, Rent, Groceries, etc.)
6. **Risk Flags** — 4 items (high utilization, enquiries, written-off, late payments)
7. **Positive Factors** — 2 items

**Backend test (curl):**
```bash
curl http://localhost:8001/api/dashboard/overview
curl http://localhost:8001/api/dashboard/insights
curl http://localhost:8001/api/dashboard/payoff-plan
curl http://localhost:8001/api/dashboard/budget-analysis
curl http://localhost:8001/api/dashboard/debt-breakdown
```

**Expected result:** All data loads, charts render, no console errors. Dashboard works without OpenAI key.

---

### Feature 3: AI Coach Chat

**URL:** http://localhost:5173/chat

**Prerequisite:** OpenAI API key with billing enabled in `backend/.env`.

**What to verify:**
1. **Empty state** — Shows "AI Financial Coach" heading with 5 suggested question buttons
2. **Click a suggested question** — Sends it as a message immediately
3. **Agent routing** — Different questions route to different agents:
   - "Analyze my debt" → Debt Analyzer (red badge)
   - "Create a savings plan" → Savings Strategist (green badge)
   - "What budget changes should I make?" → Budget Advisor (purple badge)
   - "Compare avalanche vs snowball" → Payoff Optimizer (orange badge)
   - "Hello" → Orchestrator / Financial Coach (blue badge)
4. **Agent badge** — Each response shows a colored badge with the agent name
5. **Loading state** — Three bouncing dots appear while waiting for response
6. **Conversation memory** — Follow-up messages maintain context within a session
7. **Keyboard shortcut** — Enter sends message, Shift+Enter creates new line

**Test messages to try:**
```
1. "Hello, what can you help me with?"
2. "Analyze my debt and tell me what needs urgent attention"
3. "Create a savings plan for me based on my income"
4. "What budget changes should I make to save more?"
5. "Compare avalanche vs snowball payoff strategies for my debts"
6. "What is hurting my credit score the most?"
7. "If I pay ₹10,000 extra per month, when will I be debt free?"
```

**Backend test (curl):**
```bash
# Send a message
curl -X POST http://localhost:8001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Analyze my debt", "session_id": "test-1"}'

# Check conversation history
curl http://localhost:8001/api/chat/sessions/test-1/history

# Clear session
curl -X DELETE http://localhost:8001/api/chat/sessions/test-1
```

**Expected result:** Each question gets a relevant, data-backed response from the correct specialist agent. Responses reference actual debt amounts (₹92,000 HDFC, ₹2,10,000 Axis, ₹50,000 Bajaj).

**If OpenAI key has no credits:** Chat will show an error message. Dashboard and other features still work.

---

### Feature 4: Document Upload (RAG)

**URL:** http://localhost:5173/upload

**Prerequisite:** OpenAI API key with billing (needed for embeddings).

**What to verify:**
1. **Drop zone** — Dashed border area with upload icon
2. **Drag and drop** — Drop zone highlights blue when dragging a file over it
3. **File picker** — "Choose Files" button opens system file dialog
4. **Accepted formats** — PDF, CSV, JSON, XLSX (max 10MB)
5. **Processing status** — After upload:
   - Green success message: "Processed {filename} into {N} searchable chunks"
   - Document appears in list below with status badge
6. **Document list** — Shows filename, file type icon, chunk count, status
7. **Delete** — Trash icon removes a document from the list
8. **Rejection** — Uploading a .txt or .png shows a 400 error

**Test files to upload:**
- `backend/app/data/sample_credit_score.json` (the included sample)
- Any CSV with financial data (bank statement export, etc.)
- Any PDF credit report or bank statement

**Backend test (curl):**
```bash
# Upload a file
curl -X POST http://localhost:8001/api/documents/upload \
  -F "file=@backend/app/data/sample_credit_score.json"

# List documents
curl http://localhost:8001/api/documents

# Delete a document
curl -X DELETE http://localhost:8001/api/documents/{doc-id}
```

**Expected result:** Files are parsed, chunked, and embedded. After uploading, the AI Coach chat can reference information from uploaded documents.

---

### Feature 5: Credit Report Viewer

**URL:** http://localhost:5173/report/get

**What to verify:**
1. **Score Summary** — Gauge showing 548 (Poor) + stat tiles (3 accounts, 2 active, 1 closed)
2. **Personal Info** — Name (Rahul Sharma), DOB, PAN, emails, addresses, phone numbers
3. **Accounts Table** — 3 account cards:
   - HDFC Credit Card: ₹92,000 balance, 92% utilization, ₹12,000 overdue
   - Axis Personal Loan: ₹2,10,000 balance, ₹15,000 overdue
   - Bajaj Consumer Loan: Written-off, ₹50,000
4. **Payment history badges** — DPD indicators (000, 30, 60, 90, 120, 150)
5. **Delinquencies** — Written-off (High impact), Late Payment 90 DPD (Medium)
6. **Enquiries** — 3 enquiries (HDFC, ICICI, Axis)
7. **Disputes** — 1 dispute (ACC002 Overdue Amount, Under Review)
8. **Credit Utilization** — 92,000 / 1,00,000 = 92% (High)
9. **Payment Summary** — 6 on-time, 4 late, 2 severe
10. **Risk Flags** — 4 warnings + 2 positive factors

**Backend test (curl):**
```bash
curl http://localhost:8001/api/report/get
```

**Expected result:** Full credit report renders with all sections. Works without OpenAI key.

---

### Feature 6: Navigation & Responsive Design

**What to verify:**
1. **Desktop (>640px):** Navbar shows all 4 links (Dashboard, AI Coach, Upload, Report) + Sign in button
2. **Mobile (<640px):** Navbar shows first 3 links condensed + hamburger or sign in
3. **Active link highlighting** — Current page link has blue background in navbar
4. **Page transitions** — Clicking links navigates without full page reload (SPA)
5. **Loading states** — Dashboard shows "Loading dashboard..." skeleton while fetching

---

## Automated Backend Test (All Endpoints)

Run this script to verify all backend endpoints at once:

```bash
echo "=== Health ===" && curl -s http://localhost:8001/health | python3 -m json.tool

echo "=== Report ===" && curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8001/api/report/get

echo "=== Dashboard Overview ===" && curl -s http://localhost:8001/api/dashboard/overview | python3 -m json.tool

echo "=== Debt Breakdown ===" && curl -s http://localhost:8001/api/dashboard/debt-breakdown | python3 -m json.tool

echo "=== Payoff Plan ===" && curl -s http://localhost:8001/api/dashboard/payoff-plan | python3 -m json.tool

echo "=== Budget ===" && curl -s http://localhost:8001/api/dashboard/budget-analysis | python3 -m json.tool

echo "=== Insights ===" && curl -s http://localhost:8001/api/dashboard/insights | python3 -m json.tool

echo "=== Chat ===" && curl -s -X POST http://localhost:8001/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello","session_id":"test"}' | python3 -m json.tool

echo "=== Upload ===" && curl -s -X POST http://localhost:8001/api/documents/upload \
  -F "file=@backend/app/data/sample_credit_score.json" | python3 -m json.tool

echo "=== Doc List ===" && curl -s http://localhost:8001/api/documents | python3 -m json.tool
```

---

## Expected Test Results Summary

| Feature | Without OpenAI Key | With OpenAI Key |
|---------|-------------------|-----------------|
| Landing Page | PASS | PASS |
| Dashboard (all 4 panels) | PASS | PASS |
| AI Insights | PASS | PASS |
| Payoff Strategies | PASS | PASS |
| Budget Analysis | PASS | PASS |
| Credit Report | PASS | PASS |
| AI Coach Chat | ERROR (quota) | PASS |
| Document Upload | ERROR (embedding) | PASS |
| SSE Streaming | ERROR (quota) | PASS |
| Navigation | PASS | PASS |

---

## Configuration

All config lives in `backend/.env`. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required for chat + RAG |
| `OPENAI_MODEL` | gpt-4o | LLM model (try gpt-4o-mini for lower cost) |
| `CORS_ALLOWED_ORIGINS` | http://localhost:5173 | Frontend origin |
| `LANGCHAIN_TRACING_V2` | false | Enable LangSmith tracing |
| `AGENT_TEMPERATURE` | 0.1 | LLM creativity (0=deterministic, 1=creative) |
| `MAX_UPLOAD_SIZE_MB` | 10 | Max document upload size |
| `ALLOWED_FILE_TYPES` | pdf,csv,json,xlsx | Accepted upload formats |

To switch to a cheaper model, change in `.env`:
```
OPENAI_MODEL=gpt-4o-mini
```

---

## Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Backend | Render | https://demoai-1awa.onrender.com |
| Frontend | Vercel | https://demoai-one.vercel.app |
| Auth | Supabase | (Dashboard) |
| Observability | LangSmith | https://smith.langchain.com |

---

## Project Structure

```
demoai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS
│   │   ├── settings.py          # All config from .env
│   │   ├── agents/              # LangGraph multi-agent system
│   │   │   ├── orchestrator.py  # StateGraph (route → specialist → respond)
│   │   │   ├── prompts.py       # System prompts per agent
│   │   │   ├── tools.py         # Financial calculation tools
│   │   │   ├── state.py         # Shared agent state schema
│   │   │   └── _sample_data.py  # Demo financial data
│   │   ├── rag/                 # Document processing pipeline
│   │   │   ├── loader.py        # PDF/CSV/JSON/XLSX loaders
│   │   │   ├── embeddings.py    # OpenAI embedding config
│   │   │   └── vectorstore.py   # In-memory vector store
│   │   ├── routes/              # API endpoints
│   │   │   ├── chat.py          # Chat + SSE streaming
│   │   │   ├── dashboard.py     # Dashboard aggregation
│   │   │   ├── documents.py     # Document upload + RAG
│   │   │   └── reports.py       # Credit report
│   │   └── models/              # Pydantic schemas
│   ├── .env                     # Local config (git-ignored)
│   └── requirements.txt         # Python deps
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx      # Marketing page
│   │   │   ├── Dashboard.tsx    # Financial dashboard
│   │   │   ├── Chat.tsx         # AI Coach chat
│   │   │   ├── Upload.tsx       # Document upload
│   │   │   └── SampleReport.tsx # Credit report viewer
│   │   ├── components/          # Reusable UI components
│   │   ├── services/api.ts      # Backend API client
│   │   └── hooks/               # React hooks
│   └── package.json
├── PLAN.md                      # Architecture & implementation plan
└── README.md                    # This file
```
