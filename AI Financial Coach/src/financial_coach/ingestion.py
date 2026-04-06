from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List

import pandas as pd
from PyPDF2 import PdfReader

from financial_coach.config import CANONICAL_TABLES, INGESTED_DIR
from financial_coach.schemas import SCHEMAS


@dataclass
class IngestionResult:
    tables: Dict[str, pd.DataFrame]
    raw_text: str
    warnings: List[str]


AMOUNT_PATTERN = re.compile(r"(?<!\d)(?:[$€£₹]\s*)?-?\d[\d,]*(?:\.\d+)?")
PERCENT_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*%")
DATE_PATTERNS = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b"),
)

INCOME_KEYWORDS = {
    "salary": "salary",
    "payroll": "salary",
    "net pay": "salary",
    "gross pay": "salary",
    "bonus": "bonus",
    "freelance": "freelance",
    "consulting": "freelance",
    "commission": "commission",
    "interest income": "interest",
    "dividend": "investment",
}
DEBT_KEYWORDS = {
    "credit card": "credit_card",
    "card": "credit_card",
    "loan": "loan",
    "mortgage": "mortgage",
    "student": "student",
    "auto": "auto",
    "vehicle": "auto",
    "personal loan": "personal",
}
ASSET_KEYWORDS = {
    "savings": "cash",
    "checking": "cash",
    "current account": "cash",
    "bank account": "cash",
    "fixed deposit": "deposit",
    "fd ": "deposit",
    "mutual fund": "investment",
    "retirement": "retirement",
    "401k": "retirement",
    "ppf": "retirement",
    "epf": "retirement",
    "brokerage": "investment",
}
EXPENSE_CATEGORY_KEYWORDS = {
    "rent": "Housing",
    "mortgage": "Housing",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "restaurant": "Dining",
    "dining": "Dining",
    "swiggy": "Dining",
    "zomato": "Dining",
    "fuel": "Transport",
    "uber": "Transport",
    "ola": "Transport",
    "transport": "Transport",
    "electricity": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",
    "wifi": "Utilities",
    "mobile": "Utilities",
    "subscription": "Subscriptions",
    "netflix": "Subscriptions",
    "spotify": "Subscriptions",
    "insurance": "Insurance",
    "travel": "Travel",
    "flight": "Travel",
    "hotel": "Travel",
    "medical": "Healthcare",
    "pharmacy": "Healthcare",
    "shopping": "Shopping",
}


def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_csv_text(file_path: Path) -> str:
    try:
        from langchain.document_loaders.csv_loader import CSVLoader

        loader = CSVLoader(str(file_path))
        docs = loader.load()
        return "\n".join(doc.page_content for doc in docs)
    except ImportError:
        frame = pd.read_csv(file_path)
        return frame.to_csv(index=False)


def extract_source_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(file_path)
    if suffix == ".csv":
        return extract_csv_text(file_path)
    if suffix in {".xlsx", ".xls"}:
        sheets = pd.read_excel(file_path, sheet_name=None)
        return "\n".join(df.to_csv(index=False) for df in sheets.values())
    if suffix == ".json":
        return Path(file_path).read_text(encoding="utf-8")
    return Path(file_path).read_text(encoding="utf-8")


def _append_raw_table(raw_tables: Dict[str, pd.DataFrame], table_name: str, frame: pd.DataFrame) -> None:
    cleaned_frame = frame.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if cleaned_frame.empty:
        return
    if table_name in raw_tables:
        existing = raw_tables[table_name].dropna(axis=1, how="all").dropna(axis=0, how="all")
        if existing.empty:
            raw_tables[table_name] = cleaned_frame.reset_index(drop=True)
            return
        raw_tables[table_name] = pd.concat([existing, cleaned_frame], ignore_index=True)
        return
    raw_tables[table_name] = cleaned_frame.reset_index(drop=True)


