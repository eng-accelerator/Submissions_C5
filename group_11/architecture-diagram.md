# DemoAI - AI Financial Coach: Architecture & Showcase Flow

```mermaid
graph TB
    subgraph USER["User"]
        U((User))
    end

    subgraph FRONTEND["Frontend — React + Vite + Tailwind (Vercel)"]
        LP[Landing Page]
        CHAT[AI Coach Chat]
        DASH[Financial Dashboard]
        UPLOAD[Document Upload]
        CR[Credit Report Viewer]
        SHOW[Showcase Page]
    end

    subgraph AUTH["Authentication"]
        SUPA[(Supabase<br/>Google OAuth)]
    end

    subgraph BACKEND["Backend — FastAPI (Render)"]
        API["/api Routes"]

        subgraph SHOWCASE["Showcase Feature: Multi-Agent Orchestration (LangGraph)"]
            direction TB

            subgraph ORCHESTRATOR["Orchestrator Agent — Intelligent Router"]
                CTX["1. Load Context Node<br/>RAG retrieval"]
                ROUTE["2. Route Node<br/>Analyze intent & select specialist"]
                SPEC["3. Specialist Node<br/>Execute with tools (up to 5 rounds)"]
                CTX --> ROUTE --> SPEC
            end

            subgraph AGENTS["Specialist Agents"]
                DA["Debt Analyzer<br/>Credit utilization,<br/>delinquencies,<br/>risk assessment"]
                SS["Savings Strategist<br/>Emergency funds,<br/>goal-based plans,<br/>projections"]
                BA["Budget Advisor<br/>50/30/20 analysis,<br/>category insights,<br/>recommendations"]
                PO["Payoff Optimizer<br/>Avalanche vs Snowball,<br/>month-by-month projections,<br/>interest savings"]
            end

            subgraph TOOLS["LangChain Financial Tools"]
                T1["calculate_debt_to_income()"]
                T2["simulate_payoff()"]
                T3["project_savings()"]
                T4["analyze_budget()"]
            end

            ROUTE -->|"ROUTE: debt_analyzer"| DA
            ROUTE -->|"ROUTE: savings_strategist"| SS
            ROUTE -->|"ROUTE: budget_advisor"| BA
            ROUTE -->|"ROUTE: payoff_optimizer"| PO
            ROUTE -->|"ROUTE: self"| ROUTE

            DA & SS & BA & PO --> TOOLS
        end

        subgraph RAG["RAG Pipeline"]
            LOADER["Document Loader<br/>PDF / CSV / JSON /<br/>XLSX / Images"]
            CHUNK["Text Chunking<br/>+ Metadata"]
            VS["In-Memory<br/>Vector Store"]
            LOADER --> CHUNK --> VS
        end

        subgraph SERVICES["Services"]
            BLOG["Blog Generator<br/>Text + Image + TTS"]
            PLAN["Financial Plan<br/>Multi-agent collaboration"]
        end

        SESS["Session Memory<br/>(last 50 messages)"]
        CACHE["Dashboard Cache"]
        SAMPLE["Sample Credit<br/>Report Data"]
    end

    subgraph LLM["LLM Providers"]
        OR["OpenRouter<br/>Gemini 2.0 Flash"]
        OAI["OpenAI<br/>GPT-4o"]
        EMB["OpenAI Embeddings<br/>text-embedding-3-small"]
    end

    subgraph OBS["Observability"]
        LS["LangSmith<br/>Tracing"]
    end

    %% User interactions
    U --> LP & CHAT & DASH & UPLOAD & CR & SHOW
    U -.->|Google OAuth| SUPA
    SUPA -.->|JWT| FRONTEND

    %% Frontend to Backend
    CHAT -->|"POST /api/chat"| API
    DASH -->|"GET /api/dashboard/*"| API
    UPLOAD -->|"POST /api/documents/upload"| API
    CR -->|"GET /api/reports/*"| API

    %% API routing
    API -->|chat request| CTX
    API -->|upload file| LOADER
    API -->|dashboard queries| CACHE
    CACHE -.->|cache miss| CTX
    API --> SAMPLE
    API --> BLOG & PLAN

    %% RAG integration
    VS -->|similarity search| CTX
    UPLOAD -->|embeddings| EMB

    %% Agent to LLM
    ORCHESTRATOR -->|inference| OR
    ORCHESTRATOR -->|fallback| OAI
    AGENTS -->|inference| OR
    AGENTS -->|fallback| OAI
    CHUNK -->|embed| EMB

    %% Observability
    ORCHESTRATOR -.->|traces| LS

    %% Response flow
    SPEC -->|"ChatResponse<br/>{message, agent_name, badge}"|API
    API -->|"SSE stream / JSON"| CHAT
    API -->|"overview, insights,<br/>payoff, budget"| DASH

    %% Styling
    classDef showcase fill:#fbbf24,stroke:#d97706,stroke-width:3px,color:#000
    classDef agent fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    classDef tool fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef frontend fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    classDef rag fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff
    classDef llm fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff

    class ORCHESTRATOR,CTX,ROUTE,SPEC showcase
    class DA,SS,BA,PO agent
    class T1,T2,T3,T4 tool
    class LP,CHAT,DASH,UPLOAD,CR,SHOW frontend
    class LOADER,CHUNK,VS rag
    class OR,OAI,EMB llm
```

## Flow Summary

### Showcase Feature: Multi-Agent Orchestration

The core showcase is the **LangGraph State Machine** that powers intelligent financial coaching:

1. **User sends a message** via the Chat interface
2. **Load Context Node** — RAG retrieves relevant document chunks from the user's uploaded financial data
3. **Route Node** — The Orchestrator LLM analyzes user intent and decides:
   - `self` — answer directly (simple/general queries)
   - `debt_analyzer` — debt, credit score, utilization questions
   - `savings_strategist` — savings goals, emergency funds
   - `budget_advisor` — spending analysis, budget planning
   - `payoff_optimizer` — debt payoff strategies, interest optimization
4. **Specialist Node** — The selected agent executes with access to **4 financial tools**, looping up to 5 rounds of tool calls for complex calculations
5. **Response** streams back via SSE with the agent's badge color indicating which specialist answered

### Supporting Flows

| Flow | Path |
|------|------|
| **Document Upload** | User → Upload Page → `/api/documents/upload` → Loader → Chunker → Vector Store (embeddings via OpenAI) |
| **Dashboard** | Dashboard Page → 4 parallel API calls → Cache check → RAG + LLM extraction → Financial tools → Rendered cards |
| **Credit Report** | Report Page → `/api/reports` → Sample JSON data → Rendered tables |
| **Blog Generation** | Admin Page → LLM text generation → Vision model image → gTTS audio |
