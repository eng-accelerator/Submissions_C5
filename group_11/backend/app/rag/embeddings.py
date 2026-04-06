"""
Embedding model configuration.
Uses OpenRouter or OpenAI depending on LLM_PROVIDER setting.
Falls back to a simple hash-based embedding for demo if no API key works.
"""

import hashlib
import logging
from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.settings import get_settings

logger = logging.getLogger(__name__)


class SimpleHashEmbeddings(Embeddings):
    """Deterministic hash-based embeddings for demo/offline use.
    Not suitable for real semantic search but allows the pipeline to run."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_text(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._hash_text(text)

    def _hash_text(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        # Convert hex to floats in [-1, 1]
        values: list[float] = []
        for i in range(0, min(len(h), self.dimensions * 2), 2):
            byte_val = int(h[i : i + 2], 16)
            values.append((byte_val / 127.5) - 1.0)
        # Pad if needed
        while len(values) < self.dimensions:
            values.append(0.0)
        return values[: self.dimensions]


@lru_cache
def get_embeddings() -> Embeddings:
    """Return the best available embedding model."""
    settings = get_settings()

    # Try OpenAI embeddings (works with direct OpenAI key)
    if settings.openai_api_key and settings.openai_api_key != "sk-REPLACE_ME":
        logger.info("Using OpenAI embeddings: %s", settings.openai_embedding_model)
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )

    # Try OpenRouter for embeddings (limited model support)
    if settings.openrouter_api_key:
        try:
            logger.info("Trying OpenRouter embeddings")
            emb = OpenAIEmbeddings(
                model="openai/text-embedding-3-small",
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
            )
            # Quick test
            emb.embed_query("test")
            logger.info("OpenRouter embeddings working")
            return emb
        except Exception as e:
            logger.warning("OpenRouter embeddings failed (%s), using hash fallback", e)

    # Fallback — demo-quality, no API needed
    logger.info("Using hash-based embeddings (demo mode, no API needed)")
    return SimpleHashEmbeddings()
