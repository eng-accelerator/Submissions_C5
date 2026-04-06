"""
tools.py — MCP-style Tool Definitions for the Retriever Agent
Each tool is a callable that can be bound to LangChain agents via tool-use.

Tools:
  - tavily_search      : Web search via Tavily API
  - duckduckgo_search  : Fallback web search (no key required)
  - arxiv_search       : Academic paper search
  - web_scraper        : Full page content extraction
  - combine_search     : Fan-out across all sources, deduplicate
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _clean_text(text: str, max_chars: int = 4000) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


# ──────────────────────────────────────────────
# Tool 1 — Tavily Web Search
# ──────────────────────────────────────────────

@tool
def tavily_search(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.
    Returns a list of results with title, url, content, and score.
    Best for: current events, news, general web knowledge.
    """
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or api_key == "your_tavily_api_key_here":
        logger.warning("[Tavily] No API key — skipping Tavily search.")
        return []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=True,
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "id": _make_id(r.get("url", "")),
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": _clean_text(r.get("raw_content") or r.get("content", "")),
                "snippet": r.get("content", "")[:300],
                "source_type": "web",
                "domain": _extract_domain(r.get("url", "")),
                "relevance_score": r.get("score", 0.5),
                "published_date": None,
            })
        logger.info(f"[Tavily] Got {len(results)} results for: {query}")
        return results
    except Exception as e:
        logger.error(f"[Tavily] Error: {e}")
        return []


# ──────────────────────────────────────────────
# Tool 2 — DuckDuckGo Search (no-key fallback)
# ──────────────────────────────────────────────

@tool
def duckduckgo_search(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo (no API key required).
    Returns a list of results with title, url, and snippet.
    Use as fallback when Tavily is unavailable.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "id": _make_id(r.get("href", "")),
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "content": _clean_text(r.get("body", "")),
                    "snippet": r.get("body", "")[:300],
                    "source_type": "web",
                    "domain": _extract_domain(r.get("href", "")),
                    "relevance_score": 0.5,
                    "published_date": None,
                })
        logger.info(f"[DuckDuckGo] Got {len(results)} results for: {query}")
        return results
    except Exception as e:
        logger.error(f"[DuckDuckGo] Error: {e}")
        return []


# ──────────────────────────────────────────────
# Tool 3 — arXiv Academic Paper Search
# ──────────────────────────────────────────────

