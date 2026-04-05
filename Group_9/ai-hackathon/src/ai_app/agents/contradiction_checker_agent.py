from __future__ import annotations

import re
from difflib import SequenceMatcher

from ai_app.agents.base import AgentBase
from ai_app.schemas.research import Claim, Contradiction, Source

_OPPOSITE_PAIRS: tuple[tuple[str, str], ...] = (
    ("increase", "decrease"),
    ("increases", "decreases"),
    ("rise", "fall"),
    ("rising", "falling"),
    ("higher", "lower"),
    ("more", "less"),
    ("benefit", "harm"),
    ("benefits", "harms"),
    ("safe", "unsafe"),
    ("effective", "ineffective"),
    ("works", "fails"),
    ("confirm", "refute"),
    ("true", "false"),
    ("yes", "no"),
    ("supports", "opposes"),
    ("causes", "prevents"),
    ("improve", "worsen"),
    ("positive", "negative"),
    ("gain", "loss"),
    ("success", "failure"),
)

_NEG_MARKERS: tuple[str, ...] = (
    " not ",
    "n't ",
    "no evidence",
    "does not",
    "doesn't",
    "failed to",
    "contrary to",
    "dispute",
    "conflicting",
    "refutes",
    "contradicts",
    "cannot conclude",
)

_UNCERTAIN: tuple[str, ...] = (
    "unclear",
    "debate",
    "controvers",
    "mixed evidence",
    "may ",
    "might ",
    "uncertain",
    "inconclusive",
)


def _truncate(text: str, max_len: int = 160) -> str:
    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9]{3,}", text.lower())}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _polarity_conflict(a: str, b: str) -> bool:
    al, bl = a.lower(), b.lower()
    for x, y in _OPPOSITE_PAIRS:
        if (x in al and y in bl) or (y in al and x in bl):
            return True
    return False


def _negation_tension(a: str, b: str, overlap: float) -> bool:
    if overlap < 0.16:
        return False
    al, bl = a.lower(), b.lower()
    return any(m in al for m in _NEG_MARKERS) or any(m in bl for m in _NEG_MARKERS)


def _uncertainty_tension(a: str, b: str, overlap: float) -> bool:
    if overlap < 0.2:
        return False
    al, bl = a.lower(), b.lower()
    if not (any(u in al for u in _UNCERTAIN) or any(u in bl for u in _UNCERTAIN)):
        return False
    return SequenceMatcher(None, al, bl).ratio() < 0.84


def _claims_conflict(left: Claim, right: Claim) -> bool:
    a, b = left.statement, right.statement
    if not a.strip() or not b.strip():
        return False
    if a.strip().lower() == b.strip().lower():
        return False
    ta, tb = _tokens(a), _tokens(b)
    overlap = _jaccard(ta, tb)
    if overlap < 0.11:
        return False
    if _polarity_conflict(a, b):
        return True
    if _negation_tension(a, b, overlap):
        return True
    if _uncertainty_tension(a, b, overlap):
        return True
    if overlap > 0.32 and SequenceMatcher(None, a.lower(), b.lower()).ratio() < 0.52:
        return True
    return False


def _source_label(source: Source | None) -> str:
    if not source:
        return "Unknown source"
    base = source.filename or source.title or source.url or source.id
    prov = f" ({source.provider})" if source.provider else ""
    return f"{base}{prov}"


def _primary_source_id(claim: Claim) -> str:
    return claim.supporting_source_ids[0] if claim.supporting_source_ids else ""


class ContradictionCheckerAgent(AgentBase):
    name = "contradiction_checker_agent"

    async def run(self, claims: list[Claim], sources: list[Source]) -> list[Contradiction]:
        source_map = {s.id: s for s in sources}
        seen_pairs: set[frozenset[str]] = set()
        out: list[Contradiction] = []
        for i, left in enumerate(claims):
            for right in claims[i + 1 :]:
                if not _claims_conflict(left, right):
                    continue
                key = frozenset({left.id, right.id})
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                sid_a = _primary_source_id(left)
                sid_b = _primary_source_id(right)
                src_a = source_map.get(sid_a)
                src_b = source_map.get(sid_b)
                ca = src_a.credibility_score if src_a else 0.0
                cb = src_b.credibility_score if src_b else 0.0
                label_a = _source_label(src_a)
                label_b = _source_label(src_b)
                if ca > cb + 0.06:
                    side = "a"
                    reasoning = (
                        f"The pipeline weights **{label_a}** more strongly (credibility {ca:.2f}) than **{label_b}** ({cb:.2f}) "
                        "based on source type, provider trust, metadata, date-window fit, and corroboration—not on which answer you prefer."
                    )
                    if src_a and src_a.credibility_explanation:
                        reasoning += f" Detail (A): {src_a.credibility_explanation}"
                    if src_b and src_b.credibility_explanation:
                        reasoning += f" Detail (B): {src_b.credibility_explanation}"
                elif cb > ca + 0.06:
                    side = "b"
                    reasoning = (
                        f"The pipeline weights **{label_b}** more strongly (credibility {cb:.2f}) than **{label_a}** ({ca:.2f}) "
                        "using the same scoring rules."
                    )
                    if src_b and src_b.credibility_explanation:
                        reasoning += f" Detail (B): {src_b.credibility_explanation}"
                    if src_a and src_a.credibility_explanation:
                        reasoning += f" Detail (A): {src_a.credibility_explanation}"
                else:
                    side = "tie"
                    reasoning = (
                        f"**{label_a}** and **{label_b}** are too close on credibility ({ca:.2f} vs {cb:.2f}) to pick a winner. "
                        "Seek additional independent sources before treating either position as settled."
                    )
                text_sim = SequenceMatcher(None, left.statement.lower(), right.statement.lower()).ratio()
                consensus_score = round(max(0.0, min(1.0, text_sim)), 3)
                analysis = (
                    f"Two retrieved lines of evidence point in different directions on a related point. "
                    f"Compare **{label_a}** and **{label_b}** directly rather than averaging them mentally."
                )
                out.append(
                    Contradiction(
                        claim_a_id=left.id,
                        claim_b_id=right.id,
                        claim_a=left.statement,
                        source_a_id=sid_a,
                        claim_b=right.statement,
                        source_b_id=sid_b,
                        source_a_label=label_a,
                        source_b_label=label_b,
                        position_a=_truncate(left.statement),
                        position_b=_truncate(right.statement),
                        analysis=analysis,
                        resolution=None,
                        more_credible_side=side,
                        credibility_reasoning=reasoning.strip(),
                        consensus_score=consensus_score,
                    )
                )
                if len(out) >= 24:
                    return out
        return out
