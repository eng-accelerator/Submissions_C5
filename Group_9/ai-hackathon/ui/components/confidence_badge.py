from __future__ import annotations


def render_confidence_summary(claims: list[dict]) -> str:
    if not claims:
        return "No claims yet."
    high = sum(1 for claim in claims if claim["confidence"] == "high")
    medium = sum(1 for claim in claims if claim["confidence"] == "medium")
    low = sum(1 for claim in claims if claim["confidence"] == "low")
    avg_trust = int(sum(claim["trust_score"] for claim in claims) / max(1, len(claims)))
    avg_confidence = int(sum(claim["confidence_pct"] for claim in claims) / max(1, len(claims)))
    avg_consensus = int(sum(claim.get("consensus_pct", 100) for claim in claims) / max(1, len(claims)))
    contested_n = sum(1 for claim in claims if claim.get("contested"))
    return (
        f"High confidence claims: {high}\n"
        f"Medium confidence claims: {medium}\n"
        f"Low confidence claims: {low}\n"
        f"Average confidence: {avg_confidence}%\n"
        f"Average trust score: {avg_trust}%\n"
        f"Average source consensus: {avg_consensus}%\n"
        f"Claims flagged contested: {contested_n}"
    )