@tool
def arxiv_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search arXiv for academic research papers.
    Returns papers with title, authors, abstract, arxiv_id, and URL.
    Best for: scientific topics, AI/ML research, technical domains.
    """
    try:
        import arxiv
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = []
        for paper in client.results(search):
            url = paper.entry_id
            content = (
                f"Title: {paper.title}\n"
                f"Authors: {', '.join(a.name for a in paper.authors[:5])}\n"
                f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
                f"Abstract: {paper.summary}\n"
                f"Categories: {', '.join(paper.categories)}"
            )
            results.append({
                "id": _make_id(url),
                "title": paper.title,
                "url": url,
                "content": _clean_text(content, max_chars=3000),
                "snippet": paper.summary[:300],
                "source_type": "arxiv",
                "domain": "arxiv.org",
                "relevance_score": 0.8,  # academic papers get higher base score
                "published_date": paper.published.strftime("%Y-%m-%d"),
                "citations": 0,  # arxiv API doesn't expose citation count
            })
        logger.info(f"[arXiv] Got {len(results)} papers for: {query}")
        return results
    except Exception as e:
        logger.error(f"[arXiv] Error: {e}")
        return []


# ──────────────────────────────────────────────
# Tool 4 — Web Scraper (full page content)
# ──────────────────────────────────────────────

@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4))
def _fetch_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; DeepResearcherBot/1.0; "
            "+https://github.com/your-repo)"
        )
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text


@tool
def web_scraper(url: str) -> Dict[str, Any]:
    """
    Fetch and extract clean text content from a web page URL.
    Strips navigation, ads, and boilerplate. Returns main article text.
    Use when you need the FULL content of a specific URL.
    """
    try:
        html = _fetch_url(url)
        soup = BeautifulSoup(html, "lxml")

        # Remove boilerplate tags
        for tag in soup(["script", "style", "nav", "footer", "header",
                          "aside", "advertisement", "noscript"]):
            tag.decompose()

        # Try to get main content area
        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find(id="content")
            or soup.find(class_="content")
            or soup.body
        )
        text = main.get_text(separator=" ", strip=True) if main else ""
        title = soup.title.string if soup.title else url

        return {
            "id": _make_id(url),
            "title": title,
            "url": url,
            "content": _clean_text(text, max_chars=6000),
            "snippet": text[:300],
            "source_type": "web",
            "domain": _extract_domain(url),
        }
    except Exception as e:
        logger.error(f"[WebScraper] Failed for {url}: {e}")
        return {"url": url, "content": "", "error": str(e)}


# ──────────────────────────────────────────────
# Tool 5 — Combine & Deduplicate All Search Results
# ──────────────────────────────────────────────

@tool
def combine_search_results(
    query: str,
    use_tavily: bool = True,
    use_duckduckgo: bool = True,
    use_arxiv: bool = True,
    max_per_source: int = 6,
) -> List[Dict[str, Any]]:
    """
    Fan-out search across Tavily, DuckDuckGo, and arXiv simultaneously.
    Combines, deduplicates by URL, and returns a unified ranked list.
    This is the primary retrieval tool for the Retriever Agent.
    """
    all_results: List[Dict[str, Any]] = []
    seen_urls: set = set()

    if use_tavily:
        results = tavily_search.invoke({"query": query, "max_results": max_per_source})
        all_results.extend(results)

    if use_duckduckgo:
        results = duckduckgo_search.invoke({"query": query, "max_results": max_per_source})
        all_results.extend(results)

    if use_arxiv:
        results = arxiv_search.invoke({"query": query, "max_results": max_per_source // 2})
        all_results.extend(results)

    # Deduplicate by URL
    deduped = []
    for r in all_results:
        url = r.get("url", "")
        if url not in seen_urls and url:
            seen_urls.add(url)
            deduped.append(r)

    # Sort: arxiv first (higher credibility), then by relevance
    deduped.sort(
        key=lambda x: (x.get("source_type") == "arxiv", x.get("relevance_score", 0)),
        reverse=True,
    )

    logger.info(f"[CombineSearch] Total unique results: {len(deduped)} for: {query}")
    return deduped


# ──────────────────────────────────────────────
# Tool 6 — Fact-Check via cross-reference
# ──────────────────────────────────────────────

@tool
def fact_check_claim(claim: str, sources: List[str]) -> Dict[str, Any]:
    """
    Cross-reference a specific claim against a list of source URLs.
    Returns verdict (supported/contradicted/unverified) and evidence.
    Uses DuckDuckGo to find corroborating or contradicting sources.
    """
    verification_query = f'fact check: "{claim}"'
    ddg_results = duckduckgo_search.invoke({
        "query": verification_query,
        "max_results": 4,
    })

    supporting = []
    contradicting = []

    for r in ddg_results:
        snippet = (r.get("snippet") or r.get("content", "")).lower()
        claim_lower = claim.lower()[:50]
        # Naive heuristic — LLM does real analysis in the Analyzer node
        if any(kw in snippet for kw in ["confirmed", "true", "correct", "study shows"]):
            supporting.append(r["url"])
        elif any(kw in snippet for kw in ["false", "debunked", "incorrect", "myth"]):
            contradicting.append(r["url"])

    verdict = (
        "supported" if supporting and not contradicting
        else "contradicted" if contradicting
        else "unverified"
    )

    return {
        "claim": claim,
        "verdict": verdict,
        "supporting_urls": supporting,
        "contradicting_urls": contradicting,
        "search_results": ddg_results,
    }


# ──────────────────────────────────────────────
# Expose all tools as a registry
# ──────────────────────────────────────────────

ALL_TOOLS = [
    tavily_search,
    duckduckgo_search,
    arxiv_search,
    web_scraper,
    combine_search_results,
    fact_check_claim,
]

RETRIEVER_TOOLS = [combine_search_results, arxiv_search, web_scraper]
FACT_CHECK_TOOLS = [fact_check_claim, duckduckgo_search]
