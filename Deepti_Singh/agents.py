"""
agents.py — All Agent Implementations for Multi-Agent Deep Researcher

Agents (in pipeline order):
  1. OrchestratorAgent   — Master coordinator, routes and loops
  2. QueryClarifierAgent — Asks clarification if query is ambiguous
  3. RetrieverAgent      — Fetches from web/arxiv, embeds into RAG
  4. AnalyzerAgent       — Summarizes, validates, finds contradictions
  5. FactCheckerAgent    — Cross-references key claims (sub-agent of Analyzer)
  6. InsightAgent        — Generates hypotheses via reasoning chains
  7. ReportBuilderAgent  — Compiles structured Markdown report
  8. VisualizerAgent     — Generates charts from numerical data

Each agent is a function: ResearchState -> ResearchState
LangGraph calls them as nodes.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from llm_factory import get_fast_llm, get_reasoning_llm
from rag import get_rag_store
from state import (
    AgentLog, AgentStatus, ClarificationQuestion, Contradiction,
    Insight, ResearchState, Source, SourceType, VisualizationSpec,
)
from tools import (
    arxiv_search, combine_search_results, duckduckgo_search,
    fact_check_claim, tavily_search, web_scraper,
)


# ──────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────

def _log_start(state: ResearchState, name: str) -> ResearchState:
    log = AgentLog(agent_name=name, status=AgentStatus.RUNNING,
                   started_at=datetime.now(timezone.utc).isoformat())
    state.agent_logs.append(log)
    logger.info(f"[{name}] ▶ Starting")
    return state


def _log_done(state: ResearchState, name: str, notes: str = "") -> ResearchState:
    for log in reversed(state.agent_logs):
        if log.agent_name == name and log.status == AgentStatus.RUNNING:
            log.status = AgentStatus.DONE
            log.finished_at = datetime.now(timezone.utc).isoformat()
            log.notes = notes
            break
    logger.info(f"[{name}] ✓ Done. {notes}")
    return state


def _log_error(state: ResearchState, name: str, error: str) -> ResearchState:
    for log in reversed(state.agent_logs):
        if log.agent_name == name and log.status == AgentStatus.RUNNING:
            log.status = AgentStatus.FAILED
            log.error = error
            log.finished_at = datetime.now(timezone.utc).isoformat()
            break
    logger.error(f"[{name}] ✗ Error: {error}")
    return state


def _llm_call(system: str, human: str, fast: bool = False) -> str:
    """Simple single-turn LLM call."""
    llm = get_fast_llm() if fast else get_reasoning_llm()
    messages = [SystemMessage(content=system), HumanMessage(content=human)]
    try:
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"[LLM Call] Failed: {e}")
        raise  # Re-raise to let the agent handle or log it


def _parse_json_from_llm(text: str) -> Any:
    """Extract JSON from LLM output that may contain markdown fences."""
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find first JSON object/array
        match = re.search(r"(\{[\s\S]+\}|\[[\s\S]+\])", text)
        if match:
            return json.loads(match.group(1))
        raise


def _sources_to_text(sources: List[Source], max_chars_each: int = 800) -> str:
    lines = []
    for i, s in enumerate(sources, 1):
        lines.append(
            f"[{i}] {s.title}\n"
            f"    URL: {s.url}\n"
            f"    Type: {s.source_type} | Domain: {s.domain}\n"
            f"    Content: {s.content[:max_chars_each]}\n"
        )
    return "\n".join(lines)


# ══════════════════════════════════════════════
# Agent 0 — Orchestrator
# ══════════════════════════════════════════════

def orchestrator_agent(state: ResearchState) -> ResearchState:
    """
    Master coordinator. Decides:
      - Whether clarification is needed
      - Whether retrieval was sufficient
      - Whether to loop back for more research
      - When the pipeline is complete
    """
    state = _log_start(state, "OrchestratorAgent")

    query = state.original_query.strip()
    if not query:
        state.error_message = "No query provided."
        return _log_error(state, "OrchestratorAgent", "Empty query")

    # First pass: decompose query into sub-queries
    if not state.sub_queries:
        system = (
            "You are a research orchestrator. Given a user research query, "
            "your job is to:\n"
            "1. Determine if the query needs clarification (ambiguous, too broad, or too vague).\n"
            "2. Decompose the query into 3-5 focused sub-questions.\n"
            "3. Return a JSON object with keys:\n"
            "   - needs_clarification: bool\n"
            "   - clarification_reason: str (if needed)\n"
            "   - sub_queries: list[str]\n"
            "   - clarified_query: str (refined version of the original)\n"
            "Return ONLY valid JSON, no markdown."
        )
        human = f"Research query: {query}"

        try:
            result = _parse_json_from_llm(_llm_call(system, human, fast=True))
            state.clarification_needed = result.get("needs_clarification", False)
            state.sub_queries = result.get("sub_queries", [query])
            state.clarified_query = result.get("clarified_query", query)
        except Exception as e:
            logger.warning(f"[Orchestrator] JSON parse failed: {e}. Using defaults.")
            state.clarification_needed = False
            state.sub_queries = [query]
            state.clarified_query = query

    # Subsequent passes: decide if more research is needed
    elif state.iteration > 0:
        n_sources = len(state.verified_sources)
        n_insights = len(state.insights)
        system = (
            "You are evaluating whether a research pipeline has gathered sufficient information.\n"
            "Return JSON with:\n"
            "  - needs_more_research: bool\n"
            "  - reason: str\n"
            "  - additional_queries: list[str] (if needs_more_research is true)\n"
            "Return ONLY valid JSON."
        )
        human = (
            f"Original query: {query}\n"
            f"Iteration: {state.iteration}/{state.max_iterations}\n"
            f"Sources verified: {n_sources}\n"
            f"Insights generated: {n_insights}\n"
            f"Contradictions found: {len(state.contradictions)}\n"
            "Is the research complete or should we search for more?"
        )
        try:
            result = _parse_json_from_llm(_llm_call(system, human, fast=True))
            state.needs_more_research = (
                result.get("needs_more_research", False)
                and state.iteration < state.max_iterations
            )
            if state.needs_more_research:
                extra = result.get("additional_queries", [])
                state.sub_queries = list(set(state.sub_queries + extra))
        except Exception:
            state.needs_more_research = False

    state = _log_done(
        state, "OrchestratorAgent",
        f"sub_queries={len(state.sub_queries)}, "
        f"clarification_needed={state.clarification_needed}"
    )
    return state


# ══════════════════════════════════════════════
# Agent 1 — Query Clarifier
# ══════════════════════════════════════════════

def query_clarifier_agent(state: ResearchState) -> ResearchState:
    """
    Generates clarifying questions when the query is ambiguous.
    In API mode: stores questions in state for UI to display.
    If user has answered, incorporates their answers.
    """
    state = _log_start(state, "QueryClarifierAgent")

    # If user answered, incorporate their answers
    if state.user_clarification_input:
        system = (
            "You are refining a research query based on user clarifications.\n"
            "Return a refined, precise research query as a plain string. "
            "No JSON, no markdown, just the refined query."
        )
        human = (
            f"Original query: {state.original_query}\n"
            f"Clarification questions asked:\n"
            + "\n".join(f"- {q.question}" for q in state.clarification_questions)
            + f"\n\nUser's clarification: {state.user_clarification_input}"
        )
        refined = _llm_call(system, human, fast=True)
        state.clarified_query = refined
        state.clarification_complete = True
        return _log_done(state, "QueryClarifierAgent", f"Refined: {refined[:80]}")

    # Generate clarification questions
    if not state.clarification_questions:
        system = (
            "You are a research assistant. Generate 2-3 concise clarifying questions "
            "to better understand what the user wants to research.\n"
            "Return JSON: {\"questions\": [{\"question\": str, \"purpose\": str}]}\n"
            "Return ONLY valid JSON."
        )
        human = f"Ambiguous query: {state.original_query}"
        try:
            result = _parse_json_from_llm(_llm_call(system, human, fast=True))
            state.clarification_questions = [
                ClarificationQuestion(
                    question=q["question"],
                    purpose=q.get("purpose", "")
                )
                for q in result.get("questions", [])
            ]
        except Exception as e:
            logger.warning(f"[QueryClarifier] Failed to generate questions: {e}")
            state.clarification_complete = True  # skip clarification

    return _log_done(
        state, "QueryClarifierAgent",
        f"questions={len(state.clarification_questions)}"
    )


# ══════════════════════════════════════════════
# Agent 2 — Contextual Retriever (with Agentic RAG)
# ══════════════════════════════════════════════

def retriever_agent(state: ResearchState) -> ResearchState:
    """
    Multi-source retrieval with Agentic RAG:
      1. Runs combine_search for each sub-query (Tavily + DDG + arXiv)
      2. Optionally scrapes promising URLs for full content
      3. Embeds all sources into ChromaDB
      4. Uses agentic multi-query RAG to retrieve relevant chunks
      5. Updates state.raw_sources and state.rag_chunks
    """
    state = _log_start(state, "RetrieverAgent")

    query = state.clarified_query or state.original_query
    sub_queries = state.sub_queries or [query]

    # ── Step 1: Multi-source search ───────────
    raw_results: List[Dict] = []
    seen_urls: set = set()

    for sq in sub_queries:
        results = combine_search_results.invoke({
            "query": sq,
            "use_tavily": True,
            "use_duckduckgo": True,
            "use_arxiv": True,
            "max_per_source": 5,
        })
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                raw_results.append(r)

    logger.info(f"[Retriever] Raw results: {len(raw_results)}")

    # ── Step 2: Agentic scraping decision ─────
    # LLM decides which URLs are worth scraping for full content
    if raw_results:
        scrape_candidates = [
            r for r in raw_results
            if r.get("source_type") == "web" and len(r.get("content", "")) < 500
        ][:5]  # limit to 5 full scrapes

        for candidate in scrape_candidates:
            url = candidate.get("url", "")
            if not url:
                continue
            scraped = web_scraper.invoke({"url": url})
            if scraped.get("content"):
                # Merge scraped content into result
                candidate["content"] = scraped["content"]
                candidate["title"] = scraped.get("title", candidate.get("title", ""))

    # ── Step 3: Convert to Source objects ─────
    sources: List[Source] = []
    for r in raw_results:
        try:
            src = Source(
                id=r.get("id", _make_source_id(r.get("url", ""))),
                title=r.get("title", "Untitled"),
                url=r.get("url", ""),
                content=r.get("content", ""),
                snippet=r.get("snippet", "")[:300],
                source_type=SourceType(r.get("source_type", "web")),
                domain=r.get("domain", ""),
                published_date=r.get("published_date"),
                relevance_score=float(r.get("relevance_score", 0.5)),
                citations=int(r.get("citations", 0)),
            )
            sources.append(src)
        except Exception as e:
            logger.warning(f"[Retriever] Skipping source: {e}")

    state.raw_sources = sources

    # ── Step 4: Embed into RAG ─────────────────
    if not state.rag_collection_name:
        state.rag_collection_name = f"research_{uuid.uuid4().hex[:8]}"

    rag = get_rag_store(state.rag_collection_name)
    raw_dicts = [s.model_dump() for s in sources]
    rag.add_sources(raw_dicts)

    # ── Step 5: Agentic multi-query RAG ───────
    rag_chunks = rag.multi_query(sub_queries, top_k=6)
    state.rag_chunks = rag_chunks

    return _log_done(
        state, "RetrieverAgent",
        f"sources={len(sources)}, rag_chunks={len(rag_chunks)}, "
        f"collection={state.rag_collection_name}"
    )


def _make_source_id(url: str) -> str:
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()[:10]


# ══════════════════════════════════════════════
# Agent 3 — Critical Analysis Agent
# ══════════════════════════════════════════════

def analyzer_agent(state: ResearchState) -> ResearchState:
    """
    Summarizes each source, cross-references them, identifies contradictions,
    and scores source credibility.
    """
    state = _log_start(state, "AnalyzerAgent")

    sources = state.raw_sources
    if not sources:
        return _log_done(state, "AnalyzerAgent", "No sources to analyze")

    query = state.clarified_query or state.original_query

    # ── Per-source summarization ───────────────
    summaries: Dict[str, str] = {}
    verified: List[Source] = []

    for source in sources:
        if not source.content or len(source.content) < 80:
            continue
        system = (
            "You are a critical research analyst. Summarize this source concisely "
            "(3-5 sentences). Note: publication date, key claims, data points, "
            "and any limitations or potential biases. "
            "Rate credibility 0-1 where 1=highly credible peer-reviewed source."
            "\nReturn JSON: {\"summary\": str, \"key_claims\": [str], "
            "\"credibility_score\": float, \"data_points\": [{\"label\": str, \"value\": any}]}"
            "\nReturn ONLY valid JSON."
        )
        human = (
            f"Query context: {query}\n\n"
            f"Source: {source.title}\n"
            f"URL: {source.url}\n"
            f"Type: {source.source_type}\n"
            f"Content:\n{source.content[:2000]}"
        )
        try:
            result = _parse_json_from_llm(_llm_call(system, human, fast=False))
            summaries[source.id] = result.get("summary", "")
            source.credibility_score = float(result.get("credibility_score", 0.5))

            # Collect data points for Visualizer
            for dp in result.get("data_points", []):
                state.data_points.append({
                    "source_id": source.id,
                    "source_title": source.title,
                    **dp
                })

            verified.append(source)
        except Exception as e:
            logger.warning(f"[Analyzer] Skipping {source.id}: {e}")
            summaries[source.id] = source.snippet
            verified.append(source)

    state.summary_per_source = summaries
    state.verified_sources = [s for s in verified if s.credibility_score >= 0.2]

    # ── Cross-source analysis ──────────────────
    if len(verified) >= 2:
        all_summaries = "\n\n".join(
            f"[{i+1}] {s.title} (credibility: {s.credibility_score:.1f}):\n{summaries.get(s.id, s.snippet)}"
            for i, s in enumerate(verified[:10])
        )
        system = (
            "You are a critical analyst reviewing multiple research sources.\n"
            "Identify:\n"
            "  1. Key agreements across sources\n"
            "  2. Contradictions or conflicts between sources\n"
            "  3. Major gaps in the research\n"
            "  4. Key themes\n"
            "Return JSON:\n"
            "{\n"
            "  \"cross_source_summary\": str,\n"
            "  \"key_themes\": [str],\n"
            "  \"contradictions\": [{\n"
            "    \"claim_a\": str, \"source_a_index\": int,\n"
            "    \"claim_b\": str, \"source_b_index\": int,\n"
            "    \"explanation\": str, \"severity\": \"low|medium|high\"\n"
            "  }]\n"
            "}\n"
            "Return ONLY valid JSON."
        )
        human = (
            f"Research query: {query}\n\n"
            f"Source summaries:\n{all_summaries}"
        )
        try:
            result = _parse_json_from_llm(_llm_call(system, human))
            state.cross_source_summary = result.get("cross_source_summary", "")
            state.key_themes = result.get("key_themes", [])

            for c in result.get("contradictions", []):
                idx_a = c.get("source_a_index", 1) - 1
                idx_b = c.get("source_b_index", 2) - 1
                if 0 <= idx_a < len(verified) and 0 <= idx_b < len(verified):
                    state.contradictions.append(Contradiction(
                        claim_a=c.get("claim_a", ""),
                        source_a_id=verified[idx_a].id,
                        claim_b=c.get("claim_b", ""),
                        source_b_id=verified[idx_b].id,
                        explanation=c.get("explanation", ""),
                        severity=c.get("severity", "medium"),
                    ))
        except Exception as e:
            logger.warning(f"[Analyzer] Cross-source analysis failed: {e}")

    return _log_done(
        state, "AnalyzerAgent",
        f"verified={len(state.verified_sources)}, "
        f"contradictions={len(state.contradictions)}, "
        f"themes={len(state.key_themes)}"
    )


# ══════════════════════════════════════════════
# Agent 4 — Fact Checker (sub-agent of Analyzer)
# ══════════════════════════════════════════════

def fact_checker_agent(state: ResearchState) -> ResearchState:
    """
    Cross-references key claims from verified sources against external sources.
    Marks sources as verified and updates their credibility scores.
    """
    state = _log_start(state, "FactCheckerAgent")

    if not state.verified_sources:
        return _log_done(state, "FactCheckerAgent", "No sources to fact-check")

    # Extract key claims from summaries (top 5 sources by credibility)
    top_sources = sorted(
        state.verified_sources, key=lambda s: s.credibility_score, reverse=True
    )[:5]

    fact_check_results: Dict[str, Any] = {}

    for source in top_sources:
        summary = state.summary_per_source.get(source.id, "")
        if not summary:
            continue

        # Extract a single key claim to fact-check
        system = (
            "Extract the single most important factual claim from this summary "
            "that can be verified. Return ONLY the claim as a plain sentence."
        )
        human = f"Summary: {summary}"
        try:
            claim = _llm_call(system, human, fast=True)
            result = fact_check_claim.invoke({
                "claim": claim,
                "sources": [source.url],
            })
            verdict = result.get("verdict", "unverified")
            fact_check_results[source.id] = {
                "claim": claim,
                "verdict": verdict,
                "supporting": result.get("supporting_urls", []),
                "contradicting": result.get("contradicting_urls", []),
            }

            # Adjust credibility based on fact-check
            if verdict == "supported":
                source.credibility_score = min(1.0, source.credibility_score + 0.15)
                source.is_verified = True
            elif verdict == "contradicted":
                source.credibility_score = max(0.0, source.credibility_score - 0.2)

        except Exception as e:
            logger.warning(f"[FactChecker] Skipping {source.id}: {e}")

    state.fact_check_results = fact_check_results

    return _log_done(
        state, "FactCheckerAgent",
        f"checked={len(fact_check_results)}"
    )


# ══════════════════════════════════════════════
# Agent 5 — Insight Generation Agent
# ══════════════════════════════════════════════

def insight_agent(state: ResearchState) -> ResearchState:
    """
    Generates hypotheses and trends using Chain-of-Thought reasoning.
    Uses RAG chunks + cross-source summary for grounded reasoning.
    """
    state = _log_start(state, "InsightAgent")

    query = state.clarified_query or state.original_query
    if not state.verified_sources and not state.rag_chunks:
        return _log_done(state, "InsightAgent", "Insufficient data for insights")

    # Build rich context from RAG + analysis
    rag_context = "\n\n".join(
        f"[RAG Chunk from {c.get('title', c.get('domain', 'unknown'))}]:\n{c['text']}"
        for c in state.rag_chunks[:8]
    )
    cross_summary = state.cross_source_summary or ""
    themes = "\n".join(f"- {t}" for t in state.key_themes)

    system = (
        "You are an expert research insight generator using Chain-of-Thought reasoning.\n"
        "Based on the research gathered, generate 3-5 insights (hypotheses, trends, risks, opportunities).\n"
        "For each insight, show your step-by-step reasoning chain.\n"
        "Return JSON:\n"
        "{\n"
        "  \"insights\": [{\n"
        "    \"hypothesis\": str,\n"
        "    \"category\": \"trend|risk|opportunity|gap\",\n"
        "    \"reasoning_chain\": [str],  // 3-5 reasoning steps\n"
        "    \"confidence\": float,        // 0-1\n"
        "    \"supporting_source_ids\": [str]\n"
        "  }]\n"
        "}\n"
        "Return ONLY valid JSON."
    )
    human = (
        f"Research Query: {query}\n\n"
        f"Key Themes:\n{themes}\n\n"
        f"Cross-Source Analysis:\n{cross_summary[:1500]}\n\n"
        f"Relevant Research Chunks:\n{rag_context[:3000]}"
    )

    try:
        result = _parse_json_from_llm(_llm_call(system, human))
        source_ids = [s.id for s in state.verified_sources]

        for raw in result.get("insights", []):
            # Validate source IDs
            valid_ids = [
                sid for sid in raw.get("supporting_source_ids", [])
                if sid in source_ids
            ]
            insight = Insight(
                hypothesis=raw.get("hypothesis", ""),
                category=raw.get("category", "trend"),
                reasoning_chain=raw.get("reasoning_chain", []),
                confidence=float(raw.get("confidence", 0.5)),
                supporting_source_ids=valid_ids or source_ids[:2],
            )
            state.insights.append(insight)

    except Exception as e:
        logger.error(f"[InsightAgent] Failed: {e}")

    return _log_done(
        state, "InsightAgent",
        f"insights={len(state.insights)}"
    )


# ══════════════════════════════════════════════
# Agent 6 — Report Builder
# ══════════════════════════════════════════════

def report_builder_agent(state: ResearchState) -> ResearchState:
    """
    Compiles all pipeline outputs into a structured Markdown research report.
    Sections: Executive Summary, Methodology, Key Findings, Source Analysis,
              Contradictions, Insights, Visualizations, References.
    """
    state = _log_start(state, "ReportBuilderAgent")

    query = state.clarified_query or state.original_query
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # ── Build section helpers ──────────────────

    def _sources_section() -> str:
        if not state.verified_sources:
            return "_No sources verified._\n"
        lines = []
        for s in sorted(state.verified_sources,
                         key=lambda x: x.credibility_score, reverse=True)[:15]:
            verified_badge = "✅" if s.is_verified else "🔍"
            fc = state.fact_check_results.get(s.id, {})
            verdict_str = f" | Fact-check: **{fc.get('verdict', 'N/A')}**" if fc else ""
            lines.append(
                f"### {verified_badge} {s.title}\n"
                f"- **URL**: [{s.domain}]({s.url})\n"
                f"- **Type**: {s.source_type} | **Credibility**: {s.credibility_score:.0%}{verdict_str}\n"
                f"- **Summary**: {state.summary_per_source.get(s.id, s.snippet)}\n"
            )
        return "\n".join(lines)

    def _contradictions_section() -> str:
        if not state.contradictions:
            return "_No significant contradictions found across sources._\n"
        lines = []
        for c in state.contradictions:
            sa = next((s for s in state.verified_sources if s.id == c.source_a_id), None)
            sb = next((s for s in state.verified_sources if s.id == c.source_b_id), None)
            lines.append(
                f"**Severity: {c.severity.upper()}**\n"
                f"- Claim A ({sa.title if sa else 'Unknown'}): _{c.claim_a}_\n"
                f"- Claim B ({sb.title if sb else 'Unknown'}): _{c.claim_b}_\n"
                f"- Explanation: {c.explanation}\n"
            )
        return "\n".join(lines)

    def _insights_section() -> str:
        if not state.insights:
            return "_Insufficient data for insight generation._\n"
        lines = []
        ICONS = {"trend": "📈", "risk": "⚠️", "opportunity": "💡", "gap": "🔎"}
        for ins in state.insights:
            icon = ICONS.get(ins.category, "•")
            chain_text = "\n".join(f"  {j+1}. {step}" for j, step in enumerate(ins.reasoning_chain))
            lines.append(
                f"#### {icon} {ins.category.title()}: {ins.hypothesis}\n"
                f"**Confidence**: {ins.confidence:.0%}\n\n"
                f"**Reasoning Chain**:\n{chain_text}\n"
            )
        return "\n".join(lines)

    def _methodology_section() -> str:
        sub_q_list = "\n".join(f"- {q}" for q in state.sub_queries)
        return (
            f"**Sub-queries investigated:**\n{sub_q_list}\n\n"
            f"**Sources retrieved**: {len(state.raw_sources)}\n"
            f"**Sources verified**: {len(state.verified_sources)}\n"
            f"**RAG chunks indexed**: {len(state.rag_chunks)}\n"
            f"**Pipeline iterations**: {state.iteration + 1}\n"
            f"**Vector store collection**: `{state.rag_collection_name}`\n"
        )

    def _references_section() -> str:
        refs = []
        for i, s in enumerate(state.verified_sources, 1):
            date_str = f" ({s.published_date})" if s.published_date else ""
            refs.append(f"{i}. [{s.title}]({s.url}){date_str} — {s.domain}")
        return "\n".join(refs)

    # ── Compose full report ────────────────────
    themes_text = ", ".join(state.key_themes[:8]) or "N/A"

    # Executive summary via LLM
    exec_summary = ""
    try:
        system = (
            "Write a professional 4-6 sentence executive summary of a research report. "
            "Be precise, data-driven, and highlight the most important finding. "
            "Do not use markdown in your response — plain prose only."
        )
        human = (
            f"Query: {query}\n"
            f"Key themes: {themes_text}\n"
            f"Cross-source summary: {state.cross_source_summary[:1000]}\n"
            f"Top insight: {state.insights[0].hypothesis if state.insights else 'N/A'}"
        )
        exec_summary = _llm_call(system, human)
    except Exception:
        exec_summary = state.cross_source_summary[:500] or "Research completed."

    # Visualizations placeholder
    viz_section = ""
    if state.visualization_paths:
        viz_section = "\n## 📊 Visualizations\n\n"
        for path in state.visualization_paths:
            viz_section += f"![Chart]({path})\n\n"

    report = f"""# 🔬 Deep Research Report

