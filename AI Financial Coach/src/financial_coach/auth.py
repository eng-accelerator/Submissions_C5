from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import pandas as pd


@dataclass(frozen=True)
class FgaDecision:
    user_id: str
    resource: str
    action: str
    allowed: bool
    reason: str


class OzeroFgaClient:
    """
    Lightweight Ozero FGA adapter for the MVP.

    The contract mirrors a fine-grained authorization service so the app can
    swap this class for the real Ozero SDK without changing agent logic.
    """

    def __init__(self, policy_store: Dict[str, Dict[str, Iterable[str]]]):
        self.policy_store = policy_store

    def check(self, user_id: str, resource: str, action: str) -> FgaDecision:
        allowed_resources = self.policy_store.get(user_id, {})
        resource_actions = set(allowed_resources.get(resource, []))
        wildcard_actions = set(allowed_resources.get("*", []))
        allowed = action in resource_actions or action in wildcard_actions
        reason = "authorized by policy" if allowed else "resource/action denied"
        return FgaDecision(
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed,
            reason=reason,
        )

    def authorize_table(
        self, user_id: str, table_name: str, frame: pd.DataFrame, action: str
    ) -> pd.DataFrame:
        decision = self.check(user_id, f"table:{table_name}", action)
        if not decision.allowed:
            return pd.DataFrame(columns=frame.columns)
        if frame.empty:
            return frame.copy()
        return frame.loc[frame["user_id"] == user_id].copy()

    def authorize_rows(
        self, user_id: str, table_name: str, frame: pd.DataFrame, action: str
    ) -> pd.DataFrame:
        resource = f"row:{table_name}:{user_id}"
        decision = self.check(user_id, resource, action)
        if not decision.allowed:
            return pd.DataFrame(columns=frame.columns)
        if frame.empty:
            return frame.copy()
        return frame.loc[frame["user_id"] == user_id].copy()


def build_demo_policy_store(user_id: str) -> Dict[str, Dict[str, List[str]]]:
    permissions = {
        "table:income": ["read", "calculate", "explain"],
        "table:expenses": ["read", "calculate", "explain"],
        "table:debts": ["read", "calculate", "explain"],
        "table:assets": ["read", "calculate", "explain"],
        f"row:income:{user_id}": ["read", "calculate", "explain"],
        f"row:expenses:{user_id}": ["read", "calculate", "explain"],
        f"row:debts:{user_id}": ["read", "calculate", "explain"],
        f"row:assets:{user_id}": ["read", "calculate", "explain"],
    }
    return {user_id: permissions}
