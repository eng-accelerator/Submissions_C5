"""Document upload models."""

from typing import Any

from pydantic import BaseModel


class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str  # uploaded, processing, processed, failed
    chunks: int = 0
    summary: dict[str, Any] | None = None


class UploadResponse(BaseModel):
    document: DocumentInfo
    message: str
