# AI Financial Coach Agent

Secure, investor-ready MVP for personalized financial coaching using LangGraph multi-agent orchestration, tabular RAG over canonical Pandas data, Ozero-style fine-grained authorization, Hugging Face reasoning, Llama Guard moderation, and a Streamlit dashboard.

## What is included

- Multi-agent workflow built with LangGraph
- File ingestion pipeline using PyPDF2, Pandas, and LangChain loaders, with heuristic PDF-to-table extraction
- Schema-aware tabular RAG with minimal authorized row injection
- Optional hybrid RAG over messy document text using Hugging Face sentence-transformer embeddings with lexical fallback
- Deterministic debt, savings, and budget calculations in Python
- Streamlit dashboard with metrics, charts, tables, action plan, and audit trail
- Architecture, prompts, FGA model, and n8n workflow documentation

## Repository structure

- [app.py](/C:/Users/iNNOVATEQ/Documents/New%20project/app.py)
- [run_webhooks.py](/C:/Users/iNNOVATEQ/Documents/New%20project/run_webhooks.py)
- [src/financial_coach](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach)
- [docs/architecture.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/architecture.md)
- [docs/n8n.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/n8n.md)
- [docs/prompts.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/prompts.md)
- [data/sample](/C:/Users/iNNOVATEQ/Documents/New%20project/data/sample)
- [workflows](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows)

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### Run webhook endpoints

```powershell
.venv\Scripts\Activate.ps1
python run_webhooks.py
```

### Run with Docker Compose

```powershell
docker compose up --build
```

## LangSmith tracing

- The app supports optional LangSmith tracing for LangGraph runs.
- Configure it in [`.env`](/C:/Users/iNNOVATEQ/Documents/New%20project/.env) with:
  - `LANGSMITH_API_KEY`
  - `LANGSMITH_TRACING=true`
  - `LANGSMITH_PROJECT=ai-financial-coach-agent`
- After updating dependencies, reinstall:

```powershell
pip install -r requirements.txt
```

## Demo flow

1. Launch Streamlit.
2. Keep the default `demo-user-001` user or enter another scoped user id.
3. Run the workflow with built-in sample data or upload `income.csv`, `expenses.csv`, `debts.csv`, and `assets.csv`.
4. You can also upload `pdf` documents such as statements, summaries, or messy reports. Their text remains available for hybrid retrieval, and recognizable financial lines are mapped into structured tables when possible.
4. Review the action plan, budget opportunities, authorized tables, and audit trail.

## Hybrid RAG demo

1. Install updated dependencies:

```powershell
pip install -r requirements.txt
```

2. Launch the app:

```powershell
streamlit run app.py
```

3. Upload a sample set, a supporting PDF, or use the built-in demo data.
4. In `Analysis request`, ask something that benefits from both structured facts and document evidence, for example:
   - `Explain the document evidence behind my debt payoff recommendation`
   - `What lines from my uploaded files support my savings plan?`
   - `Show the text evidence related to my emergency fund and debt obligations`
5. Click `Run secure analysis`.
6. Show two areas in the UI:
   - `Retrieval Summary` for authorized table retrieval
   - `Hybrid RAG Document Hits` for chunk-level document-text evidence

### What to say in the demo

- Primary retrieval is still secure tabular RAG over canonical user-scoped tables.
- Hybrid retrieval adds document chunk search over messy uploaded text.
- PDF uploads now attempt a conservative schema-aware extraction pass before falling back to text-only use.
- If the embedding model is available, document hits use Hugging Face embeddings.
- If not, the app falls back safely to lexical chunk matching without breaking the workflow.

## Extra dummy datasets

- [set_1_balanced](/C:/Users/iNNOVATEQ/Documents/New%20project/data/sample/set_1_balanced) with user id `balanced-user-001`
- [set_2_debt_stressed](/C:/Users/iNNOVATEQ/Documents/New%20project/data/sample/set_2_debt_stressed) with user id `debt-stressed-002`
- [set_3_high_saver](/C:/Users/iNNOVATEQ/Documents/New%20project/data/sample/set_3_high_saver) with user id `high-saver-003`

To use one of these sets:

1. Enter the matching `User ID` in the sidebar.
2. Upload the four files from that sample set.
3. Click `Run secure analysis`.

## Security model

- Every canonical row carries `user_id` and `scope`.
- Table and row checks are executed before retrieval, calculations, and explanation.
- Unauthorized rows are removed before LangGraph agents receive context.
- The narrative explanation is moderated before display/export.

## Implementation notes

- The MVP uses a lightweight Ozero FGA adapter and Hugging Face reasoning facade so the architecture is production-aligned while remaining runnable locally.
- `yfinance` enriches the plan with market context and falls back safely when live data is unavailable.
- The explanation layer is intentionally separated from the calculator layer to keep math deterministic and auditable.
- `n8n` workflows can call the webhook server for ingestion, analysis, audit reads, and notification callbacks.

## Delivery checklist mapping

- Architecture: [docs/architecture.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/architecture.md)
- Prompts: [docs/prompts.md](/C:/Users/iNNOVATEQ/Documents/New%20project/docs/prompts.md)
- Dashboard implementation: [app.py](/C:/Users/iNNOVATEQ/Documents/New%20project/app.py)
- Agent graph: [graph.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/graph.py)
- Authorization model: [auth.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/auth.py)
