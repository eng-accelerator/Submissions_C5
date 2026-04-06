"""
Document upload and processing endpoints.
Uploads are processed into RAG chunks and stored in the vector store.
Each document also gets a financial summary extracted for the dashboard.
"""

import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.models.document import DocumentInfo, UploadResponse
from app.rag.loader import load_from_bytes
from app.rag.vectorstore import add_documents, clear_user_store
from app.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# In-memory document registry (demo mode)
_documents: dict[str, list[DocumentInfo]] = {}

# Demo user id
_DEMO_USER = "demo-user"


def _extract_summary(docs: list, filename: str) -> dict:
    """Extract a quick financial summary from parsed document chunks."""
    all_text = "\n".join(d.page_content for d in docs)
    text_lower = all_text.lower()

    summary: dict = {
        "type": "unknown",
        "highlights": [],
        "numbers": {},
    }

    # Detect document type
    if any(k in text_lower for k in ["credit score", "score_band", "credit_limit", "delinquenc"]):
        summary["type"] = "credit_report"
    elif any(k in text_lower for k in ["balance", "deposit", "withdrawal", "statement", "transaction"]):
        summary["type"] = "bank_statement"
    elif any(k in text_lower for k in ["salary", "pay", "gross", "net", "earnings"]):
        summary["type"] = "pay_stub"
    elif any(k in text_lower for k in ["expense", "budget", "category", "spending"]):
        summary["type"] = "expense_report"

    # Extract numbers from text
    import re
    numbers = re.findall(r'[\d,]+(?:\.\d{1,2})?', all_text)
    numeric_values = []
    for n in numbers:
        try:
            val = float(n.replace(",", ""))
            if 1 < val < 10_000_000:  # reasonable financial range
                numeric_values.append(val)
        except ValueError:
            pass

    if numeric_values:
        summary["numbers"] = {
            "count": len(numeric_values),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "total": round(sum(numeric_values), 2),
            "avg": round(sum(numeric_values) / len(numeric_values), 2),
        }

    # Extract key-value pairs for highlights
    for doc in docs[:3]:  # first 3 chunks
        lines = doc.page_content.split("\n")
        for line in lines[:10]:
            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip()
                if key and val and len(key) < 40 and len(val) < 100:
                    summary["highlights"].append({"key": key, "value": val})
                    if len(summary["highlights"]) >= 12:
                        break

    # Credit report specific
    if summary["type"] == "credit_report":
        for doc in docs:
            text = doc.page_content
            # Look for score
            score_match = re.search(r'score["\s:]*(\d{3})', text, re.IGNORECASE)
            if score_match:
                summary["credit_score"] = int(score_match.group(1))
            # Look for accounts
            account_matches = re.findall(r'(HDFC|Axis|ICICI|SBI|Bajaj|Kotak|Yes Bank|IndusInd)', text, re.IGNORECASE)
            if account_matches:
                summary["banks"] = list(set(m.title() for m in account_matches))

    summary["chunk_count"] = len(docs)
    summary["total_text_length"] = len(all_text)

    return summary


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile):
    """Upload a financial document (PDF, CSV, JSON, XLSX) for RAG processing."""
    settings = get_settings()

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lstrip(".").lower()
    if ext not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{ext} not supported. Allowed: {settings.allowed_file_types}",
        )

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Max: {settings.max_upload_size_mb}MB",
        )

    doc_id = str(uuid.uuid4())
    doc_info = DocumentInfo(
        id=doc_id,
        filename=file.filename,
        file_type=ext,
        status="processing",
    )

    try:
        import asyncio
        docs = await asyncio.to_thread(load_from_bytes, content, file.filename)
        chunks_added = add_documents(_DEMO_USER, docs)
        doc_info.status = "processed"
        doc_info.chunks = chunks_added
        doc_info.summary = _extract_summary(docs, file.filename)
        logger.info(f"Processed {file.filename}: {chunks_added} chunks, type={doc_info.summary.get('type')}")
    except Exception as e:
        logger.exception(f"Failed to process {file.filename}")
        doc_info.status = "failed"
        return UploadResponse(
            document=doc_info,
            message=f"Failed to process file: {e}",
        )

    _documents.setdefault(_DEMO_USER, []).append(doc_info)

    return UploadResponse(
        document=doc_info,
        message=f"Processed {file.filename} into {doc_info.chunks} searchable chunks.",
    )


@router.get("", response_model=list[DocumentInfo])
async def list_documents():
    """List all uploaded documents with summaries."""
    return _documents.get(_DEMO_USER, [])


@router.get("/summary")
async def documents_summary():
    """Aggregated financial summary across all uploaded documents."""
    user_docs = _documents.get(_DEMO_USER, [])
    processed = [d for d in user_docs if d.status == "processed" and d.summary]

    if not processed:
        return {"has_data": False, "documents": [], "message": "No documents uploaded yet. Upload a financial document to see your summary."}

    doc_summaries = []
    for d in processed:
        s = d.summary or {}
        doc_summaries.append({
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "doc_type": s.get("type", "unknown"),
            "chunks": d.chunks,
            "highlights": s.get("highlights", []),
            "numbers": s.get("numbers", {}),
            "credit_score": s.get("credit_score"),
            "banks": s.get("banks", []),
        })

    return {"has_data": True, "documents": doc_summaries}


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document."""
    user_docs = _documents.get(_DEMO_USER, [])
    _documents[_DEMO_USER] = [d for d in user_docs if d.id != doc_id]
    return {"status": "deleted", "id": doc_id}


@router.delete("")
async def clear_all_documents():
    """Clear all documents and vector store for the demo user."""
    _documents.pop(_DEMO_USER, None)
    clear_user_store(_DEMO_USER)
    return {"status": "cleared"}
