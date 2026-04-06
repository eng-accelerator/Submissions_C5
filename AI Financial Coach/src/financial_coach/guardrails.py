from __future__ import annotations

from typing import Dict, List


class LlamaGuardModerator:
    """
    Lightweight moderation facade representing Llama Guard.
    """

    HIGH_RISK_TERMS = {
        "guaranteed return",
        "insider tip",
        "hide assets",
        "evade taxes",
        "wire money to",
    }

    def moderate(self, prompt: str, output: str) -> Dict[str, object]:
        violations: List[str] = []
        combined = f"{prompt} {output}".lower()
        for term in self.HIGH_RISK_TERMS:
            if term in combined:
                violations.append(term)
        return {
            "approved": not violations,
            "violations": violations,
            "policy": "financial-coaching-safe-advice-v1",
        }