def _parse_amount(value: str) -> float | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)
    if cleaned in {"", "-", ".", "-."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_amount_values(text: str) -> List[float]:
    sanitized = text
    for pattern in DATE_PATTERNS:
        sanitized = pattern.sub(" ", sanitized)
    sanitized = PERCENT_PATTERN.sub(" ", sanitized)
    amounts = [_parse_amount(match.group(0)) for match in AMOUNT_PATTERN.finditer(sanitized)]
    return [amount for amount in amounts if amount and amount > 0]


def _extract_date(value: str) -> str | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(value)
        if not match:
            continue
        parsed = pd.to_datetime(match.group(0), errors="coerce", dayfirst=False)
        if pd.isna(parsed):
            continue
        return parsed.strftime("%Y-%m-%d")
    return None


def _extract_percent(value: str) -> float | None:
    match = PERCENT_PATTERN.search(value)
    if not match:
        return None
    return float(match.group(1))


def _clean_label(value: str) -> str:
    compact = re.sub(r"\s+", " ", value).strip(" :-")
    return compact[:80] if compact else "PDF entry"


def _infer_from_keywords(text: str, mapping: Dict[str, str], default: str) -> str:
    lowered = text.lower()
    for keyword, resolved in mapping.items():
        if keyword in lowered:
            return resolved
    return default


def _extract_institution(text: str) -> str:
    before_amount = AMOUNT_PATTERN.split(text, maxsplit=1)[0]
    label = _clean_label(before_amount)
    return label if label != "PDF entry" else "PDF document"


def _build_income_rows(text: str, source_id: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in text.splitlines():
        lowered = line.lower()
        if not any(keyword in lowered for keyword in INCOME_KEYWORDS):
            continue
        amounts = _extract_amount_values(line)
        if not amounts:
            continue
        gross = max(amounts)
        net = min(amounts) if len(amounts) > 1 else gross
        rows.append(
            {
                "source_id": source_id,
                "income_type": _infer_from_keywords(line, INCOME_KEYWORDS, "income"),
                "employer": _extract_institution(line),
                "gross_monthly": gross,
                "net_monthly": net,
                "frequency": "monthly",
                "confidence": 0.55,
                "effective_date": _extract_date(line),
            }
        )
    return rows


def _build_expense_rows(text: str, source_id: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in text.splitlines():
        amounts = _extract_amount_values(line)
        if not amounts:
            continue
        lowered = line.lower()
        if any(keyword in lowered for keyword in INCOME_KEYWORDS) or any(keyword in lowered for keyword in DEBT_KEYWORDS):
            continue
        category = _infer_from_keywords(line, EXPENSE_CATEGORY_KEYWORDS, "")
        if not category:
            continue
        merchant = _extract_institution(line)
        essentiality = "essential" if category in {"Housing", "Groceries", "Utilities", "Transport", "Healthcare", "Insurance"} else "discretionary"
        rows.append(
            {
                "source_id": source_id,
                "category": category,
                "merchant": merchant,
                "amount": max(amounts),
                "frequency": "monthly",
                "essentiality": essentiality,
                "confidence": 0.5,
                "transaction_date": _extract_date(line),
            }
        )
    return rows


def _extract_due_day(text: str) -> int | None:
    match = re.search(r"(?:due\s+date|due\s+day|payment\s+due\s+on)\D{0,8}(\d{1,2})", text.lower())
    if not match:
        return None
    value = int(match.group(1))
    if 1 <= value <= 31:
        return value
    return None


def _build_debt_rows(text: str, source_id: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in text.splitlines():
        lowered = line.lower()
        if not any(keyword in lowered for keyword in DEBT_KEYWORDS):
            continue
        amounts = _extract_amount_values(line)
        if not amounts:
            continue
        balance = max(amounts)
        minimum_payment = min(amounts) if len(amounts) > 1 else None
        debt_type = _infer_from_keywords(line, DEBT_KEYWORDS, "loan")
        rows.append(
            {
                "source_id": source_id,
                "debt_name": _clean_label(AMOUNT_PATTERN.split(line, maxsplit=1)[0]),
                "debt_type": debt_type,
                "balance": balance,
                "apr": _extract_percent(line),
                "minimum_payment": minimum_payment,
                "due_day": _extract_due_day(line),
                "secured": debt_type in {"mortgage", "auto"},
                "confidence": 0.55,
            }
        )
    return rows


def _build_asset_rows(text: str, source_id: str) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for line in text.splitlines():
        lowered = line.lower()
        if not any(keyword in lowered for keyword in ASSET_KEYWORDS):
            continue
        if any(keyword in lowered for keyword in DEBT_KEYWORDS):
            continue
        amounts = _extract_amount_values(line)
        if not amounts:
            continue
        asset_type = _infer_from_keywords(line, ASSET_KEYWORDS, "asset")
        rows.append(
            {
                "source_id": source_id,
                "asset_name": _clean_label(AMOUNT_PATTERN.split(line, maxsplit=1)[0]),
                "asset_type": asset_type,
                "institution": _extract_institution(line),
                "balance": max(amounts),
                "liquidity_tier": "high" if asset_type == "cash" else "medium",
                "risk_level": "low" if asset_type in {"cash", "deposit"} else "medium",
                "valuation_date": _extract_date(line),
                "confidence": 0.55,
            }
        )
    return rows


def extract_pdf_tables(file_path: Path) -> Dict[str, pd.DataFrame]:
    text = extract_pdf_text(file_path)
    source_id = file_path.stem.lower()
    extracted = {
        "income": pd.DataFrame(_build_income_rows(text, source_id)),
        "expenses": pd.DataFrame(_build_expense_rows(text, source_id)),
        "debts": pd.DataFrame(_build_debt_rows(text, source_id)),
        "assets": pd.DataFrame(_build_asset_rows(text, source_id)),
    }
    return extracted


def _coerce_numeric(frame: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for column in columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    return frame


def normalize_tables(raw_frames: Dict[str, pd.DataFrame], user_id: str, source_id: str) -> Dict[str, pd.DataFrame]:
    normalized: Dict[str, pd.DataFrame] = {}
    for table_name in CANONICAL_TABLES:
        schema = SCHEMAS[table_name]
        frame = raw_frames.get(table_name, pd.DataFrame(columns=schema.columns)).copy()
        for column in schema.columns:
            if column not in frame.columns:
                frame[column] = None
        frame["user_id"] = user_id
        frame["scope"] = frame["scope"].fillna("private")
        frame["source_id"] = source_id
        frame["confidence"] = pd.to_numeric(frame["confidence"], errors="coerce").fillna(0.9)
        frame = frame[schema.columns]
        normalized[table_name] = frame

    normalized["income"] = _coerce_numeric(normalized["income"], ["gross_monthly", "net_monthly", "confidence"])
    normalized["expenses"] = _coerce_numeric(normalized["expenses"], ["amount", "confidence"])
    normalized["debts"] = _coerce_numeric(normalized["debts"], ["balance", "apr", "minimum_payment", "confidence"])
    normalized["assets"] = _coerce_numeric(normalized["assets"], ["balance", "confidence"])
    return normalized


def ingest_structured_files(file_paths: List[Path], user_id: str) -> IngestionResult:
    raw_tables: Dict[str, pd.DataFrame] = {}
    warnings: List[str] = []
    raw_text_parts: List[str] = []

    for file_path in file_paths:
        raw_text_parts.append(extract_source_text(file_path))
        suffix = file_path.suffix.lower()
        try:
            if suffix == ".csv":
                frame = pd.read_csv(file_path)
                table_name = file_path.stem.lower()
                _append_raw_table(raw_tables, table_name, frame)
            elif suffix in {".xlsx", ".xls"}:
                workbook = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, frame in workbook.items():
                    _append_raw_table(raw_tables, sheet_name.lower(), frame)
            elif suffix == ".pdf":
                pdf_tables = extract_pdf_tables(file_path)
                for table_name, frame in pdf_tables.items():
                    _append_raw_table(raw_tables, table_name, frame)
        except Exception as exc:  # pragma: no cover - defensive parsing
            warnings.append(f"{file_path.name}: {exc}")

    source_id = "-".join(path.stem for path in file_paths) or "manual-upload"
    tables = normalize_tables(raw_tables, user_id=user_id, source_id=source_id)

    for table_name, frame in tables.items():
        output_path = INGESTED_DIR / f"{user_id}_{table_name}.csv"
        frame.to_csv(output_path, index=False)

    return IngestionResult(
        tables=tables,
        raw_text="\n".join(raw_text_parts),
        warnings=warnings,
    )
