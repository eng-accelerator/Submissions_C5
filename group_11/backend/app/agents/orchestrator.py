"""
LangGraph multi-agent orchestrator.

Graph: load_context -> route -> specialist -> respond
"""

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.agents.prompts import (
    BUDGET_ADVISOR_PROMPT,
    DEBT_ANALYZER_PROMPT,
    ORCHESTRATOR_PROMPT,
    PAYOFF_OPTIMIZER_PROMPT,
    SAVINGS_STRATEGIST_PROMPT,
)
from app.agents.state import FinancialAgentState
from app.agents.tools import ALL_TOOLS
from app.settings import get_settings

logger = logging.getLogger(__name__)

SPECIALIST_PROMPTS = {
    "debt_analyzer": DEBT_ANALYZER_PROMPT,
    "savings_strategist": SAVINGS_STRATEGIST_PROMPT,
    "budget_advisor": BUDGET_ADVISOR_PROMPT,
    "payoff_optimizer": PAYOFF_OPTIMIZER_PROMPT,
}

AGENT_DISPLAY_NAMES = {
    "orchestrator": "Financial Coach",
    "debt_analyzer": "Debt Analyzer",
    "savings_strategist": "Savings Strategist",
    "budget_advisor": "Budget Advisor",
    "payoff_optimizer": "Payoff Optimizer",
}


def _get_llm() -> ChatOpenAI:
    """Create LLM instance based on provider config (openrouter or openai)."""
    settings = get_settings()

    if settings.llm_provider == "openrouter" and settings.openrouter_api_key:
        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=settings.agent_temperature,
            default_headers={
                "HTTP-Referer": "https://demoai-one.vercel.app",
                "X-Title": "DemoAI Financial Coach",
            },
        )

    # Fallback to direct OpenAI
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.agent_temperature,
    )


def _build_context_string(state: FinancialAgentState) -> str:
    """Build a context string from the user's financial data."""
    parts: list[str] = []

    profile = state.get("financial_profile") or {}
    if profile:
        parts.append(f"Financial Profile: {json.dumps(profile, indent=2, default=str)}")

    debts = state.get("debt_records") or []
    if debts:
        parts.append(f"Debt Records: {json.dumps(debts, indent=2, default=str)}")

    rag_ctx = state.get("retrieved_context") or ""
    if rag_ctx:
        parts.append(f"Retrieved Documents:\n{rag_ctx}")

    if not parts:
        return (
            "No financial documents have been uploaded yet. "
            "Ask the user to upload their credit report, bank statement, or other financial documents "
            "at the Upload page so you can analyze their data. "
            "In the meantime, you can answer general financial questions."
        )
    return "\n\n".join(parts)


# ── Graph nodes ──────────────────────────────────────────────


def load_context_node(state: FinancialAgentState) -> dict[str, Any]:
    """Load user financial context from uploaded documents via RAG."""
    from app.rag.vectorstore import search

    user_id = state.get("user_id", "demo-user")
    messages = state.get("messages", [])

    # RAG: retrieve relevant chunks from uploaded documents
    retrieved_context = ""
    if messages:
        last_message = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
        docs = search(user_id, last_message, k=8)
        if docs:
            retrieved_context = "\n\n".join(
                f"[Document chunk]: {doc.page_content}" for doc in docs
            )
            logger.info("RAG: retrieved %d chunks for query", len(docs))

    # Build profile from retrieved context (no hardcoded data)
    profile = {}
    debts: list[dict] = []
    if not retrieved_context:
        logger.info("No documents uploaded yet — agents will work with user's questions only")

    return {
        "financial_profile": profile,
        "debt_records": debts,
        "retrieved_context": retrieved_context,
    }


def route_node(state: FinancialAgentState) -> dict[str, Any]:
    """Orchestrator decides which specialist to call."""
    llm = _get_llm()
    messages = [SystemMessage(content=ORCHESTRATOR_PROMPT)] + list(state["messages"])
    response = llm.invoke(messages)
    content = response.content if isinstance(response.content, str) else str(response.content)

    # Parse routing decision
    route = "self"
    response_text = content
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("ROUTE:"):
            route = line.split(":", 1)[1].strip().lower()
            response_text = "\n".join(
                l for l in content.split("\n") if not l.strip().startswith("ROUTE:")
            ).strip()
            break

    if route == "self" or route not in SPECIALIST_PROMPTS:
        # Orchestrator answers directly
        return {
            "current_agent": "orchestrator",
            "messages": [AIMessage(content=response_text, name="orchestrator")],
        }

    return {"current_agent": route}


def specialist_node(state: FinancialAgentState) -> dict[str, Any]:
    """Run the selected specialist agent with tools."""
    agent_name = state["current_agent"]
    prompt_template = SPECIALIST_PROMPTS.get(agent_name)
    if not prompt_template:
        return {
            "messages": [AIMessage(content="I'm not sure how to help with that. Could you rephrase?", name="orchestrator")],
        }

    context = _build_context_string(state)
    system_prompt = prompt_template.format(context=context)

    llm = _get_llm().bind_tools(ALL_TOOLS)
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

    # Run with tool calling loop
    max_tool_rounds = 5
    for _ in range(max_tool_rounds):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            # No more tool calls — final answer
            content = response.content if isinstance(response.content, str) else str(response.content)
            return {
                "messages": [AIMessage(content=content, name=agent_name)],
            }

        # Execute tool calls
        from langchain_core.messages import ToolMessage

        for tc in response.tool_calls:
            tool_fn = next((t for t in ALL_TOOLS if t.name == tc["name"]), None)
            if tool_fn:
                try:
                    result = tool_fn.invoke(tc["args"])
                    messages.append(ToolMessage(content=json.dumps(result, default=str), tool_call_id=tc["id"]))
                except Exception as e:
                    messages.append(ToolMessage(content=f"Tool error: {e}", tool_call_id=tc["id"]))
            else:
                messages.append(ToolMessage(content=f"Unknown tool: {tc['name']}", tool_call_id=tc["id"]))

    # Exhausted tool rounds — get final response without tools
    final = _get_llm().invoke(messages)
    content = final.content if isinstance(final.content, str) else str(final.content)
    return {
        "messages": [AIMessage(content=content, name=agent_name)],
    }


def should_call_specialist(state: FinancialAgentState) -> str:
    """Conditional edge: skip specialist if orchestrator already answered."""
    if state.get("current_agent") == "orchestrator":
        return "end"
    return "specialist"


# ── Build the graph ──────────────────────────────────────────


def build_graph() -> StateGraph:
    """Build and compile the multi-agent financial advisor graph."""
    graph = StateGraph(FinancialAgentState)

    graph.add_node("load_context", load_context_node)
    graph.add_node("route", route_node)
    graph.add_node("specialist", specialist_node)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "route")
    graph.add_conditional_edges("route", should_call_specialist, {
        "specialist": "specialist",
        "end": END,
    })
    graph.add_edge("specialist", END)

    return graph.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
