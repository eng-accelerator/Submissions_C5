"""
Dashboard endpoints — aggregated financial overview.
Uses uploaded document data via RAG + LLM extraction.
Falls back to sample data if no documents are uploaded.
"""

import logging

from fastapi import APIRouter

from app.agents.tools import (
    analyze_budget,
    calculate_debt_to_income,
    simulate_payoff,
)
from app.rag.vectorstore import search
from app.services.financial_plan import _call_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_DEMO_USER = "demo-user"

# Cache extracted data so we don't call LLM on every dashboard request
_dashboard_cache: dict[str, dict] = {}

EXTRACT_PROMPT = """\
You are a financial data extractor. From the documents below, extract all financial details.
Return ONLY valid JSON with this exact structure (use 0 if unknown, [] if none):
{{
  "credit_score": 0,
  "credit_score_band": "",
  "total_accounts": 0,
  "active_accounts": 0,
  "monthly_income": 0,
  "monthly_expenses": 0,
  "risk_flags": [],
  "positive_factors": [],
  "accounts": [
    {{
      "name": "",
      "lender": "",
      "type": "",
      "status": "",
      "current_balance": 0,
      "credit_limit": 0,
      "loan_amount": 0,
      "overdue_amount": 0,
      "utilization_percent": 0,
      "remarks": []
    }}
  ],
  "expenses": {{
    "Rent": 0,
    "Groceries": 0,
    "Transport": 0,
    "Utilities": 0,
    "EMI": 0,
    "Entertainment": 0,
    "Shopping": 0,
    "Dining": 0,
    "Insurance": 0,
    "Subscriptions": 0
  }}
}}

Extract real values from the documents. For expenses, estimate from transactions if available.

DOCUMENTS:
{context}
"""


def _get_dashboard_data() -> dict:
    """Extract financial data from uploaded documents via RAG + LLM, with caching."""
    if _DEMO_USER in _dashboard_cache:
        return _dashboard_cache[_DEMO_USER]

    # Search for relevant document chunks
    queries = [
        "credit score accounts debt loans balance overdue",
        "income salary earnings monthly",
        "expenses spending transactions categories",
        "payment history delinquency risk",
    ]
    all_chunks: list[str] = []
    for q in queries:
        docs = search(_DEMO_USER, q, k=5)
        for doc in docs:
            if doc.page_content not in all_chunks:
                all_chunks.append(doc.page_content)

    if not all_chunks:
        return {}

    context = "\n\n".join(all_chunks)
    logger.info("Dashboard extraction: using %d unique document chunks", len(all_chunks))

    data = _call_agent(EXTRACT_PROMPT, context)
    if "raw" not in data:
        _dashboard_cache[_DEMO_USER] = data
    return data


def _estimate_interest_rate(account_type: str) -> float:
    rates = {
        "Credit Card": 36.0,
        "Personal Loan": 14.0,
        "Consumer Loan": 18.0,
        "Home Loan": 8.5,
        "Auto Loan": 10.0,
    }
    return rates.get(account_type, 15.0)


def _estimate_min_payment(balance: float, acc_type: str) -> float:
    if acc_type == "Credit Card":
        return max(balance * 0.05, 500)
    return max(balance * 0.03, 1000)


@router.get("/overview")
async def overview():
    """Financial overview from uploaded documents."""
    data = _get_dashboard_data()
    if not data:
        return {
            "credit_score": 0,
            "credit_score_band": "Unknown",
            "total_debt": 0,
            "total_overdue": 0,
            "monthly_income": 0,
            "monthly_expenses": 0,
            "total_min_payments": 0,
            "debt_count": 0,
            "active_accounts": 0,
            "risk_flags": [],
            "positive_factors": [],
            "message": "No documents uploaded. Upload financial documents to see your dashboard.",
        }

    accounts = data.get("accounts", [])
    total_debt = sum(a.get("current_balance", 0) for a in accounts)
    total_overdue = sum(a.get("overdue_amount", 0) for a in accounts)
    total_min = sum(
        _estimate_min_payment(a.get("current_balance", 0), a.get("type", ""))
        for a in accounts
        if a.get("current_balance", 0) > 0
    )

    return {
        "credit_score": data.get("credit_score", 0),
        "credit_score_band": data.get("credit_score_band", "Unknown"),
        "total_debt": total_debt,
        "total_overdue": total_overdue,
        "monthly_income": data.get("monthly_income", 0),
        "monthly_expenses": data.get("monthly_expenses", 0),
        "total_min_payments": round(total_min, 2),
        "debt_count": len(accounts),
        "active_accounts": data.get("active_accounts", 0),
        "risk_flags": data.get("risk_flags", []),
        "positive_factors": data.get("positive_factors", []),
    }


@router.get("/debt-breakdown")
async def debt_breakdown():
    """Debt broken down by account."""
    data = _get_dashboard_data()
    if not data:
        return {"debts": [], "dti": {}}

    accounts = data.get("accounts", [])
    debts = []
    for acc in accounts:
        balance = acc.get("current_balance", 0)
        acc_type = acc.get("type", "Unknown")
        debts.append({
            "name": f"{acc.get('lender', 'Unknown')} - {acc_type}",
            "lender": acc.get("lender", "Unknown"),
            "type": acc_type,
            "status": acc.get("status", "Unknown"),
            "balance": balance,
            "credit_limit": acc.get("credit_limit"),
            "loan_amount": acc.get("loan_amount"),
            "interest_rate": _estimate_interest_rate(acc_type),
            "min_payment": _estimate_min_payment(balance, acc_type),
            "overdue_amount": acc.get("overdue_amount", 0),
            "utilization_percent": acc.get("utilization_percent"),
            "remarks": acc.get("remarks", []),
        })

    total_min = sum(d["min_payment"] for d in debts if d["balance"] > 0)
    income = data.get("monthly_income", 50000)
    dti = calculate_debt_to_income.invoke({
        "monthly_income": income,
        "total_monthly_debt_payments": total_min,
    })

    return {"debts": debts, "dti": dti}


