from __future__ import annotations

from ai_app.agents.base import AgentBase
from ai_app.agents.contradiction_checker_agent import ContradictionCheckerAgent
from ai_app.agents.source_verifier_agent import SourceVerifierAgent
from ai_app.domain.enums import ConfidenceLabel
from ai_app.schemas.research import Claim, Contradiction, ResearchSession


def _apply_contradiction_metadata(claims: list[Claim], contradictions: list[Contradiction]) -> None:
    by_id = {c.id: c for c in claims}
    for ctr in contradictions:
        left = by_id.get(ctr.claim_a_id)
        right = by_id.get(ctr.claim_b_id)
        if not left or not right:
            continue
        for sid in right.supporting_source_ids:
            if sid and sid not in left.contradicting_source_ids:
                left.contradicting_source_ids.append(sid)
        for sid in left.supporting_source_ids:
            if sid and sid not in right.contradicting_source_ids:
                right.contradicting_source_ids.append(sid)
    for claim in claims:
        involved = sum(1 for ctr in contradictions if ctr.claim_a_id == claim.id or ctr.claim_b_id == claim.id)
        if involved:
            claim.contested = True
            claim.consensus_pct = max(18, 100 - involved * 28 - (12 if claim.weak_evidence else 0))
            claim.trust_score = max(0, claim.trust_score - min(22, involved * 8 + (4 if claim.weak_evidence else 0)))
        elif claim.contested:
            claim.consensus_pct = min(claim.consensus_pct, 58)
        if claim.weak_evidence and claim.consensus_pct > 78:
            claim.consensus_pct = min(claim.consensus_pct, 76)


class CriticalAnalysisAgent(AgentBase):
    name = "critical_analysis_agent"

    def __init__(self, source_verifier: SourceVerifierAgent, contradiction_checker: ContradictionCheckerAgent) -> None:
        self.source_verifier = source_verifier
        self.contradiction_checker = contradiction_checker

    async def run(self, session: ResearchSession) -> ResearchSession:
        await self.source_verifier.run(session)
        source_map = {source.id: source for source in session.sources}
        claims: list[Claim] = []
        for finding in session.findings:
            supports = list(finding.source_ids)
            support_sources = [source_map[source_id] for source_id in supports if source_id in source_map]
            avg_credibility = sum(source.credibility_score for source in support_sources) / max(1, len(support_sources))
            evidence_density = min(1.0, len(supports) / 3)
            confidence_pct = min(97, int(40 + (avg_credibility * 35) + (evidence_density * 22)))
            confidence = ConfidenceLabel.HIGH if confidence_pct >= 80 else ConfidenceLabel.MEDIUM if confidence_pct >= 60 else ConfidenceLabel.LOW
            contested = any(token in finding.content.lower() for token in ("controvers", "unclear", "debate", "mixed evidence", "contradict"))
            weak_evidence = len(supports) < 1 or avg_credibility < 0.58
            citation_parts: list[str] = []
            for source in support_sources[:3]:
                page_suffix = f" p.{','.join(str(page) for page in source.page_refs)}" if source.page_refs else ""
                citation_parts.append(f"{source.filename or source.title}{page_suffix}")
            citation_summary = ", ".join(citation_parts) or "Limited explicit source support"
            claims.append(
                Claim(
                    statement=finding.content.split(".")[0].strip() or finding.content[:120],
                    supporting_source_ids=supports,
                    confidence=confidence,
                    confidence_pct=confidence_pct,
                    reasoning="This claim is derived from retrieved evidence, then weighted by source credibility, date-fit, and corroboration.",
                    credibility_summary=f"Average source credibility {avg_credibility:.2f}; trusted because the cited sources were scored on provider quality, metadata completeness, date-window fit, and corroboration.",
                    evidence_summary=f"Primary evidence comes from {citation_summary}. Supporting snippet: {finding.quote_excerpt or finding.snippet or finding.content[:180]}",
                    contested=contested,
                    weak_evidence=weak_evidence,
                    consensus_pct=100,
                    trust_score=min(100, confidence_pct + (3 if avg_credibility > 0.75 else 0) - (5 if contested else 0)),
                )
            )
        session.claims.extend(claims)
        session.contradictions.extend(await self.contradiction_checker.run(claims, session.sources))
        _apply_contradiction_metadata(session.claims, session.contradictions)
        return session
