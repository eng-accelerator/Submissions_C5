"""
rag.py — Agentic RAG (Retrieval Augmented Generation) Module

Implements:
  - Document chunking and embedding
  - ChromaDB vector store persistence
  - Semantic similarity retrieval
  - Agentic RAG: the agent decides WHAT to retrieve and WHEN

The Retriever Agent uses this to:
  1. Embed all raw sources into a collection
  2. Retrieve semantically relevant chunks per sub-query
  3. Build an enriched context window for downstream agents
"""

from __future__ import annotations

import os
import re
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

CHROMA_DIR   = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHUNK_SIZE   = 800      # characters per chunk
CHUNK_OVERLAP = 150
TOP_K        = 5        # chunks returned per query

# Use HuggingFace sentence-transformers (free, no API key needed)
# Falls back gracefully if transformers not installed
_EF_CACHE: Optional[Any] = None


def _get_embedding_function():
    global _EF_CACHE
    if _EF_CACHE is not None:
        return _EF_CACHE
    try:
        _EF_CACHE = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("[RAG] Using SentenceTransformer embeddings (all-MiniLM-L6-v2)")
    except Exception as e:
        logger.warning(f"[RAG] SentenceTransformer unavailable ({e}), using default.")
        _EF_CACHE = embedding_functions.DefaultEmbeddingFunction()
    return _EF_CACHE


# ──────────────────────────────────────────────
# ChromaDB Client (persistent)
# ──────────────────────────────────────────────

def _get_chroma_client() -> chromadb.PersistentClient:
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DIR)


# ──────────────────────────────────────────────
# Chunking
# ──────────────────────────────────────────────

def chunk_text(text: str, source_id: str, source_url: str) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks for embedding."""
    chunks = []
    text = re.sub(r"\s+", " ", text).strip()
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append({
            "id": f"{source_id}_chunk_{idx}",
            "text": chunk,
            "source_id": source_id,
            "source_url": source_url,
            "chunk_index": idx,
        })
        start = end - CHUNK_OVERLAP
        idx += 1
    return chunks


# ──────────────────────────────────────────────
# RAG Store — CRUD on a Chroma collection
# ──────────────────────────────────────────────

class RAGStore:
    """
    Manages a ChromaDB collection for a single research session.
    Each research run gets its own isolated collection.
    """

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = _get_chroma_client()
        self.ef = _get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"[RAG] Collection '{collection_name}' ready.")

    # ── Ingest ────────────────────────────────

    def add_sources(self, sources: List[Dict[str, Any]]) -> int:
        """Chunk and embed a list of source dicts."""
        all_ids, all_docs, all_metas = [], [], []

        for source in sources:
            content = source.get("content", "")
            if not content or len(content) < 50:
                continue
            chunks = chunk_text(
                text=content,
                source_id=source.get("id", str(uuid.uuid4())),
                source_url=source.get("url", ""),
            )
            for chunk in chunks:
                all_ids.append(chunk["id"])
                all_docs.append(chunk["text"])
                all_metas.append({
                    "source_id":  chunk["source_id"],
                    "source_url": chunk["source_url"],
                    "chunk_index": chunk["chunk_index"],
                    "title": source.get("title", ""),
                    "source_type": source.get("source_type", "web"),
                    "domain": source.get("domain", ""),
                })

        if not all_ids:
            return 0

        # Batch upsert (avoid duplicate IDs)
        BATCH = 100
        for i in range(0, len(all_ids), BATCH):
            self.collection.upsert(
                ids=all_ids[i:i+BATCH],
                documents=all_docs[i:i+BATCH],
                metadatas=all_metas[i:i+BATCH],
            )

        logger.info(f"[RAG] Indexed {len(all_ids)} chunks into '{self.collection_name}'")
        return len(all_ids)

    # ── Retrieve ──────────────────────────────

    def query(self, query_text: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """Semantic search — returns top_k most relevant chunks."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error(f"[RAG] Query error: {e}")
            return []

        chunks = []
        docs      = results.get("documents", [[]])[0]
        metas     = results.get("metadatas", [[]])[0]
        distances = results.get("distances",  [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            chunks.append({
                "text":        doc,
                "source_url":  meta.get("source_url", ""),
                "source_id":   meta.get("source_id", ""),
                "title":       meta.get("title", ""),
                "source_type": meta.get("source_type", ""),
                "domain":      meta.get("domain", ""),
                "similarity":  round(1 - dist, 4),  # cosine: 1=identical
            })

        logger.info(f"[RAG] Retrieved {len(chunks)} chunks for: '{query_text[:60]}'")
        return chunks

    def multi_query(self, queries: List[str], top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        Agentic RAG: run multiple sub-queries and merge unique results.
        Deduplicates by (source_id, chunk_index).
        """
        seen, merged = set(), []
        for q in queries:
            for chunk in self.query(q, top_k=top_k):
                key = f"{chunk['source_id']}_{chunk['text'][:30]}"
                if key not in seen:
                    seen.add(key)
                    merged.append(chunk)
        # Re-rank by similarity
        merged.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return merged[:top_k * 2]  # return generous set for agent to reason over

    # ── Utility ───────────────────────────────

    def count(self) -> int:
        return self.collection.count()

    def delete_collection(self):
        self.client.delete_collection(self.collection_name)
        logger.info(f"[RAG] Deleted collection '{self.collection_name}'")


# ──────────────────────────────────────────────
# Global registry of active RAG stores
# (one per research session, keyed by collection name)
# ──────────────────────────────────────────────

_STORE_REGISTRY: Dict[str, RAGStore] = {}


def get_rag_store(collection_name: str) -> RAGStore:
    """Get or create a RAGStore for a session."""
    if collection_name not in _STORE_REGISTRY:
        _STORE_REGISTRY[collection_name] = RAGStore(collection_name)
    return _STORE_REGISTRY[collection_name]
