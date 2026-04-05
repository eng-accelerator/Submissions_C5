"""
Sample financial data for demo mode (no Supabase required).
Derived from the sample_credit_score.json already in the project.
"""

import json
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_credit_score.json"


def get_sample_financial_context() -> dict:
    """Return a structured financial context from the sample credit report."""
    if not _DATA_FILE.is_file():
        return {"profile": {}, "debts": []}

    with _DATA_FILE.open(encoding="utf-8") as f:
        report = json.load(f)

    profile = {
        "name": report.get("personal_information", {}).get("name", "Demo User"),
        "credit_score": report.get("report_summary", {}).get("score", 0),
        "credit_score_band": report.get("report_summary", {}).get("score_band", "Unknown"),
        "total_accounts": report.get("report_summary", {}).get("total_accounts", 0),
        "active_accounts": report.get("report_summary", {}).get("active_accounts", 0),
        "credit_utilization": report.get("credit_utilization", {}),
        "payment_summary": report.get("payment_summary", {}),
        "risk_flags": report.get("risk_flags", []),
        "positive_factors": report.get("positive_factors", []),
        "delinquencies": report.get("delinquencies", []),
        "enquiries": report.get("enquiries", []),
        "monthly_income": 50000,  # Demo default (INR)
        "monthly_expenses": 35000,  # Demo default
    }

    debts = []
    for acc in report.get("accounts", []):
        debts.append({
            "name": f"{acc.get('lender', 'Unknown')} - {acc.get('type', 'Unknown')}",
            "lender": acc.get("lender", "Unknown"),
            "type": acc.get("type", "Unknown"),
            "status": acc.get("status", "Unknown"),
            "balance": acc.get("current_balance", 0),
            "credit_limit": acc.get("credit_limit"),
            "loan_amount": acc.get("loan_amount"),
            "interest_rate": _estimate_interest_rate(acc.get("type", "")),
            "min_payment": _estimate_min_payment(acc),
            "overdue_amount": acc.get("overdue_amount", 0),
            "utilization_percent": acc.get("utilization_percent"),
            "payment_history": acc.get("payment_history", []),
            "remarks": acc.get("remarks", []),
        })

    return {"profile": profile, "debts": debts}


def _estimate_interest_rate(account_type: str) -> float:
    """Estimate interest rate by account type (demo only)."""
    rates = {
        "Credit Card": 36.0,
        "Personal Loan": 14.0,
        "Consumer Loan": 18.0,
        "Home Loan": 8.5,
        "Auto Loan": 10.0,
    }
    return rates.get(account_type, 15.0)


def _estimate_min_payment(account: dict) -> float:
    """Estimate minimum monthly payment (demo only)."""
    balance = account.get("current_balance", 0)
    acc_type = account.get("type", "")
    if acc_type == "Credit Card":
        return max(balance * 0.05, 500)  # 5% of balance or INR 500
    # For loans, estimate EMI roughly
    return max(balance * 0.03, 1000)
