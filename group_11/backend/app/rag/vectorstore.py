"""
In-memory vector store for demo mode.
In production, swap to Supabase pgvector via VECTOR_STORE_PROVIDER env var.
"""

import logging
from typing import Optional

from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)

# Per-user in-memory stores (demo mode)
_stores: dict[str, InMemoryVectorStore] = {}


def get_vectorstore(user_id: str) -> InMemoryVectorStore:
    """Get or create a vector store for a user."""
    if user_id not in _stores:
        _stores[user_id] = InMemoryVectorStore(embedding=get_embeddings())
    return _stores[user_id]


def add_documents(user_id: str, documents: list[Document]) -> int:
    """Add documents to a user's vector store. Returns count of docs added."""
    if not documents:
        return 0
    store = get_vectorstore(user_id)
    store.add_documents(documents)
    logger.info(f"Added {len(documents)} documents for user {user_id}")
    return len(documents)


def search(user_id: str, query: str, k: int = 5) -> list[Document]:
    """Search a user's vector store for relevant documents."""
    store = get_vectorstore(user_id)
    try:
        return store.similarity_search(query, k=k)
    except Exception as e:
        logger.warning(f"Vector search failed for user {user_id}: {e}")
        return []


def clear_user_store(user_id: str) -> None:
    """Remove a user's vector store."""
    _stores.pop(user_id, None)