@router.get("/payoff-plan")
async def payoff_plan():
    """Compare avalanche vs snowball payoff strategies."""
    data = _get_dashboard_data()
    if not data:
        return {"message": "No documents uploaded.", "strategies": []}

    accounts = data.get("accounts", [])
    payable = []
    for acc in accounts:
        balance = acc.get("current_balance", 0)
        status = acc.get("status", "")
        if balance > 0 and status != "Written-off":
            acc_type = acc.get("type", "Unknown")
            payable.append({
                "name": f"{acc.get('lender', 'Unknown')} - {acc_type}",
                "balance": balance,
                "interest_rate": _estimate_interest_rate(acc_type),
                "min_payment": _estimate_min_payment(balance, acc_type),
            })

    if not payable:
        return {"message": "No active debts to create a payoff plan for.", "strategies": []}

    avalanche = simulate_payoff.invoke({
        "debts": payable,
        "strategy": "avalanche",
        "extra_monthly_payment": 5000,
    })
    snowball = simulate_payoff.invoke({
        "debts": payable,
        "strategy": "snowball",
        "extra_monthly_payment": 5000,
    })

    return {
        "extra_monthly_payment": 5000,
        "strategies": [avalanche, snowball],
        "recommendation": "avalanche" if avalanche["total_interest"] <= snowball["total_interest"] else "snowball",
    }


@router.get("/budget-analysis")
async def budget_analysis():
    """Budget analysis against 50/30/20 benchmarks."""
    data = _get_dashboard_data()
    if not data:
        return {"breakdown": None}

    income = data.get("monthly_income", 50000)
    expenses = data.get("expenses", {})

    # Filter out zero values
    expenses = {k: v for k, v in expenses.items() if v > 0}

    if not expenses:
        # Fallback: estimate from monthly_expenses
        total_exp = data.get("monthly_expenses", 35000)
        expenses = {
            "Essentials": round(total_exp * 0.5),
            "Lifestyle": round(total_exp * 0.3),
            "Other": round(total_exp * 0.2),
        }

    result = analyze_budget.invoke({
        "monthly_income": income,
        "expenses": expenses,
    })

    return result


@router.get("/insights")
async def insights():
    """AI-generated financial insights from uploaded data."""
    data = _get_dashboard_data()
    if not data:
        return {"insights": [{"type": "tip", "title": "Upload Documents", "description": "Upload your financial documents (credit report, bank statements) to get personalized insights."}]}

    insights_list = []

    score = data.get("credit_score", 0)
    band = data.get("credit_score_band", "")
    if score > 0 and score < 600:
        insights_list.append({
            "type": "warning",
            "title": "Low Credit Score",
            "description": f"Your credit score of {score} ({band}) needs urgent attention. Focus on clearing overdue payments and reducing credit utilization.",
        })
    elif score >= 700:
        insights_list.append({
            "type": "positive",
            "title": "Good Credit Score",
            "description": f"Your credit score of {score} ({band}) is in good shape. Keep maintaining timely payments.",
        })

    # Check accounts for issues
    accounts = data.get("accounts", [])
    written_off = [a for a in accounts if a.get("status") == "Written-off"]
    if written_off:
        insights_list.append({
            "type": "critical",
            "title": "Written-Off Account",
            "description": f"You have {len(written_off)} written-off account(s). Contact the lender to negotiate a settlement.",
        })

    overdue = [a for a in accounts if a.get("overdue_amount", 0) > 0]
    if overdue:
        total_overdue = sum(a.get("overdue_amount", 0) for a in overdue)
        insights_list.append({
            "type": "critical",
            "title": "Overdue Payments",
            "description": f"You have overdue payments totaling {total_overdue:,.0f} across {len(overdue)} account(s). Clear these immediately to prevent score damage.",
        })

    # Positive factors
    for factor in data.get("positive_factors", []):
        insights_list.append({
            "type": "positive",
            "title": "Positive Signal",
            "description": factor,
        })

    # Risk flags
    for flag in data.get("risk_flags", []):
        insights_list.append({
            "type": "warning",
            "title": "Risk Flag",
            "description": flag,
        })

    # Savings potential
    income = data.get("monthly_income", 0)
    expenses = data.get("monthly_expenses", 0)
    if income > 0 and income > expenses:
        savings = income - expenses
        insights_list.append({
            "type": "tip",
            "title": "Savings Opportunity",
            "description": f"You have ~{savings:,.0f}/month surplus. Consider allocating 50% to debt payoff and 50% to an emergency fund.",
        })

    return {"insights": insights_list}


@router.post("/refresh")
async def refresh_dashboard():
    """Clear the dashboard cache so next request re-extracts from documents."""
    _dashboard_cache.pop(_DEMO_USER, None)
    return {"status": "refreshed"}
