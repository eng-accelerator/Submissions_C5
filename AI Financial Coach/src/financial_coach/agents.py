from __future__ import annotations

from typing import Dict, List

import pandas as pd

from financial_coach.calculators import (
    budget_opportunities,
    compare_payoff_strategies,
    emergency_fund_target,
    monthly_cash_flow,
)
from financial_coach.currency import format_money
from financial_coach.guardrails import LlamaGuardModerator
from financial_coach.llm import HybridReasoner


class DebtAnalyzerAgent:
    def analyze(self, debt_df: pd.DataFrame, cash_flow: Dict[str, float]) -> Dict[str, object]:
        extra_payment = max(cash_flow["disposable_income"] * 0.6, 0.0)
        strategies = compare_payoff_strategies(debt_df, extra_payment=extra_payment)
        preferred = "avalanche"
        if strategies["snowball"]["months_to_payoff"] < strategies["avalanche"]["months_to_payoff"]:
            preferred = "snowball"
        return {
            "extra_payment_budget": round(extra_payment, 2),
            "strategies": strategies,
            "recommended_strategy": preferred,
        }


class SavingsStrategyAgent:
    def analyze(
        self,
        income_df: pd.DataFrame,
        expense_df: pd.DataFrame,
        debt_df: pd.DataFrame,
        asset_df: pd.DataFrame,
    ) -> Dict[str, object]:
        cash_flow = monthly_cash_flow(income_df, expense_df, debt_df)
        target = emergency_fund_target(expense_df, months=6)
        liquid_assets = (
            asset_df.loc[asset_df["liquidity_tier"].fillna("").str.lower() == "high", "balance"].sum()
            if not asset_df.empty
            else 0.0
        )
        gap = max(target - float(liquid_assets), 0.0)
        savings_allocation = max(cash_flow["disposable_income"] * 0.4, 0.0)
        return {
            "cash_flow": cash_flow,
            "emergency_fund_target": round(target, 2),
            "liquid_assets": round(float(liquid_assets), 2),
            "emergency_fund_gap": round(gap, 2),
            "recommended_monthly_savings": round(savings_allocation, 2),
        }


class BudgetOptimizationAgent:
    def analyze(self, expense_df: pd.DataFrame) -> Dict[str, object]:
        opportunities = budget_opportunities(expense_df)
        total_savings = round(sum(item["suggested_reduction"] for item in opportunities), 2)
        return {
            "opportunities": opportunities,
            "total_potential_reduction": total_savings,
        }


