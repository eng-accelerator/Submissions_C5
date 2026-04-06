from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Dict, List, Tuple

import pandas as pd

from financial_coach.auth import OzeroFgaClient

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional dependency at runtime
    SentenceTransformer = None


@dataclass
class DocumentHit:
    chunk_id: int
    score: float
    retrieval_mode: str
    text: str


@dataclass
class RetrievalBundle:
    tables: Dict[str, pd.DataFrame]
    summaries: Dict[str, List[str]]
    document_hits: List[DocumentHit]


class HybridDocumentRetriever:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self, chunk_size: int = 280):
        self.chunk_size = chunk_size
        self._model = None

    def retrieve(self, query: str, raw_text: str, top_k: int = 3) -> List[DocumentHit]:
        chunks = self._chunk_text(raw_text)
        if not chunks:
            return []
        embedding_hits = self._embedding_search(query, chunks, top_k)
        if embedding_hits:
            return embedding_hits
        return self._lexical_search(query, chunks, top_k)

    def _chunk_text(self, raw_text: str) -> List[str]:
        clean = " ".join(raw_text.split())
        if not clean:
            return []
        words = clean.split(" ")
        return [
            " ".join(words[index : index + self.chunk_size])
            for index in range(0, len(words), self.chunk_size)
        ]

    def _load_model(self):
        if self._model is not None:
            return self._model
        if SentenceTransformer is None:
            return None
        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception:  # pragma: no cover - model download/runtime issues
            self._model = None
        return self._model

    def _embedding_search(self, query: str, chunks: List[str], top_k: int) -> List[DocumentHit]:
        model = self._load_model()
        if model is None:
            return []
        try:
            query_vector = model.encode([query], normalize_embeddings=True)[0]
            chunk_vectors = model.encode(chunks, normalize_embeddings=True)
        except Exception:  # pragma: no cover - runtime/model issues
            return []

        scored: List[DocumentHit] = []
        for idx, chunk_vector in enumerate(chunk_vectors):
            score = float(sum(a * b for a, b in zip(query_vector, chunk_vector)))
            scored.append(
                DocumentHit(
                    chunk_id=idx,
                    score=round(score, 4),
                    retrieval_mode="embedding",
                    text=chunks[idx],
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

    def _lexical_search(self, query: str, chunks: List[str], top_k: int) -> List[DocumentHit]:
        query_terms = [term for term in query.lower().split() if len(term) > 2]
        scored: List[DocumentHit] = []
        for idx, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            overlap = sum(chunk_lower.count(term) for term in query_terms)
            denominator = sqrt(max(len(chunk_lower.split()), 1))
            score = overlap / denominator if denominator else 0.0
            scored.append(
                DocumentHit(
                    chunk_id=idx,
                    score=round(score, 4),
                    retrieval_mode="lexical",
                    text=chunk,
                )
            )
        return [item for item in sorted(scored, key=lambda hit: hit.score, reverse=True)[:top_k] if item.score > 0]


class TabularRagAgent:
    def __init__(self, fga_client: OzeroFgaClient):
        self.fga_client = fga_client
        self.document_retriever = HybridDocumentRetriever()

    def retrieve(
        self,
        user_id: str,
        query: str,
        tables: Dict[str, pd.DataFrame],
        raw_text: str = "",
    ) -> RetrievalBundle:
        authorized: Dict[str, pd.DataFrame] = {}
        summaries: Dict[str, List[str]] = {}
        query_lower = query.lower()

        for table_name, frame in tables.items():
            authorized_table = self.fga_client.authorize_table(user_id, table_name, frame, "read")
            authorized_rows = self.fga_client.authorize_rows(user_id, table_name, authorized_table, "read")
            filtered, summary = self._filter_rows(query_lower, table_name, authorized_rows)
            authorized[table_name] = filtered
            summaries[table_name] = summary

        document_hits = self.document_retriever.retrieve(query=query, raw_text=raw_text)
        summaries["hybrid_documents"] = [
            f"hits={len(document_hits)}",
            "mode=embedding" if any(hit.retrieval_mode == "embedding" for hit in document_hits) else "mode=lexical_or_none",
        ]
        return RetrievalBundle(tables=authorized, summaries=summaries, document_hits=document_hits)

    def _filter_rows(
        self, query_lower: str, table_name: str, frame: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        if frame.empty:
            return frame, ["No authorized rows available."]

        filtered = frame
        if table_name == "expenses":
            if "budget" in query_lower or "spend" in query_lower:
                filtered = frame.sort_values("amount", ascending=False).head(12)
        elif table_name == "debts":
            if "debt" in query_lower or "payoff" in query_lower:
                filtered = frame.sort_values("apr", ascending=False)
        elif table_name == "income":
            filtered = frame.sort_values("net_monthly", ascending=False)
        elif table_name == "assets":
            if "emergency" in query_lower or "savings" in query_lower:
                filtered = frame.sort_values("balance", ascending=False)

        summary = [
            f"authorized_rows={len(filtered)}",
            f"columns={', '.join(filtered.columns[:6])}",
        ]
        return filtered, summary

    @staticmethod
    def inject_context(bundle: RetrievalBundle) -> Dict[str, List[dict]]:
        injected: Dict[str, List[dict]] = {}
        for table_name, frame in bundle.tables.items():
            injected[table_name] = frame.to_dict(orient="records")
        return injected
