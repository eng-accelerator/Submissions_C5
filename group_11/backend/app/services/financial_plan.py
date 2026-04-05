"""
Financial Plan Generator — runs all 4 specialist agents on merged document data
to produce a unified, structured financial plan.
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.tools import ALL_TOOLS
from app.rag.vectorstore import search
from app.settings import get_settings

logger = logging.getLogger(__name__)

# Store plans in memory (demo mode)
_plans: dict[str, dict] = {}


def _get_llm() -> ChatOpenAI:
    settings = get_settings()
    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=0.1,
            timeout=90,
            default_headers={
                "HTTP-Referer": "https://demoai-one.vercel.app",
                "X-Title": "DemoAI Plan",
            },
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.1,
        timeout=90,
    )


SNAPSHOT_PROMPT = """\
You are a financial data extractor. From the documents below, extract a financial snapshot.
Return ONLY valid JSON with this exact structure (use 0 if unknown):
{{
  "monthly_income": 0,
  "monthly_expenses": 0,
  "monthly_surplus": 0,
  "credit_score": 0,
  "credit_score_band": "",
  "total_debt": 0,
  "total_savings": 0,
  "debt_to_income_pct": 0,
  "accounts": [{{"name": "", "type": "", "balance": 0, "status": ""}}]
}}

DOCUMENTS:
{context}
"""

DEBT_PLAN_PROMPT = """\
You are a debt advisor. Based on the financial data below, write the URGENT ACTIONS section of a financial plan.
Return ONLY valid JSON:
{{
  "risk_level": "low|moderate|high|critical",
  "actions": [
    {{"priority": 1, "action": "...", "reason": "...", "impact": "high|medium|low"}}
  ]
}}
Keep to 3-5 most important actions. Be specific with numbers.

FINANCIAL DATA:
{context}
"""

BUDGET_PLAN_PROMPT = """\
You are a budget advisor. Based on the financial data below, write the BUDGET PLAN section.
Return ONLY valid JSON:
{{
  "recommended_budget": {{
    "needs": {{"amount": 0, "pct": 50, "categories": ["rent", "groceries"]}},
    "wants": {{"amount": 0, "pct": 30, "categories": ["entertainment"]}},
    "savings": {{"amount": 0, "pct": 20, "categories": ["emergency fund"]}}
  }},
  "current_vs_recommended": [
    {{"category": "...", "current": 0, "recommended": 0, "action": "..."}}
  ],
  "top_cuts": [
    {{"area": "...", "save_amount": 0, "suggestion": "..."}}
  ]
}}
Be specific. Use actual numbers from the data.

FINANCIAL DATA:
{context}
"""

PAYOFF_PLAN_PROMPT = """\
You are a debt payoff strategist. Based on the financial data below, write the DEBT PAYOFF section.
Return ONLY valid JSON:
{{
  "strategy": "avalanche|snowball",
  "reason": "...",
  "extra_monthly_payment": 0,
  "total_months": 0,
  "total_interest_saved": 0,
  "debt_free_date": "...",
  "payoff_order": [
    {{"name": "...", "balance": 0, "payoff_month": 0}}
  ]
}}
Calculate with realistic numbers from the data.

FINANCIAL DATA:
{context}
"""

SAVINGS_PLAN_PROMPT = """\
You are a savings strategist. Based on the financial data below, write the SAVINGS GOALS section.
Return ONLY valid JSON:
{{
  "phases": [
    {{
      "name": "Phase 1",
      "months": "1-6",
      "goal": "...",
      "monthly_amount": 0,
      "target_total": 0
    }}
  ],
  "emergency_fund_target": 0,
  "emergency_fund_months": 0
}}
Be realistic given the user's income and debts. Max 3 phases.

FINANCIAL DATA:
{context}
"""


def _call_agent(prompt_template: str, context: str) -> dict:
    """Call an agent with structured output prompt. Parse JSON from response."""
    llm = _get_llm()
    prompt = prompt_template.format(context=context)
    response = llm.invoke([
        SystemMessage(content="You return ONLY valid JSON. No markdown, no explanation, just JSON."),
        HumanMessage(content=prompt),
    ])
    text = response.content if isinstance(response.content, str) else str(response.content)

    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Agent returned invalid JSON, using raw text")
        return {"raw": text}


def generate_plan(user_id: str = "demo-user") -> dict:
    """Generate a full financial plan from all uploaded documents."""

    # 1. Gather all document context via RAG
    queries = [
        "income salary earnings deductions net pay",
        "bank balance transactions deposits withdrawals spending",
        "credit score debt accounts loans utilization delinquency",
        "expenses budget categories monthly spending",
    ]
    all_chunks: list[str] = []
    for q in queries:
        docs = search(user_id, q, k=5)
        for doc in docs:
            if doc.page_content not in all_chunks:
                all_chunks.append(doc.page_content)

    if not all_chunks:
        return {"error": "No documents uploaded. Please upload financial documents first."}

    context = "\n\n".join(all_chunks)
    logger.info("Plan generation: using %d unique document chunks", len(all_chunks))

    # 2. Run all 4 agents
    logger.info("Generating financial snapshot...")
    snapshot = _call_agent(SNAPSHOT_PROMPT, context)

    logger.info("Generating debt actions...")
    debt_actions = _call_agent(DEBT_PLAN_PROMPT, context)

    logger.info("Generating budget plan...")
    budget_plan = _call_agent(BUDGET_PLAN_PROMPT, context)

    logger.info("Generating payoff plan...")
    payoff_plan = _call_agent(PAYOFF_PLAN_PROMPT, context)

    logger.info("Generating savings goals...")
    savings_goals = _call_agent(SAVINGS_PLAN_PROMPT, context)

    # 3. Combine into plan
    plan = {
        "id": str(uuid.uuid4())[:8],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot,
        "debt_actions": debt_actions,
        "budget_plan": budget_plan,
        "payoff_plan": payoff_plan,
        "savings_goals": savings_goals,
    }

    # Store
    _plans[user_id] = plan
    logger.info("Financial plan generated: %s", plan["id"])
    return plan


def get_plan(user_id: str = "demo-user") -> dict | None:
    return _plans.get(user_id)