**Query**: {query}
**Generated**: {now}
**Key Themes**: {themes_text}

---

## 📋 Executive Summary

{exec_summary}

---

## 🔧 Methodology

{_methodology_section()}

---

## 📚 Source Analysis

{_sources_section()}

---

## ⚡ Contradictions & Caveats

{_contradictions_section()}

---

## 💡 Insights & Hypotheses

{_insights_section()}
{viz_section}
---

## 📖 References

{_references_section()}

---
*Generated by Multi-Agent AI Deep Researcher | {now}*
"""

    state.final_report_md = report

    # Save to disk
    report_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
    os.makedirs(report_dir, exist_ok=True)
    safe_name = re.sub(r"[^\w\-]", "_", query[:40])
    path = os.path.join(report_dir, f"{safe_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    state.final_report_path = path

    return _log_done(
        state, "ReportBuilderAgent",
        f"report_path={path}, chars={len(report)}"
    )


# ══════════════════════════════════════════════
# Agent 7 — Visualizer Agent
# ══════════════════════════════════════════════

def visualizer_agent(state: ResearchState) -> ResearchState:
    """
    Generates charts from numerical data points found during analysis.
    Uses matplotlib + plotly. Saves PNGs to reports directory.
    """
    state = _log_start(state, "VisualizerAgent")

    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt
    import plotly.express as px
    import plotly.io as pio

    report_dir = os.getenv("REPORT_OUTPUT_DIR", "./reports")
    os.makedirs(report_dir, exist_ok=True)
    paths: List[str] = []

    data_points = state.data_points
    if not data_points:
        return _log_done(state, "VisualizerAgent", "No data points for visualization")

    # ── Ask LLM what charts to make ───────────
    system = (
        "Given these data points from research, suggest 1-3 charts to visualize.\n"
        "Return JSON: {\"charts\": [{\n"
        "  \"chart_type\": \"bar|line|pie\",\n"
        "  \"title\": str,\n"
        "  \"x_label\": str,\n"
        "  \"y_label\": str,\n"
        "  \"data_point_indices\": [int]  // indices into the data_points list\n"
        "}]}\n"
        "Only suggest charts that make sense with the data. Return ONLY valid JSON."
    )
    human = (
        f"Query: {state.clarified_query or state.original_query}\n"
        f"Data points (indexed from 0):\n"
        + "\n".join(
            f"[{i}] label={dp.get('label')}, value={dp.get('value')}, "
            f"source={dp.get('source_title', '')}"
            for i, dp in enumerate(data_points[:30])
        )
    )

    try:
        chart_specs_raw = _parse_json_from_llm(_llm_call(system, human, fast=True))
        chart_specs = chart_specs_raw.get("charts", [])
    except Exception as e:
        logger.warning(f"[Visualizer] Could not get chart specs: {e}")
        chart_specs = []

    for spec in chart_specs[:3]:
        try:
            indices = spec.get("data_point_indices", [])
            selected = [data_points[i] for i in indices if i < len(data_points)]
            if not selected:
                selected = data_points[:10]

            labels = [dp.get("label", f"Item {i}") for i, dp in enumerate(selected)]
            values = []
            for dp in selected:
                try:
                    values.append(float(str(dp.get("value", 0)).replace("%", "").replace(",", "")))
                except (ValueError, TypeError):
                    values.append(0.0)

            chart_type = spec.get("chart_type", "bar")
            title = spec.get("title", "Research Data")
            fname = re.sub(r"[^\w]", "_", title[:30]) + ".png"
            fpath = os.path.join(report_dir, fname)

            fig, ax = plt.subplots(figsize=(10, 5))
            if chart_type == "bar":
                ax.bar(labels, values, color="#4F8EF7")
            elif chart_type == "line":
                ax.plot(labels, values, marker="o", color="#4F8EF7", linewidth=2)
            elif chart_type == "pie":
                ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)

            ax.set_title(title, fontsize=14, fontweight="bold")
            if chart_type != "pie":
                ax.set_xlabel(spec.get("x_label", ""))
                ax.set_ylabel(spec.get("y_label", ""))
            plt.tight_layout()
            plt.savefig(fpath, dpi=150, bbox_inches="tight")
            plt.close(fig)
            paths.append(fpath)
            logger.info(f"[Visualizer] Saved chart: {fpath}")

        except Exception as e:
            logger.warning(f"[Visualizer] Chart failed: {e}")

    state.visualization_paths = paths

    return _log_done(
        state, "VisualizerAgent",
        f"charts_generated={len(paths)}"
    )
