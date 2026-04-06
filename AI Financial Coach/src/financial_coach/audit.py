from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from financial_coach.config import AUDIT_DIR


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    user_id: str
    payload: Dict[str, Any]
    source: str
    run_id: str

    def to_record(self) -> Dict[str, Any]:
        return {
            "event_id": str(uuid4()),
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": self.event_type,
            "user_id": self.user_id,
            "source": self.source,
            "payload": self.payload,
        }


class AuditLogger:
    def __init__(self, path: Path | None = None):
        self.path = path or AUDIT_DIR / "audit_log.jsonl"

    def log_event(self, event: AuditEvent) -> Dict[str, Any]:
        record = event.to_record()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
        return record

    def read_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]
