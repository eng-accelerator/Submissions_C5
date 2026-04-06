from __future__ import annotations

import os
from typing import Dict, List

from financial_coach.config import load_env_file


def langsmith_enabled() -> bool:
    load_env_file()
    api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
    tracing = os.getenv("LANGSMITH_TRACING", "false").strip().lower()
    return bool(api_key) and tracing in {"1", "true", "yes", "on"}


def langsmith_project() -> str:
    load_env_file()
    return os.getenv("LANGSMITH_PROJECT", "ai-financial-coach-agent").strip() or "ai-financial-coach-agent"


def build_langgraph_config(
    run_name: str,
    tags: List[str] | None = None,
    metadata: Dict[str, object] | None = None,
) -> Dict[str, object]:
    config: Dict[str, object] = {
        "run_name": run_name,
        "tags": tags or [],
        "metadata": metadata or {},
    }
    if langsmith_enabled():
        config["metadata"] = {
            **(metadata or {}),
            "langsmith_project": langsmith_project(),
            "langsmith_tracing": True,
        }
    return config
