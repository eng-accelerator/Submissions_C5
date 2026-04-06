"""
graph.py — LangGraph Pipeline Wiring

Builds the multi-agent research graph with:
  - Conditional routing (clarification loop, research loop)
  - Checkpointing (LangGraph MemorySaver)
  - Streaming support

Graph flow:
  orchestrator
      ↓
  [if clarification_needed] → query_clarifier → [wait for user] → orchestrator
      ↓
  retriever
      ↓
  analyzer
      ↓
  fact_checker
      ↓
  insight
      ↓
  [if needs_more_research & iteration < max] → retriever (loop)
      ↓
  visualizer
      ↓
  report_builder
      ↓
  END
"""

from __future__ import annotations

from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents import (
    analyzer_agent,
    fact_checker_agent,
    insight_agent,
    orchestrator_agent,
    query_clarifier_agent,
    report_builder_agent,
    retriever_agent,
    visualizer_agent,
)
from state import ResearchState


# ──────────────────────────────────────────────
# Adapter: LangGraph passes dict, agents use Pydantic
# ──────────────────────────────────────────────

def _wrap(agent_fn):
    """Wrap a Pydantic-based agent for LangGraph dict interface."""
    def wrapper(state_dict: dict) -> dict:
        state = ResearchState(**state_dict)
        result = agent_fn(state)
        return result.model_dump()
    wrapper.__name__ = agent_fn.__name__
    return wrapper


# ──────────────────────────────────────────────
# Routing conditions
# ──────────────────────────────────────────────

def route_after_orchestrator(state: dict) -> Literal["query_clarifier", "retriever"]:
    """Go to clarifier if needed and not yet complete, else straight to retriever."""
    if (
        state.get("clarification_needed")
        and not state.get("clarification_complete")
        and state.get("iteration", 0) == 0
    ):
        return "query_clarifier"
    return "retriever"


def route_after_clarifier(state: dict) -> Literal["retriever", "__end__"]:
    """
    After clarifier:
    - If clarification is complete → continue to retriever
    - If questions were generated but not answered → pause (END for now, API resumes)
    """
    if state.get("clarification_complete"):
        return "retriever"
    # Questions are stored in state; API will resume with user's answer
    return "__end__"


def route_after_insight(state: dict) -> Literal["retriever", "visualizer"]:
    """Loop back to retriever if orchestrator says more research is needed."""
    needs_more = state.get("needs_more_research", False)
    iteration = state.get("iteration", 0)
    max_iter = state.get("max_iterations", 2)

    if needs_more and iteration < max_iter:
        logger.info(f"[Graph] Looping back: iteration {iteration + 1}/{max_iter}")
        return "retriever"
    return "visualizer"


def increment_iteration(state: dict) -> dict:
    """Middleware node to increment iteration counter before looping."""
    state["iteration"] = state.get("iteration", 0) + 1
    state["needs_more_research"] = False  # reset flag
    return state


# ──────────────────────────────────────────────
# Build the graph
# ──────────────────────────────────────────────

def build_graph(checkpointing: bool = True) -> StateGraph:
    """
    Construct and compile the LangGraph StateGraph.

    Args:
        checkpointing: If True, attach MemorySaver for resumable sessions.

    Returns:
        Compiled LangGraph app.
    """
    builder = StateGraph(dict)

    # ── Register nodes ─────────────────────────
    builder.add_node("orchestrator",    _wrap(orchestrator_agent))
    builder.add_node("query_clarifier", _wrap(query_clarifier_agent))
    builder.add_node("retriever",       _wrap(retriever_agent))
    builder.add_node("analyzer",        _wrap(analyzer_agent))
    builder.add_node("fact_checker",    _wrap(fact_checker_agent))
    builder.add_node("insight",         _wrap(insight_agent))
    builder.add_node("loop_increment",  increment_iteration)
    builder.add_node("visualizer",      _wrap(visualizer_agent))
    builder.add_node("report_builder",  _wrap(report_builder_agent))

    # ── Entry ──────────────────────────────────
    builder.add_edge(START, "orchestrator")

    # ── Conditional: clarification or retrieval ─
    builder.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "query_clarifier": "query_clarifier",
            "retriever":       "retriever",
        },
    )

    # ── Clarifier → either continue or wait ────
    builder.add_conditional_edges(
        "query_clarifier",
        route_after_clarifier,
        {
            "retriever": "retriever",
            "__end__":   END,
        },
    )

    # ── Main pipeline ──────────────────────────
    builder.add_edge("retriever",    "analyzer")
    builder.add_edge("analyzer",     "fact_checker")
    builder.add_edge("fact_checker", "insight")

    # ── Conditional: loop or proceed ───────────
    builder.add_conditional_edges(
        "insight",
        route_after_insight,
        {
            "retriever":  "loop_increment",  # goes through increment first
            "visualizer": "visualizer",
        },
    )
    builder.add_edge("loop_increment", "retriever")

    # ── Final ──────────────────────────────────
    builder.add_edge("visualizer",    "report_builder")
    builder.add_edge("report_builder", END)

    # ── Compile ────────────────────────────────
    if checkpointing:
        memory = MemorySaver()
        app = builder.compile(checkpointer=memory)
        logger.info("[Graph] Compiled with MemorySaver checkpointing.")
    else:
        app = builder.compile()
        logger.info("[Graph] Compiled without checkpointing.")

    return app


# ──────────────────────────────────────────────
# Singleton compiled app
# ──────────────────────────────────────────────

_APP = None

def get_app(checkpointing: bool = True):
    global _APP
    if _APP is None:
        _APP = build_graph(checkpointing=checkpointing)
    return _APP
