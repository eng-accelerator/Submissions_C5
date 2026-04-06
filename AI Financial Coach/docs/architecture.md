# AI Financial Coach Agent Architecture

## 1. High-Level System Architecture

```text
[User / Streamlit Dashboard]
        |
        v
[File Upload + Query Intake]
        |
        v
[n8n Ingestion Workflow]
  - file validation
  - audit event creation
  - route PDF/CSV/XLSX processors
        |
        v
[Financial Data Ingestion Agent]
  - PyPDF2 text extraction
  - LangChain document loaders
  - Pandas normalization
  - canonical table persistence
        |
        v
[Ozero FGA Policy Checkpoint]
  - table-level authorization
  - row-level authorization
        |
        v
[Tabular RAG & Data Injection Agent]
  - schema-aware Pandas retrieval
  - minimal authorized row injection
        |
        v
[LangGraph Orchestrator]
  - Savings Strategy Agent
  - Debt Analyzer Agent
  - Budget Optimization Agent
  - optional future agents
        |
        v
[Deterministic Python Calculators]
        |
        v
[Hugging Face Explanation Layer]
        |
        v
[Llama Guard Moderation]
        |
        v
[Streamlit Dashboard + Audit Trail + Export]
```

## 2. LangGraph Agent Workflow and State Machine

### Nodes
- `retrieve_data`
- `collect_market_context`
- `savings_analysis`
- `debt_analysis`
- `budget_analysis`
- `orchestrate`

### State
- `user_id`
- `query`
- `authorized_tables`
- `retrieval_summary`
- `debt_plan`
- `savings_plan`
- `budget_plan`
- `market_context`
- `action_plan`
- `explanation`
- `moderation`
- `audit_log`

### Pseudocode

```python
graph = StateGraph(CoachState)

graph.add_node("retrieve_data", tabular_rag.retrieve_authorized_rows)
graph.add_node("collect_market_context", fetch_market_context)
graph.add_node("savings_analysis", savings_strategy_agent.run)
graph.add_node("debt_analysis", debt_analyzer_agent.run)
graph.add_node("budget_analysis", budget_optimization_agent.run)
graph.add_node("orchestrate", financial_coach_orchestrator.run)

graph.set_entry_point("retrieve_data")
graph.add_edge("retrieve_data", "collect_market_context")
graph.add_edge("collect_market_context", "savings_analysis")
graph.add_edge("savings_analysis", "debt_analysis")
graph.add_edge("debt_analysis", "budget_analysis")
graph.add_edge("budget_analysis", "orchestrate")
graph.add_edge("orchestrate", END)
```

### State Transition Rules
- No downstream node receives raw uploaded files.
- `retrieve_data` strips unauthorized rows before writing `authorized_tables`.
- `debt_analysis` and `budget_analysis` consume only `authorized_tables`.
- `orchestrate` can explain only previously computed deterministic results.
- `moderation` occurs before dashboard rendering and export.

## 3. Ozero FGA Authorization Model

### Authorization Objects
- `user:{user_id}`
- `table:income`
- `table:expenses`
- `table:debts`
- `table:assets`
- `row:income:{user_id}`
- `row:expenses:{user_id}`
- `row:debts:{user_id}`
- `row:assets:{user_id}`

### Relations
- `read`
- `calculate`
- `explain`

### Example Policy Mapping

```json
{
  "demo-user-001": {
    "table:income": ["read", "calculate", "explain"],
    "table:expenses": ["read", "calculate", "explain"],
    "table:debts": ["read", "calculate", "explain"],
    "table:assets": ["read", "calculate", "explain"],
    "row:income:demo-user-001": ["read", "calculate", "explain"],
    "row:expenses:demo-user-001": ["read", "calculate", "explain"],
    "row:debts:demo-user-001": ["read", "calculate", "explain"],
    "row:assets:demo-user-001": ["read", "calculate", "explain"]
  }
}
```

### Enforcement Points
1. Before tabular retrieval, `authorize_table` and `authorize_rows` filter the DataFrame.
2. Before calculations, only authorized frames are handed to the debt, savings, and budget agents.
3. Before explanations, only deterministic outputs plus authorized summaries are sent to the reasoning layer.

## 4. Tabular RAG Design and Data Injection Strategy

### Design
- Uploaded PDFs and spreadsheets are converted into normalized Pandas DataFrames.
- Retrieval is schema-aware and rule-based rather than free-form embedding search.
- Each query is mapped to table-specific retrieval behavior.
- Only top relevant rows are serialized into downstream context.

### Hybrid RAG extension
- The same uploaded source text is chunked into document segments.
- A Hugging Face sentence-transformer model can embed each chunk for semantic retrieval.
- Top document hits are returned alongside the authorized tabular rows.
- If embeddings are unavailable at runtime, lexical scoring is used as a safe fallback.
- Tabular facts remain the source of truth for calculations; document hits provide supporting context only.

