import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.models.credit_report import CreditReport

router = APIRouter(prefix="/api/report", tags=["reports"])

_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_credit_score.json"


@router.get("/get", response_model=CreditReport)
async def get_sample_report() -> CreditReport:
    """Return JSON from ``app/data/sample_credit_score.json``."""
    if not _DATA_FILE.is_file():
        raise HTTPException(status_code=404, detail="sample_credit_score.json not found")
    with _DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return CreditReport(**data)
