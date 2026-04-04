"""
llm_factory.py — LLM provider abstraction
Supports Anthropic Claude (primary) with OpenRouter as fallback.
Uses LangChain chat model interface throughout.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOpenAI  # OpenRouter uses OAI-compatible API
from loguru import logger

load_dotenv()


# ──────────────────────────────────────────────
# Model aliases
# ──────────────────────────────────────────────

CLAUDE_SONNET  = "claude-sonnet-4-5"
CLAUDE_HAIKU   = "claude-haiku-4-5-20251001"

# Via OpenRouter
OR_MIXTRAL     = "nousresearch/hermes-4-70b"
OR_LLAMA3      = "perplexity/sonar-deep-research"


@lru_cache(maxsize=8)
def get_llm(
    model: str = CLAUDE_SONNET,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    streaming: bool = False,
) -> ChatAnthropic:
    """
    Return a LangChain-compatible LLM.
    Falls back to OpenRouter if Anthropic key is absent.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
        logger.info(f"[LLM Factory] Using Anthropic model: {model}")
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            anthropic_api_key=anthropic_key,
        )

    if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
        or_model = OR_MIXTRAL if "sonnet" in model else OR_LLAMA3
        logger.warning(f"[LLM Factory] Falling back to OpenRouter: {or_model}")
        return ChatOpenAI(
            model=or_model,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
        )

    raise EnvironmentError(
        "No LLM API key found. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY in .env"
    )


def get_fast_llm(streaming: bool = False):
    """Haiku / lighter model for quick classification tasks."""
    return get_llm(model=CLAUDE_HAIKU, temperature=0.0, max_tokens=1024, streaming=streaming)


def get_reasoning_llm(streaming: bool = False):
    """Full Sonnet for deep reasoning tasks."""
    return get_llm(model=CLAUDE_SONNET, temperature=0.3, max_tokens=8096, streaming=streaming)
