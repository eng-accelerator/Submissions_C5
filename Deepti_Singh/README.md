# 🔬 Multi-Agent AI Deep Researcher

A production-grade Python backend for multi-hop, multi-source AI research using **LangGraph**, **Agentic RAG**, **MCP-style tools**, and **Claude Sonnet**.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  OrchestratorAgent                                  │
│  • Decomposes query into sub-queries                │
│  • Decides clarification / loop-back                │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┴──────────────┐
          │ needs_clarification?     │
         YES                        NO
          │                         │
          ▼                         │
┌─────────────────┐                 │
│ QueryClarifier  │                 │
│ • Generates     │                 │
│   follow-up Qs  │                 │
│ • Waits for     │                 │
│   user answer   │                 │
└────────┬────────┘                 │
         └──────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  RetrieverAgent  (Agentic RAG)                      │
│  Tools:                                             │
│  ├── Tavily API (web search)                        │
│  ├── DuckDuckGo (fallback, no key needed)           │
│  ├── arXiv API (academic papers)                    │
│  ├── Web Scraper (full page content)                │
│  └── ChromaDB + SentenceTransformer (embedding)    │
│  • Multi-query RAG retrieval                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  AnalyzerAgent                                      │
│  • Per-source summarization + credibility scoring   │
│  • Cross-source contradiction detection             │
│  • Key theme extraction                             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  FactCheckerAgent  (sub-agent)                      │
│  • Extracts key claims per source                   │
│  • Cross-references via DuckDuckGo                  │
│  • Adjusts credibility scores                       │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  InsightAgent                                       │
│  • Chain-of-Thought reasoning                       │
│  • Hypotheses: trend / risk / opportunity / gap     │
│  • Grounded in RAG chunks                           │
└─────────────────────┬───────────────────────────────┘
                      │
            ┌─────────┴──────────────┐
            │ needs_more_research?   │
           YES (loop ≤ max_iter)    NO
            │                        │
            └──► RetrieverAgent      │
                      │              │
                      ▼              ▼
          ┌─────────────────────────────────────────┐
          │  VisualizerAgent                        │
          │  • LLM decides what charts to make       │
          │  • matplotlib / plotly                   │
          │  • Saves PNG to reports/                 │
          └───────────────┬─────────────────────────┘
                          │
                          ▼
          ┌─────────────────────────────────────────┐
          │  ReportBuilderAgent                     │
          │  • Executive Summary (LLM-generated)    │
          │  • Source Analysis + Credibility        │
          │  • Contradictions & Caveats             │
          │  • Insights with reasoning chains        │
          │  • References                            │
          │  • Saves .md to reports/                │
          └─────────────────────────────────────────┘
```

---

## 📁 File Structure

```
deep_researcher/
├── api.py          # FastAPI backend + SSE streaming
├── agents.py       # All 7 agent implementations
├── graph.py        # LangGraph wiring + conditional routing
├── state.py        # Pydantic state schema (shared truth)
├── tools.py        # MCP-style tool definitions
├── rag.py          # Agentic RAG with ChromaDB
├── llm_factory.py  # Anthropic + OpenRouter LLM abstraction
├── run.py          # CLI runner for testing
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment

# On Windows:
venv\Scripts\activate

# On macOS / Linux:
source venv/bin/activate

### 1. Install dependencies

```bash
cd deep_researcher
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env with your keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   TAVILY_API_KEY=tvly-...     (optional but recommended)
#   LANGCHAIN_API_KEY=...       (optional, for LangSmith tracing)
```

### 3. Run CLI (quick test)

```bash
python run.py "What are the latest breakthroughs in Alzheimer's treatment?"
python run.py "How is quantum computing affecting cryptography in 2025?" --iterations 2
```

### 4. Run API server

```bash
python api.py
# or
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 5. API Usage

```bash
# Start research
curl -X POST http://localhost:8000/research/start \
  -H "Content-Type: application/json" \
  -d '{"query": "Impact of LLMs on drug discovery", "max_iterations": 2}'

# Response: {"session_id": "abc-123", "status": "running", ...}

# Stream events (Server-Sent Events)
curl http://localhost:8000/research/abc-123/stream

# Get status
curl http://localhost:8000/research/abc-123/status

# Submit clarification (if prompted)
curl -X POST http://localhost:8000/research/abc-123/clarify \
  -H "Content-Type: application/json" \
  -d '{"answer": "Focus on small molecule drugs, last 2 years"}'

# Get final report
curl http://localhost:8000/research/abc-123/report
curl "http://localhost:8000/research/abc-123/report?format=md"
curl "http://localhost:8000/research/abc-123/report?format=file" --output report.md
```

---

## 🔑 Key Techniques Used

| Technique | Where Used |
|---|---|
| **LangGraph StateGraph** | `graph.py` — conditional routing, loop-back, checkpointing |
| **Agentic RAG** | `rag.py` + `agents.py` — multi-query retrieval, chromadb |
| **MCP-style Tools** | `tools.py` — LangChain `@tool` decorated functions |
| **Chain-of-Thought** | `InsightAgent` — step-by-step reasoning chains |
| **Multi-source retrieval** | `RetrieverAgent` — Tavily + DDG + arXiv fan-out |
| **Pydantic structured output** | `state.py`, all agents parse LLM JSON responses |
| **MemorySaver checkpointing** | `graph.py` — resumable sessions |
| **SSE streaming** | `api.py` — real-time agent progress to frontend |
| **Credibility scoring** | `AnalyzerAgent` + `FactCheckerAgent` |

---

## 🧪 Recommended Demo Queries

1. `"What are the latest breakthroughs in Alzheimer's treatment in 2024-2025?"`
2. `"How is quantum computing threatening current cryptography standards?"`
3. `"What is the current state of nuclear fusion energy commercialization?"`
4. `"How are LLMs being used in drug discovery pipelines?"`