### Data Injection Rules
- `expenses`: top spending categories for budget questions.
- `debts`: highest APR ordering for debt payoff requests.
- `income`: dominant net income streams for cash flow calculations.
- `assets`: liquid assets first for emergency fund planning.

### Why This Is Secure
- Authorized rows are filtered before retrieval logic runs.
- Only minimal authorized records are injected.
- No raw document text is passed into downstream agents after normalization.

## 5. Canonical Data Schemas

### `income`
- `user_id`
- `scope`
- `source_id`
- `income_type`
- `employer`
- `gross_monthly`
- `net_monthly`
- `frequency`
- `confidence`
- `effective_date`

### `expenses`
- `user_id`
- `scope`
- `source_id`
- `category`
- `merchant`
- `amount`
- `frequency`
- `essentiality`
- `confidence`
- `transaction_date`

### `debts`
- `user_id`
- `scope`
- `source_id`
- `debt_name`
- `debt_type`
- `balance`
- `apr`
- `minimum_payment`
- `due_day`
- `secured`
- `confidence`

### `assets`
- `user_id`
- `scope`
- `source_id`
- `asset_name`
- `asset_type`
- `institution`
- `balance`
- `liquidity_tier`
- `risk_level`
- `valuation_date`
- `confidence`

## 6. Sample Prompt Templates for Each Agent

See [prompts.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/prompts.md).

## 7. n8n Workflow Descriptions

### Workflow 1: File Upload Ingestion
- Trigger: user file upload from Streamlit or object storage webhook.
- Validate MIME type, file size, and virus-scan status.
- Create audit event with upload metadata.
- Route files to Python ingestion service.
- Persist normalized tables and emit notification.

### Workflow 2: Monthly Re-Analysis
- Trigger: scheduled monthly cron.
- Pull newly ingested data for each active user.
- Run LangGraph orchestration in batch mode.
- Save summaries and push alerts for major cash flow deterioration.

### Workflow 3: Guardrail Alerting
- Trigger: moderation failure or high-risk advice pattern.
- Write audit log entry.
- Notify compliance channel via Slack and email.
- Suppress dashboard export until reviewed.

## 8. Hugging Face Model Selection Rationale

- Reasoning and explanation model: `mistralai/Mistral-7B-Instruct-v0.3`
  - Strong instruction following for narrative synthesis.
  - Cost-effective for explanation generation.
  - Good fit for private inference endpoints.
- Embedding model for optional hybrid retrieval: `sentence-transformers/all-MiniLM-L6-v2`
  - Lightweight and inexpensive.
  - Suitable for document chunk tagging and similarity fallback.
- Safety model: `meta-llama/Llama-Guard-3-8B`
  - Explicit safety policy support.
  - Works well as a separate moderation gate before presenting advice.

## 9. Streamlit Dashboard Design

### Charts
- Expense distribution by category bar chart.
- Debt strategy comparison chart for payoff horizon.

### Tables
- Authorized canonical tables.
- Budget opportunity table with reduction estimates.
- Audit log with agent-step summaries.

### Insights
- Cash flow metrics.
- Emergency fund gap.
- Debt strategy recommendation.
- Market benchmark context from `yfinance`.

### Action Items
- Ordered checklist suitable for user execution.
- Exportable markdown summary for advisor review.

## 10. End-to-End User Journey

1. User uploads PDFs, CSVs, or spreadsheets in Streamlit.
2. n8n validates and routes files into the ingestion pipeline.
3. Ingestion agent extracts text and normalizes canonical tables.
4. Ozero FGA filters the user’s accessible tables and rows.
5. Tabular RAG selects only relevant authorized rows.
6. LangGraph runs savings, debt, and budget agents.
7. Python calculators produce deterministic outputs.
8. Hugging Face model generates the narrative explanation.
9. Llama Guard moderates the response.
10. Streamlit renders dashboard insights and audit trail.

## 11. Guardrail Enforcement Layers

- Input validation on file type, size, and parser failures.
- Ozero FGA table and row filtering before retrieval.
- Deterministic calculators isolated from LLM reasoning.
- Llama Guard moderation on final output.
- Audit logging on every graph node.
- Safe fallback values when market APIs fail.

## 12. Future Extensibility Ideas

- Goal Planning Agent for home purchase, retirement, and education targets.
- Financial Risk Awareness Agent for concentration and liquidity risk.
- Live bank connector ingestion via secure aggregators routed through n8n.
- Investor-ready cohort analytics for aggregate anonymized insights.
- Human advisor review queue for complex or blocked recommendations.
