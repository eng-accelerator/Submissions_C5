from __future__ import annotations

from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
UPLOAD_DIR = DATA_DIR / "uploads"
INGESTED_DIR = DATA_DIR / "ingested"
EXPORT_DIR = DATA_DIR / "exports"
AUDIT_DIR = DATA_DIR / "audit"
WORKFLOW_DIR = ROOT_DIR / "workflows"
N8N_DIR = ROOT_DIR / "n8n"

CANONICAL_TABLES = ("income", "expenses", "debts", "assets")


for directory in (DATA_DIR, SAMPLE_DIR, UPLOAD_DIR, INGESTED_DIR, EXPORT_DIR, AUDIT_DIR, WORKFLOW_DIR, N8N_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def load_env_file() -> None:
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        cleaned = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), cleaned)
