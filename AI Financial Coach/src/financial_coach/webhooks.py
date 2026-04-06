from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from financial_coach.audit import AuditEvent, AuditLogger
from financial_coach.config import ROOT_DIR, SAMPLE_DIR, UPLOAD_DIR, load_env_file
from financial_coach.service import FinancialCoachService


load_env_file()


def _json_response(status: str, data: Dict[str, Any], code: int = 200):
    payload = json.dumps({"status": status, "data": data}, default=str).encode("utf-8")
    return code, payload


def _safe_file_paths(raw_paths: List[str]) -> List[Path]:
    allowed_roots = [ROOT_DIR, SAMPLE_DIR, UPLOAD_DIR]
    resolved: List[Path] = []
    for raw in raw_paths:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = ROOT_DIR / candidate
        candidate = candidate.resolve()
        if not any(root.resolve() in candidate.parents or candidate == root.resolve() for root in allowed_roots):
            raise ValueError(f"Path is outside allowed roots: {candidate}")
        if not candidate.exists():
            raise FileNotFoundError(f"File not found: {candidate}")
        resolved.append(candidate)
    return resolved


def _read_json_body(environ: Dict[str, Any]) -> Dict[str, Any]:
    content_length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(content_length) if content_length else b"{}"
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "")

    try:
        if method == "GET" and path == "/health":
            code, payload = _json_response(
                "ok",
                {"service": "financial-coach-webhooks", "audit_events": len(AuditLogger().read_recent(5))},
            )
        elif method == "GET" and path == "/webhooks/n8n/audit":
            params = parse_qs(environ.get("QUERY_STRING", ""))
            limit = int(params.get("limit", ["25"])[0])
            code, payload = _json_response("ok", {"events": AuditLogger().read_recent(limit)})
        elif method == "POST" and path == "/webhooks/n8n/ingest":
            body = _read_json_body(environ)
            user_id = str(body.get("user_id", "demo-user-001")).strip() or "demo-user-001"
            files = _safe_file_paths(list(body.get("files", [])))
            service = FinancialCoachService(user_id=user_id)
            tables = service.load_tables(files)
            AuditLogger().log_event(
                event=AuditEvent(
                    event_type="ingestion_completed",
                    user_id=user_id,
                    source="n8n-webhook",
                    run_id=str(body.get("run_id", "manual-ingest")),
                    payload={
                        "files": [str(path) for path in files],
                        "table_counts": {name: len(frame) for name, frame in tables.items()},
                    },
                )
            )
            code, payload = _json_response(
                "ok",
                {
                    "user_id": user_id,
                    "files": [str(path) for path in files],
                    "table_counts": {name: len(frame) for name, frame in tables.items()},
                },
            )
        elif method == "POST" and path == "/webhooks/n8n/analyze":
            body = _read_json_body(environ)
            user_id = str(body.get("user_id", "demo-user-001")).strip() or "demo-user-001"
            query = str(body.get("query", "Create a safe financial coaching plan."))
            files = _safe_file_paths(list(body.get("files", []))) if body.get("files") else []
            send_notifications = _as_bool(body.get("send_notifications", False))
            service = FinancialCoachService(user_id=user_id)
            result = service.run(
                query=query,
                uploaded_paths=files,
                source="n8n-webhook",
                send_notifications=send_notifications,
            )
            code, payload = _json_response(
                "ok",
                {
                    "user_id": user_id,
                    "run_id": result.get("run_id"),
                    "action_plan": result.get("action_plan", {}),
                    "moderation": result.get("moderation", {}),
                    "notification_status": result.get("notification_status"),
                },
            )
        else:
            code, payload = _json_response("error", {"message": "Not found"}, code=404)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        code, payload = _json_response("error", {"message": str(exc)}, code=400)
    except Exception as exc:  # pragma: no cover - defensive web boundary
        code, payload = _json_response("error", {"message": str(exc)}, code=500)

    status_line = f"{code} {'OK' if code < 400 else 'ERROR'}"
    headers = [("Content-Type", "application/json"), ("Content-Length", str(len(payload)))]
    start_response(status_line, headers)
    return [payload]


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    with make_server(host, port, application) as server:
        print(f"Webhook server listening on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    run_server()