class FinancialCoachOrchestrator:
    def __init__(self) -> None:
        self.reasoner = HybridReasoner()
        self.moderator = LlamaGuardModerator()

    def _build_direct_answer(
        self,
        query: str,
        cash_flow: Dict[str, float],
        savings_plan: Dict[str, object],
        debt_plan: Dict[str, object],
        budget_plan: Dict[str, object],
        currency_code: str,
    ) -> str:
        query_lower = query.lower()
        recommended_savings = float(savings_plan.get("recommended_monthly_savings", 0.0))
        disposable_income = float(cash_flow.get("disposable_income", 0.0))
        emergency_target = float(savings_plan.get("emergency_fund_target", 0.0))
        emergency_gap = float(savings_plan.get("emergency_fund_gap", 0.0))
        debt_strategy = str(debt_plan.get("recommended_strategy", "avalanche"))
        budget_reduction = float(budget_plan.get("total_potential_reduction", 0.0))

        if "saving" in query_lower or "savings" in query_lower:
            return (
                f"Your recommended monthly savings is {format_money(recommended_savings, currency_code)}. "
                f"You currently have {format_money(disposable_income, currency_code)} of monthly disposable income, "
                f"and your emergency fund gap is {format_money(emergency_gap, currency_code)} against a {format_money(emergency_target, currency_code)} target."
            )
        if "debt" in query_lower or "payoff" in query_lower:
            return (
                f"Your current recommended debt strategy is {debt_strategy}. "
                f"Available extra debt payment budget is {format_money(float(debt_plan.get('extra_payment_budget', 0)), currency_code)} per month."
            )
        if "budget" in query_lower or "spend" in query_lower or "expense" in query_lower:
            return (
                f"Your budget review found about {format_money(budget_reduction, currency_code)} of potential monthly reductions "
                "in discretionary categories before touching essentials."
            )
        if "income" in query_lower or "cash flow" in query_lower:
            return (
                f"Your monthly net income is {format_money(float(cash_flow.get('net_income', 0)), currency_code)}, "
                f"with {format_money(float(cash_flow.get('disposable_income', 0)), currency_code)} left after expenses and debt minimums."
            )
        if "emergency" in query_lower:
            return (
                f"Your emergency fund target is {format_money(emergency_target, currency_code)}, and the remaining gap is {format_money(emergency_gap, currency_code)}."
            )
        return (
            f"You have {format_money(disposable_income, currency_code)} of monthly disposable income and "
            f"{format_money(recommended_savings, currency_code)} is the current recommended monthly savings allocation."
        )

    @staticmethod
    def _is_targeted_metric_question(query: str) -> bool:
        query_lower = query.lower()
        metric_terms = [
            "saving",
            "savings",
            "debt",
            "payoff",
            "budget",
            "spend",
            "expense",
            "income",
            "cash flow",
            "emergency",
            "disposable",
        ]
        broader_terms = [
            "why",
            "how",
            "should",
            "recommend",
            "compare",
            "best",
            "explain",
            "evidence",
            "plan",
            "strategy",
        ]
        has_metric = any(term in query_lower for term in metric_terms)
        has_broader = any(term in query_lower for term in broader_terms)
        return has_metric and not has_broader

    def answer_chat_question(
        self,
        question: str,
        state: Dict[str, object],
    ) -> str:
        cash_flow = state.get("savings_plan", {}).get("cash_flow", {})
        savings_plan = state.get("savings_plan", {})
        debt_plan = state.get("debt_plan", {})
        budget_plan = state.get("budget_plan", {})
        currency_code = str(state.get("currency_code", "INR"))
        if self._is_targeted_metric_question(question):
            return self._build_direct_answer(
                query=question,
                cash_flow=cash_flow,
                savings_plan=savings_plan,
                debt_plan=debt_plan,
                budget_plan=budget_plan,
                currency_code=currency_code,
            )

        payload = {
            "user_id": state.get("user_id"),
            "question": question,
            "instructions": [
                "Answer the user's specific question using only the provided analysis state.",
                "Do not redo financial math beyond the provided deterministic outputs.",
                "If document hits are available, use them as supporting evidence.",
                "Keep the answer concise and directly responsive to the question.",
            ],
            "context": {
                "cash_flow": cash_flow,
                "savings_plan": savings_plan,
                "debt_plan": debt_plan,
                "budget_plan": budget_plan,
                "action_plan": state.get("action_plan", {}),
                "market_context": state.get("market_context", {}),
                "document_hits": state.get("document_hits", []),
                "retrieval_summary": state.get("retrieval_summary", {}),
                "currency_code": currency_code,
            },
        }
        return self.reasoner.generate_explanation(payload)

    def assemble(
        self,
        user_id: str,
        query: str,
        cash_flow: Dict[str, float],
        debt_plan: Dict[str, object],
        savings_plan: Dict[str, object],
        budget_plan: Dict[str, object],
        market_context: Dict[str, object],
        currency_code: str,
    ) -> Dict[str, object]:
        action_items: List[str] = []
        if debt_plan.get("recommended_strategy"):
            action_items.append(
                "Direct the majority of extra debt payments to the "
                f"{debt_plan['recommended_strategy']} strategy while maintaining all minimum payments."
            )
        if savings_plan.get("recommended_monthly_savings", 0) > 0:
            action_items.append(
                f"Automate {format_money(float(savings_plan['recommended_monthly_savings']), currency_code)} monthly into a high-liquidity emergency reserve."
            )
        if budget_plan.get("total_potential_reduction", 0) > 0:
            action_items.append(
                f"Trim up to {format_money(float(budget_plan['total_potential_reduction']), currency_code)} monthly from discretionary categories before cutting essentials."
            )
        if cash_flow.get("disposable_income", 0) < 0:
            action_items.insert(
                0,
                "Stabilize cash flow immediately by reducing discretionary spend and pausing non-essential savings contributions.",
            )

        payload = {
            "user_id": user_id,
            "query": query,
            "action_items": action_items,
            "context": {
                "cash_flow": cash_flow,
                "debt_plan": debt_plan,
                "savings_plan": savings_plan,
                "budget_plan": budget_plan,
            },
            "market_context": market_context,
        }
        direct_answer = self._build_direct_answer(
            query=query,
            cash_flow=cash_flow,
            savings_plan=savings_plan,
            debt_plan=debt_plan,
            budget_plan=budget_plan,
            currency_code=currency_code,
        )
        explanation = self.reasoner.generate_explanation(payload)
        moderation = self.moderator.moderate(query, explanation)
        return {
            "action_items": action_items,
            "direct_answer": direct_answer,
            "explanation": explanation,
            "moderation": moderation,
        }
