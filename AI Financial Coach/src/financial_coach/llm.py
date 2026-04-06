from __future__ import annotations

import json
import os
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from financial_coach.config import load_env_file


class HuggingFaceReasoner:
    """
    Demo-friendly reasoning facade.

    Replace `generate_explanation` internals with a Hugging Face Inference Endpoint
    call or self-hosted text-generation pipeline.
    """

    model_name = "mistralai/Mistral-7B-Instruct-v0.3"

    def generate_explanation(self, payload: Dict[str, object]) -> str:
        action_items = payload.get("action_items", [])
        context = payload.get("context", {})
        market = payload.get("market_context", {})
        lines: List[str] = [
            "Personalized financial coaching summary",
            f"Disposable income: {context.get('cash_flow', {}).get('disposable_income', 0)} per month.",
            f"Emergency fund target: {context.get('emergency_fund_target', 0)}.",
            f"10Y treasury context: {market.get('treasury_10y')}.",
            "Recommended actions:",
        ]
        for idx, item in enumerate(action_items, start=1):
            lines.append(f"{idx}. {item}")
        lines.append("Structured payload:")
        lines.append(json.dumps(payload, indent=2, default=str))
        return "\n".join(lines)


class OpenRouterReasoner:
    model_name = "meta-llama/llama-3.1-8b-instruct"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self) -> None:
        load_env_file()
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def generate_explanation(self, payload: Dict[str, object]) -> str:
        message = (
            "You are a careful financial coach. Use the provided structured results only. "
            "Do not perform fresh math. Provide a concise, safe, personalized explanation.\n\n"
            f"Structured payload:\n{json.dumps(payload, indent=2, default=str)}"
        )
        body = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "You produce guarded financial coaching explanations from deterministic inputs.",
                },
                {"role": "user", "content": message},
            ],
            "temperature": 0.2,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AI Financial Coach Agent",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
        except (HTTPError, URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"OpenRouter request failed: {exc}") from exc


class HybridReasoner:
    def __init__(self) -> None:
        self.openrouter = OpenRouterReasoner()
        self.fallback = HuggingFaceReasoner()

    def generate_explanation(self, payload: Dict[str, object]) -> str:
        if self.openrouter.is_configured():
            try:
                return self.openrouter.generate_explanation(payload)
            except RuntimeError:
                return self.fallback.generate_explanation(payload)
        return self.fallback.generate_explanation(payload)
