from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class NotificationDispatcher:
    def __init__(self) -> None:
        self.webhook_url = os.getenv("N8N_NOTIFICATION_WEBHOOK", "").strip()

    def dispatch(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.webhook_url:
            return {
                "delivered": False,
                "channel": "webhook",
                "reason": "N8N_NOTIFICATION_WEBHOOK not configured",
            }
        request = Request(
            self.webhook_url,
            data=json.dumps({"event_type": event_type, "payload": payload}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=15) as response:
                body = response.read().decode("utf-8")
            return {"delivered": True, "channel": "webhook", "response": body}
        except (HTTPError, URLError) as exc:
            return {"delivered": False, "channel": "webhook", "reason": str(exc)}
