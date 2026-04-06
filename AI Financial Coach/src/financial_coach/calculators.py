from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass
class DebtScenario:
    strategy: str
    months_to_payoff: int
    interest_paid: float
    ordering: List[str]


def monthly_cash_flow(income_df: pd.DataFrame, expense_df: pd.DataFrame, debt_df: pd.DataFrame) -> Dict[str, float]:
    net_income = float(income_df["net_monthly"].sum()) if not income_df.empty else 0.0
    expenses = float(expense_df["amount"].sum()) if not expense_df.empty else 0.0
    debt_minimums = float(debt_df["minimum_payment"].sum()) if not debt_df.empty else 0.0
    disposable = net_income - expenses - debt_minimums
    return {
        "net_income": round(net_income, 2),
        "core_expenses": round(expenses, 2),
        "debt_minimums": round(debt_minimums, 2),
        "disposable_income": round(disposable, 2),
    }


def emergency_fund_target(expense_df: pd.DataFrame, months: int = 6) -> float:
    essential_mask = expense_df["essentiality"].fillna("").str.lower().isin(["essential", "fixed"])
    essential_spend = float(expense_df.loc[essential_mask, "amount"].sum()) if not expense_df.empty else 0.0
    return round(essential_spend * months, 2)


def _simulate_strategy(debt_df: pd.DataFrame, ordering: List[str], extra_payment: float) -> DebtScenario:
    debts = debt_df.copy()
    debts["monthly_rate"] = debts["apr"] / 100 / 12
    balances = debts.set_index("debt_name")["balance"].to_dict()
    minimums = debts.set_index("debt_name")["minimum_payment"].to_dict()
    rates = debts.set_index("debt_name")["monthly_rate"].to_dict()

    months = 0
    interest_paid = 0.0
    max_months = 600

    while any(balance > 0.01 for balance in balances.values()) and months < max_months:
        months += 1
        leftover = extra_payment
        for name in ordering:
            balance = balances[name]
            if balance <= 0.01:
                continue
            interest = balance * rates[name]
            interest_paid += interest
            balances[name] = balance + interest
            payment = minimums[name]
            if name == next((d for d in ordering if balances[d] > 0.01), name):
                payment += leftover
            balances[name] = max(0.0, balances[name] - payment)

    return DebtScenario(
        strategy=" / ".join(ordering[:3]),
        months_to_payoff=months,
        interest_paid=round(interest_paid, 2),
        ordering=ordering,
    )


def compare_payoff_strategies(debt_df: pd.DataFrame, extra_payment: float) -> Dict[str, object]:
    if debt_df.empty:
        return {
            "snowball": {"months_to_payoff": 0, "interest_paid": 0.0, "ordering": []},
            "avalanche": {"months_to_payoff": 0, "interest_paid": 0.0, "ordering": []},
        }

    snowball_order = debt_df.sort_values(["balance", "apr"]).debt_name.tolist()
    avalanche_order = debt_df.sort_values(["apr", "balance"], ascending=[False, True]).debt_name.tolist()
    snowball = _simulate_strategy(debt_df, snowball_order, max(extra_payment, 0.0))
    avalanche = _simulate_strategy(debt_df, avalanche_order, max(extra_payment, 0.0))
    return {
        "snowball": {
            "months_to_payoff": snowball.months_to_payoff,
            "interest_paid": snowball.interest_paid,
            "ordering": snowball.ordering,
        },
        "avalanche": {
            "months_to_payoff": avalanche.months_to_payoff,
            "interest_paid": avalanche.interest_paid,
            "ordering": avalanche.ordering,
        },
    }


def budget_opportunities(expense_df: pd.DataFrame) -> List[Dict[str, object]]:
    if expense_df.empty:
        return []
    grouped = (
        expense_df.groupby(["category", "essentiality"], dropna=False)["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )
    suggestions: List[Dict[str, object]] = []
    for _, row in grouped.head(8).iterrows():
        category = str(row["category"])
        essentiality = str(row["essentiality"]).lower()
        amount = float(row["amount"])
        reducible = 0.0 if essentiality in {"essential", "fixed"} else amount * 0.15
        suggestions.append(
            {
                "category": category,
                "monthly_spend": round(amount, 2),
                "suggested_reduction": round(reducible, 2),
                "impact": "low lifestyle impact" if reducible > 0 else "monitor only",
            }
        )
    return suggestions
