from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CanonicalSchema:
    name: str
    columns: List[str]
    description: str


SCHEMAS: Dict[str, CanonicalSchema] = {
    "income": CanonicalSchema(
        name="income",
        columns=[
            "user_id",
            "scope",
            "source_id",
            "income_type",
            "employer",
            "gross_monthly",
            "net_monthly",
            "frequency",
            "confidence",
            "effective_date",
        ],
        description="Normalized recurring and one-off income sources.",
    ),
    "expenses": CanonicalSchema(
        name="expenses",
        columns=[
            "user_id",
            "scope",
            "source_id",
            "category",
            "merchant",
            "amount",
            "frequency",
            "essentiality",
            "confidence",
            "transaction_date",
        ],
        description="Normalized expense lines classified into budget categories.",
    ),
    "debts": CanonicalSchema(
        name="debts",
        columns=[
            "user_id",
            "scope",
            "source_id",
            "debt_name",
            "debt_type",
            "balance",
            "apr",
            "minimum_payment",
            "due_day",
            "secured",
            "confidence",
        ],
        description="Normalized debt obligations for payoff planning and simulation.",
    ),
    "assets": CanonicalSchema(
        name="assets",
        columns=[
            "user_id",
            "scope",
            "source_id",
            "asset_name",
            "asset_type",
            "institution",
            "balance",
            "liquidity_tier",
            "risk_level",
            "valuation_date",
            "confidence",
        ],
        description="Normalized liquid and non-liquid asset holdings.",
    ),
}
