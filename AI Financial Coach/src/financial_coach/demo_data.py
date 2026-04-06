from __future__ import annotations

from typing import Dict

import pandas as pd


def build_demo_tables(user_id: str) -> Dict[str, pd.DataFrame]:
    income = pd.DataFrame(
        [
            {
                "user_id": user_id,
                "scope": "private",
                "source_id": "demo-income",
                "income_type": "salary",
                "employer": "Acme Systems",
                "gross_monthly": 9800,
                "net_monthly": 7200,
                "frequency": "monthly",
                "confidence": 0.99,
                "effective_date": "2026-03-01",
            },
            {
                "user_id": user_id,
                "scope": "private",
                "source_id": "demo-income",
                "income_type": "freelance",
                "employer": "Independent",
                "gross_monthly": 1200,
                "net_monthly": 900,
                "frequency": "monthly",
                "confidence": 0.91,
                "effective_date": "2026-03-01",
            },
        ]
    )
    expenses = pd.DataFrame(
        [
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Housing", "merchant": "Rent", "amount": 2100, "frequency": "monthly", "essentiality": "essential", "confidence": 0.99, "transaction_date": "2026-03-01"},
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Groceries", "merchant": "FreshMart", "amount": 650, "frequency": "monthly", "essentiality": "essential", "confidence": 0.98, "transaction_date": "2026-03-01"},
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Dining", "merchant": "Restaurants", "amount": 420, "frequency": "monthly", "essentiality": "discretionary", "confidence": 0.92, "transaction_date": "2026-03-01"},
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Transport", "merchant": "Metro Fuel", "amount": 360, "frequency": "monthly", "essentiality": "essential", "confidence": 0.93, "transaction_date": "2026-03-01"},
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Streaming", "merchant": "Subscriptions", "amount": 95, "frequency": "monthly", "essentiality": "discretionary", "confidence": 0.95, "transaction_date": "2026-03-01"},
            {"user_id": user_id, "scope": "private", "source_id": "demo-expenses", "category": "Travel", "merchant": "Weekend Trips", "amount": 300, "frequency": "monthly", "essentiality": "discretionary", "confidence": 0.8, "transaction_date": "2026-03-01"},
        ]
    )
    debts = pd.DataFrame(
        [
            {"user_id": user_id, "scope": "private", "source_id": "demo-debts", "debt_name": "Credit Card Platinum", "debt_type": "credit_card", "balance": 7200, "apr": 22.99, "minimum_payment": 210, "due_day": 18, "secured": False, "confidence": 0.99},
            {"user_id": user_id, "scope": "private", "source_id": "demo-debts", "debt_name": "Auto Loan", "debt_type": "auto", "balance": 11800, "apr": 6.2, "minimum_payment": 340, "due_day": 9, "secured": True, "confidence": 0.99},
            {"user_id": user_id, "scope": "private", "source_id": "demo-debts", "debt_name": "Student Loan", "debt_type": "student", "balance": 16400, "apr": 4.8, "minimum_payment": 180, "due_day": 12, "secured": False, "confidence": 0.97},
        ]
    )
    assets = pd.DataFrame(
        [
            {"user_id": user_id, "scope": "private", "source_id": "demo-assets", "asset_name": "Emergency Savings", "asset_type": "cash", "institution": "North Bank", "balance": 4200, "liquidity_tier": "high", "risk_level": "low", "valuation_date": "2026-03-31", "confidence": 0.99},
            {"user_id": user_id, "scope": "private", "source_id": "demo-assets", "asset_name": "401k", "asset_type": "retirement", "institution": "Workplace Plan", "balance": 38200, "liquidity_tier": "low", "risk_level": "medium", "valuation_date": "2026-03-31", "confidence": 0.96},
        ]
    )
    return {
        "income": income,
        "expenses": expenses,
        "debts": debts,
        "assets": assets,
    }


def build_demo_raw_text(user_id: str) -> str:
    return "\n".join(
        [
            f"User profile for {user_id}. Salary credited monthly with a recurring freelance side income.",
            "Expense note: housing, groceries, utilities, transport, dining, streaming, and leisure travel are the main categories.",
            "Debt note: credit card balance has the highest APR, followed by auto and student loan obligations.",
            "Asset note: liquid emergency savings are available, while retirement assets are less liquid.",
            "Advisory objective: balance debt payoff, emergency savings, and budget optimization using user-scoped evidence only.",
        ]
    )
