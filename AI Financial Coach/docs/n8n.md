# n8n Integration Guide

## What Was Added

- Python webhook server entrypoint: [run_webhooks.py](/C:/Users/iNNOVATEQ/Documents/New%20project/run_webhooks.py)
- Webhook implementation: [webhooks.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/webhooks.py)
- Audit logging: [audit.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/audit.py)
- Notification hooks: [notifications.py](/C:/Users/iNNOVATEQ/Documents/New%20project/src/financial_coach/notifications.py)
- Sample n8n workflows:
  - [n8n_financial_coach_ingestion.json](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows/n8n_financial_coach_ingestion.json)
  - [n8n_financial_coach_notification.json](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows/n8n_financial_coach_notification.json)
- Local containers:
  - [docker-compose.yml](/C:/Users/iNNOVATEQ/Documents/New%20project/docker-compose.yml)
  - [Dockerfile](/C:/Users/iNNOVATEQ/Documents/New%20project/Dockerfile)

## Webhook Endpoints

### `GET /health`
- Returns a service health payload.

### `GET /webhooks/n8n/audit?limit=25`
- Returns recent audit events from `data/audit/audit_log.jsonl`.

### `POST /webhooks/n8n/ingest`
- Loads and normalizes uploaded files.
- Accepts:

```json
{
  "user_id": "demo-user-001",
  "files": [
    "data/sample/income.csv",
    "data/sample/expenses.csv",
    "data/sample/debts.csv",
    "data/sample/assets.csv"
  ],
  "run_id": "n8n-run-001"
}
```

### `POST /webhooks/n8n/analyze`
- Triggers the full LangGraph financial coach workflow.
- Accepts:

```json
{
  "user_id": "demo-user-001",
  "query": "Create a safe debt payoff, savings, and budget optimization plan.",
  "files": [
    "data/sample/income.csv",
    "data/sample/expenses.csv",
    "data/sample/debts.csv",
    "data/sample/assets.csv"
  ],
  "send_notifications": true
}
```

## Running Locally Without Docker

### Terminal 1

```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Terminal 2

```powershell
.venv\Scripts\Activate.ps1
python run_webhooks.py
```

## Running With Docker Compose

```powershell
docker compose up --build
```

Services:
- Streamlit: `http://localhost:8501`
- Webhook server: `http://localhost:8000/health`
- n8n: `http://localhost:5678`

## Importing The Sample n8n Workflows

1. Open `http://localhost:5678`.
2. Import [n8n_financial_coach_ingestion.json](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows/n8n_financial_coach_ingestion.json).
3. Import [n8n_financial_coach_notification.json](/C:/Users/iNNOVATEQ/Documents/New%20project/workflows/n8n_financial_coach_notification.json).
4. Set `N8N_NOTIFICATION_WEBHOOK` in `.env` to your notification workflow URL if you want callback delivery.

## Audit Logging

- All analysis requests and completions are appended to `data/audit/audit_log.jsonl`.
- Notification attempts are logged as separate audit events.
- The audit webhook endpoint exposes recent events for dashboarding or review.
