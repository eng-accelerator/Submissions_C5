"""Agent tools — financial calculations available to specialist agents."""

from langchain_core.tools import tool


@tool
def calculate_debt_to_income(monthly_income: float, total_monthly_debt_payments: float) -> dict:
    """Calculate debt-to-income ratio and assess risk level.

    Args:
        monthly_income: Gross monthly income.
        total_monthly_debt_payments: Sum of all monthly debt payments.
    """
    if monthly_income <= 0:
        return {"error": "Monthly income must be positive"}
    dti = (total_monthly_debt_payments / monthly_income) * 100
    if dti < 20:
        risk = "Low"
        advice = "Your DTI is healthy. Good position for savings and investment."
    elif dti < 36:
        risk = "Moderate"
        advice = "Manageable, but be cautious about taking on new debt."
    elif dti < 50:
        risk = "High"
        advice = "Your debt burden is heavy. Focus on paying down high-interest debt."
    else:
        risk = "Critical"
        advice = "Debt payments exceed safe limits. Consider debt consolidation or counseling."
    return {
        "dti_percent": round(dti, 1),
        "risk_level": risk,
        "advice": advice,
        "monthly_income": monthly_income,
        "monthly_debt_payments": total_monthly_debt_payments,
    }


@tool
def simulate_payoff(
    debts: list[dict],
    strategy: str = "avalanche",
    extra_monthly_payment: float = 0,
) -> dict:
    """Simulate debt payoff using avalanche or snowball strategy.

    Args:
        debts: List of dicts with keys: name, balance, interest_rate, min_payment.
        strategy: 'avalanche' (highest interest first) or 'snowball' (lowest balance first).
        extra_monthly_payment: Additional amount to put toward debt each month.
    """
    if not debts:
        return {"error": "No debts provided"}

    # Work on copies
    active = []
    for d in debts:
        active.append({
            "name": d.get("name", "Unknown"),
            "balance": float(d.get("balance", 0)),
            "rate": float(d.get("interest_rate", 0)) / 100 / 12,  # monthly rate
            "min_payment": float(d.get("min_payment", 0)),
        })

    total_paid = 0.0
    total_interest = 0.0
    months = 0
    max_months = 360  # 30 year cap
    payoff_order: list[dict] = []

    while any(d["balance"] > 0.01 for d in active) and months < max_months:
        months += 1
        extra_left = extra_monthly_payment

        # Sort by strategy
        if strategy == "avalanche":
            priority = sorted(
                [i for i, d in enumerate(active) if d["balance"] > 0.01],
                key=lambda i: active[i]["rate"],
                reverse=True,
            )
        else:
            priority = sorted(
                [i for i, d in enumerate(active) if d["balance"] > 0.01],
                key=lambda i: active[i]["balance"],
            )

        for i, d in enumerate(active):
            if d["balance"] <= 0.01:
                continue
            interest = d["balance"] * d["rate"]
            total_interest += interest
            d["balance"] += interest
            payment = min(d["min_payment"], d["balance"])
            d["balance"] -= payment
            total_paid += payment

        # Apply extra to priority target
        for i in priority:
            d = active[i]
            if d["balance"] <= 0.01 or extra_left <= 0:
                continue
            extra = min(extra_left, d["balance"])
            d["balance"] -= extra
            total_paid += extra
            extra_left -= extra
            if d["balance"] <= 0.01:
                payoff_order.append({"name": d["name"], "month": months})
            break

        # Check for newly paid off debts
        for d in active:
            if d["balance"] <= 0.01 and not any(p["name"] == d["name"] for p in payoff_order):
                payoff_order.append({"name": d["name"], "month": months})

    return {
        "strategy": strategy,
        "total_months": months,
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "payoff_order": payoff_order,
        "debt_free_date": f"~{months // 12} years {months % 12} months",
    }


@tool
def project_savings(monthly_savings: float, months: int, annual_rate: float = 4.0) -> dict:
    """Project savings growth with compound interest.

    Args:
        monthly_savings: Amount saved each month.
        months: Number of months to project.
        annual_rate: Expected annual interest rate (default 4%).
    """
    monthly_rate = annual_rate / 100 / 12
    balance = 0.0
    milestones: list[dict] = []

    for m in range(1, months + 1):
        balance += monthly_savings
        balance *= 1 + monthly_rate
        if m % 6 == 0 or m == months:
            milestones.append({"month": m, "balance": round(balance, 2)})

    total_contributed = monthly_savings * months
    return {
        "monthly_savings": monthly_savings,
        "months": months,
        "annual_rate": annual_rate,
        "final_balance": round(balance, 2),
        "total_contributed": round(total_contributed, 2),
        "interest_earned": round(balance - total_contributed, 2),
        "milestones": milestones,
    }


@tool
def analyze_budget(monthly_income: float, expenses: dict[str, float]) -> dict:
    """Analyze a budget against the 50/30/20 rule.

    Args:
        monthly_income: Gross monthly income.
        expenses: Dict mapping category name to monthly amount.
    """
    total_expenses = sum(expenses.values())
    savings_potential = monthly_income - total_expenses

    # 50/30/20 targets
    needs_target = monthly_income * 0.50
    wants_target = monthly_income * 0.30
    savings_target = monthly_income * 0.20

    # Categorize (simple heuristic)
    needs_categories = {"rent", "housing", "utilities", "groceries", "food", "insurance",
                        "healthcare", "transport", "transportation", "emi", "loan", "debt"}
    wants_categories = {"entertainment", "dining", "shopping", "subscriptions", "travel",
                        "personal", "lifestyle"}

    needs_total = sum(v for k, v in expenses.items() if k.lower() in needs_categories)
    wants_total = sum(v for k, v in expenses.items() if k.lower() in wants_categories)
    other_total = total_expenses - needs_total - wants_total

    return {
        "monthly_income": monthly_income,
        "total_expenses": round(total_expenses, 2),
        "savings_potential": round(savings_potential, 2),
        "breakdown": {
            "needs": {"actual": round(needs_total, 2), "target": round(needs_target, 2)},
            "wants": {"actual": round(wants_total, 2), "target": round(wants_target, 2)},
            "savings": {"actual": round(savings_potential, 2), "target": round(savings_target, 2)},
            "uncategorized": round(other_total, 2),
        },
        "expense_details": {k: round(v, 2) for k, v in sorted(expenses.items(), key=lambda x: -x[1])},
    }


# Collect all tools for agent binding
ALL_TOOLS = [calculate_debt_to_income, simulate_payoff, project_savings, analyze_budget]
