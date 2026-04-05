"""Shared state schema for the multi-agent financial advisor graph."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class FinancialAgentState(TypedDict):
    """State passed through every node in the LangGraph."""

    # Conversation history (LangGraph auto-merges via add_messages)
    messages: Annotated[list, add_messages]

    # User context — loaded once at session start
    user_id: str
    financial_profile: dict[str, Any]
    debt_records: list[dict[str, Any]]

    # RAG context — populated by retrieval node
    retrieved_context: str

    # Routing
    current_agent: str
